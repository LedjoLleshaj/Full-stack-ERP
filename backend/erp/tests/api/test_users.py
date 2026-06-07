import pytest
from django.contrib.auth.hashers import identify_hasher
from erp.models import User


@pytest.mark.django_db
class TestCreateUser:
    def test_create_user_hashes_password(self, authenticated_api_client):
        resp = authenticated_api_client.post("/erp/create-user", {
            "username": "alice",
            "password": "s3cret-pass",
            "email": "alice@example.com",
            "firstname": "Alice",
            "lastname": "A",
            "role": "STAFF",
        }, format="json")
        assert resp.status_code == 201
        u = User.objects.get(username="alice")
        assert u.password != "s3cret-pass"
        identify_hasher(u.password)
        assert "password" not in resp.json()

    def test_create_user_missing_fields(self, authenticated_api_client):
        resp = authenticated_api_client.post("/erp/create-user", {
            "username": "bob",
        }, format="json")
        assert resp.status_code == 400

    def test_duplicate_username_rejected(self, authenticated_api_client, existing_user):
        resp = authenticated_api_client.post("/erp/create-user", {
            "username": existing_user.username,
            "password": "x",
            "email": "dupe@example.com",
            "firstname": "D",
            "lastname": "U",
            "role": "STAFF",
        }, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestUpdateUser:
    def test_update_user_hashes_password(self, authenticated_api_client, existing_user):
        resp = authenticated_api_client.put(
            f"/erp/update-user/{existing_user.id}",
            {
                "username": existing_user.username,
                "password": "new-password",
                "email": existing_user.email,
                "firstname": "X",
                "lastname": "Y",
                "role": "STAFF",
            },
            format="json",
        )
        assert resp.status_code == 200
        existing_user.refresh_from_db()
        assert existing_user.password != "new-password"
        identify_hasher(existing_user.password)

    def test_update_user_without_password(self, authenticated_api_client, existing_user):
        old_password = existing_user.password
        resp = authenticated_api_client.put(
            f"/erp/update-user/{existing_user.id}",
            {
                "firstname": "NewFirst",
                "lastname": "NewLast",
            },
            format="json",
        )
        assert resp.status_code == 200
        existing_user.refresh_from_db()
        assert existing_user.firstname == "NewFirst"
        assert existing_user.password == old_password

    def test_update_nonexistent_user(self, authenticated_api_client):
        resp = authenticated_api_client.put("/erp/update-user/99999", {}, format="json")
        assert resp.status_code == 404


@pytest.mark.django_db
class TestGetUsers:
    def test_list_users_requires_auth(self, api_client):
        resp = api_client.get("/erp/users")
        assert resp.status_code == 401

    def test_list_users(self, authenticated_api_client, existing_user):
        resp = authenticated_api_client.get("/erp/users")
        assert resp.status_code == 200
        assert any(u["username"] == existing_user.username for u in resp.json())
        for u in resp.json():
            assert "password" not in u
