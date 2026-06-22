from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from erp.constants import AccountType, Currency, ExpenseFrequency
from erp.models import Account, RecurringExpense, User
from erp.serializers import RecurringExpenseSerializer


@pytest.mark.django_db
def test_serializer_rejects_when_no_matching_account():
    serializer = RecurringExpenseSerializer(data={
        "name": "Rent",
        "amount": "500.00",
        "currency": Currency.EUR,
        "account_type": AccountType.BANK,
        "frequency": ExpenseFrequency.MONTHLY,
        "start_date": "2026-01-01",
    })
    assert not serializer.is_valid()
    assert "account_type" in serializer.errors


@pytest.mark.django_db
def test_serializer_valid_with_matching_account():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("0.00"),
    )
    serializer = RecurringExpenseSerializer(data={
        "name": "Rent",
        "amount": "500.00",
        "currency": Currency.EUR,
        "account_type": AccountType.BANK,
        "frequency": ExpenseFrequency.MONTHLY,
        "start_date": "2026-01-01",
    })
    assert serializer.is_valid(), serializer.errors
    exp = serializer.save()
    assert exp.next_due_date == date(2026, 1, 1)


def _account_eur():
    return Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("5000.00"),
    )


def _client_with_role(role):
    user = User.objects.create_user(
        username=f"u_{role}", password="x", firstname="F", lastname="L", role=role,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _due_expense():
    return RecurringExpense.objects.create(
        name="Rent", amount=Decimal("500.00"), currency=Currency.EUR,
        account_type=AccountType.BANK, frequency=ExpenseFrequency.MONTHLY,
        start_date=date(2020, 1, 1),
    )


@pytest.mark.django_db
def test_list_recurring_expenses(authenticated_api_client):
    _account_eur()
    _due_expense()
    res = authenticated_api_client.get("/api/v1/recurring-expenses/")
    assert res.status_code == 200
    assert res.data["count"] == 1


@pytest.mark.django_db
def test_charge_action_moves_money(authenticated_api_client):
    account = _account_eur()
    exp = _due_expense()
    res = authenticated_api_client.post(
        f"/api/v1/recurring-expenses/{exp.id}/charge/"
    )
    assert res.status_code == 201
    account.refresh_from_db()
    assert account.current_balance == Decimal("4500.00")


@pytest.mark.django_db
def test_run_due_action(authenticated_api_client):
    _account_eur()
    _due_expense()
    res = authenticated_api_client.post("/api/v1/recurring-expenses/run-due/")
    assert res.status_code == 200
    assert res.data["charged"] >= 1


@pytest.mark.django_db
def test_due_action_lists_due(authenticated_api_client):
    _account_eur()
    _due_expense()
    res = authenticated_api_client.get("/api/v1/recurring-expenses/due/")
    assert res.status_code == 200
    assert len(res.data) == 1


@pytest.mark.django_db
def test_destroy_soft_deletes(authenticated_api_client):
    _account_eur()
    exp = _due_expense()
    res = authenticated_api_client.delete(f"/api/v1/recurring-expenses/{exp.id}/")
    assert res.status_code == 204
    exp.refresh_from_db()
    assert exp.is_active is False


@pytest.mark.django_db
def test_charge_requires_manager():
    _account_eur()
    exp = _due_expense()
    staff = _client_with_role("STAFF")
    res = staff.post(f"/api/v1/recurring-expenses/{exp.id}/charge/")
    assert res.status_code == 403


@pytest.mark.django_db
def test_reverse_charge_action():
    account = _account_eur()
    exp = _due_expense()
    manager = _client_with_role("MANAGER")
    charged = manager.post(f"/api/v1/recurring-expenses/{exp.id}/charge/")
    charge_id = charged.data["id"]
    res = manager.post(f"/api/v1/expense-charges/{charge_id}/reverse/")
    assert res.status_code == 200
    account.refresh_from_db()
    assert account.current_balance == Decimal("5000.00")


@pytest.mark.django_db
def test_charges_filtered_by_expense(authenticated_api_client):
    _account_eur()
    exp = _due_expense()
    authenticated_api_client.post(f"/api/v1/recurring-expenses/{exp.id}/charge/")
    res = authenticated_api_client.get(
        f"/api/v1/expense-charges/?recurring_expense={exp.id}"
    )
    assert res.status_code == 200
    assert res.data["count"] == 1


@pytest.mark.django_db
def test_create_requires_manager():
    _account_eur()
    staff = _client_with_role("STAFF")
    res = staff.post("/api/v1/recurring-expenses/", {
        "name": "Rent", "amount": "500.00", "currency": "EUR",
        "account_type": "BANK", "frequency": "MONTHLY", "start_date": "2026-01-01",
    }, format="json")
    assert res.status_code == 403


@pytest.mark.django_db
def test_list_requires_authentication():
    res = APIClient().get("/api/v1/recurring-expenses/")
    assert res.status_code in (401, 403)
