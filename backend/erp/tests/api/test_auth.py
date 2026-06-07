import pytest

from erp.models import User


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client):
        User.objects.create_user(
            username="testuser", password="testpass123",
            firstname="Test", lastname="User",
        )
        resp = api_client.post("/erp/login", {
            "username": "testuser",
            "password": "testpass123",
        }, format="json")
        assert resp.status_code == 200
        assert "access_token" in resp.cookies
        assert "refresh_token" in resp.cookies
        data = resp.json()
        assert data["username"] == "testuser"
        assert "password" not in data

    def test_login_invalid_password(self, api_client):
        User.objects.create_user(
            username="testuser", password="testpass123",
            firstname="Test", lastname="User",
        )
        resp = api_client.post("/erp/login", {
            "username": "testuser",
            "password": "wrongpassword",
        }, format="json")
        assert resp.status_code == 401

    def test_login_missing_fields(self, api_client):
        resp = api_client.post("/erp/login", {"username": "x"}, format="json")
        assert resp.status_code == 400

    def test_login_nonexistent_user(self, api_client):
        resp = api_client.post("/erp/login", {
            "username": "ghost",
            "password": "pass",
        }, format="json")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestLogout:
    def test_logout_clears_cookies(self, api_client):
        User.objects.create_user(
            username="testuser", password="testpass123",
            firstname="Test", lastname="User",
        )
        api_client.post("/erp/login", {
            "username": "testuser",
            "password": "testpass123",
        }, format="json")
        resp = api_client.post("/erp/logout")
        assert resp.status_code == 200
