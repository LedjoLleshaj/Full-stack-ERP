import pytest
from rest_framework.test import APIClient

from erp.constants import UserRole
from erp.models import User


def make_user(role, suffix=""):
    return User.objects.create_user(
        username=f"{role.lower()}{suffix}",
        password="pass",
        firstname="Test",
        lastname="User",
        role=role,
    )


def client_for(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db
class TestLoginReturnsRole:
    def test_role_in_login_response(self, api_client):
        User.objects.create_user(
            username="roletest", password="pass123",
            firstname="T", lastname="U", role=UserRole.MANAGER,
        )
        resp = api_client.post("/erp/login", {"username": "roletest", "password": "pass123"}, format="json")
        assert resp.status_code == 200
        assert resp.json()["role"] == UserRole.MANAGER


@pytest.mark.django_db
class TestPermissionClasses:
    def test_viewer_cannot_create_supplier(self):
        viewer = make_user(UserRole.VIEWER, "1")
        resp = client_for(viewer).post("/erp/add-supplier", {
            "firstname": "A", "lastname": "B", "address": "X"
        }, format="json")
        assert resp.status_code == 403

    def test_staff_can_create_supplier(self):
        staff = make_user(UserRole.STAFF, "1")
        resp = client_for(staff).post("/erp/add-supplier", {
            "firstname": "A", "lastname": "B", "address": "X"
        }, format="json")
        assert resp.status_code in (200, 201)

    def test_manager_can_create_supplier(self):
        mgr = make_user(UserRole.MANAGER, "1")
        resp = client_for(mgr).post("/erp/add-supplier", {
            "firstname": "A", "lastname": "B", "address": "X"
        }, format="json")
        assert resp.status_code in (200, 201)

    def test_staff_cannot_delete_supplier(self):
        from erp.models import Supplier
        supplier = Supplier.objects.create(firstname="X", lastname="Y", address="Z")
        staff = make_user(UserRole.STAFF, "2")
        resp = client_for(staff).delete(f"/erp/delete-supplier/{supplier.id}")
        assert resp.status_code == 403

    def test_manager_can_delete_supplier(self):
        from erp.models import Supplier
        supplier = Supplier.objects.create(firstname="X", lastname="Y", address="Z")
        mgr = make_user(UserRole.MANAGER, "2")
        resp = client_for(mgr).delete(f"/erp/delete-supplier/{supplier.id}")
        assert resp.status_code == 200

    def test_viewer_can_read_suppliers(self):
        viewer = make_user(UserRole.VIEWER, "2")
        resp = client_for(viewer).get("/erp/suppliers")
        assert resp.status_code == 200

    def test_unauthenticated_cannot_read(self):
        resp = APIClient().get("/erp/suppliers")
        assert resp.status_code == 401

    def test_admin_can_delete(self):
        from erp.models import Supplier
        supplier = Supplier.objects.create(firstname="A", lastname="B", address="C")
        admin = make_user(UserRole.ADMIN, "1")
        resp = client_for(admin).delete(f"/erp/delete-supplier/{supplier.id}")
        assert resp.status_code == 200

    def test_viewer_cannot_delete_client(self):
        from erp.models import Client
        c = Client.objects.create(firstname="A", lastname="B", phone="1", address="X", city="Y")
        viewer = make_user(UserRole.VIEWER, "3")
        resp = client_for(viewer).delete(f"/erp/delete-client/{c.id}")
        assert resp.status_code == 403

    def test_viewer_cannot_create_user(self):
        viewer = make_user(UserRole.VIEWER, "4")
        resp = client_for(viewer).post("/erp/create-user", {
            "username": "newu", "password": "p", "firstname": "N", "lastname": "U"
        }, format="json")
        assert resp.status_code == 403

    def test_staff_cannot_create_user(self):
        staff = make_user(UserRole.STAFF, "3")
        resp = client_for(staff).post("/erp/create-user", {
            "username": "newu2", "password": "p", "firstname": "N", "lastname": "U"
        }, format="json")
        assert resp.status_code == 403

    def test_manager_can_create_user(self):
        mgr = make_user(UserRole.MANAGER, "3")
        resp = client_for(mgr).post("/erp/create-user", {
            "username": "newu3", "password": "pass123", "firstname": "N", "lastname": "U"
        }, format="json")
        assert resp.status_code == 201
