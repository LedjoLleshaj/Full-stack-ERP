from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command

from erp.constants import AccountType, Currency, ExpenseFrequency
from erp.models import Account, ExpenseCharge, RecurringExpense


def _expense_due_today():
    return RecurringExpense.objects.create(
        name="Rent",
        amount=Decimal("500.00"),
        currency=Currency.EUR,
        account_type=AccountType.BANK,
        frequency=ExpenseFrequency.MONTHLY,
        start_date=date(2020, 1, 1),  # far past -> due now
    )


@pytest.mark.django_db
def test_command_dry_run_makes_no_changes():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("5000.00"),
    )
    _expense_due_today()
    call_command("charge_due_expenses", "--dry-run")
    assert ExpenseCharge.objects.count() == 0


@pytest.mark.django_db
def test_command_charges_due_expenses():
    account = Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("5000.00"),
    )
    _expense_due_today()
    call_command("charge_due_expenses")
    assert ExpenseCharge.objects.count() >= 1
    account.refresh_from_db()
    assert account.current_balance < Decimal("5000.00")
