from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from erp.constants import AccountType, Currency, ExpenseChargeStatus, ExpenseFrequency
from erp.models import Account, AccountTransaction, ExpenseCharge, RecurringExpense
from erp.services.expense_service import ExpenseError, ExpenseService


def test_expense_frequency_choices():
    values = {c[0] for c in ExpenseFrequency.CHOICES}
    assert values == {"DAILY", "WEEKLY", "MONTHLY"}
    assert ExpenseFrequency.DAILY == "DAILY"
    assert ExpenseFrequency.WEEKLY == "WEEKLY"
    assert ExpenseFrequency.MONTHLY == "MONTHLY"


def test_expense_charge_status_choices():
    values = {c[0] for c in ExpenseChargeStatus.CHOICES}
    assert values == {"POSTED", "REVERSED"}
    assert ExpenseChargeStatus.POSTED == "POSTED"
    assert ExpenseChargeStatus.REVERSED == "REVERSED"


@pytest.mark.django_db
def test_recurring_expense_defaults_next_due_to_start():
    exp = RecurringExpense.objects.create(
        name="Office rent",
        amount=Decimal("500.00"),
        currency=Currency.EUR,
        account_type=AccountType.BANK,
        frequency=ExpenseFrequency.MONTHLY,
        start_date=date(2026, 1, 1),
    )
    assert exp.next_due_date == date(2026, 1, 1)
    assert exp.is_active is True
    assert exp.auto_charge is True


@pytest.mark.django_db
def test_expense_charge_unique_per_period():
    exp = RecurringExpense.objects.create(
        name="Rent",
        amount=Decimal("500.00"),
        currency=Currency.EUR,
        account_type=AccountType.BANK,
        frequency=ExpenseFrequency.MONTHLY,
        start_date=date(2026, 1, 1),
    )
    account = Account.objects.create(
        account_name="Bank EUR",
        account_type=AccountType.BANK,
        currency=Currency.EUR,
        current_balance=Decimal("0.00"),
    )
    ExpenseCharge.objects.create(
        recurring_expense=exp, account=account, amount=exp.amount,
        currency=exp.currency, period_date=date(2026, 1, 1),
    )
    with pytest.raises(IntegrityError):
        ExpenseCharge.objects.create(
            recurring_expense=exp, account=account, amount=exp.amount,
            currency=exp.currency, period_date=date(2026, 1, 1),
        )


# ---------------------------------------------------------------------------
# Part A — compute_next_due
# ---------------------------------------------------------------------------

def test_compute_next_due_daily():
    assert ExpenseService.compute_next_due(
        ExpenseFrequency.DAILY, date(2026, 1, 31)
    ) == date(2026, 2, 1)


def test_compute_next_due_weekly():
    assert ExpenseService.compute_next_due(
        ExpenseFrequency.WEEKLY, date(2026, 1, 1)
    ) == date(2026, 1, 8)


def test_compute_next_due_monthly():
    assert ExpenseService.compute_next_due(
        ExpenseFrequency.MONTHLY, date(2026, 1, 15)
    ) == date(2026, 2, 15)


def test_compute_next_due_monthly_clamps_month_end():
    assert ExpenseService.compute_next_due(
        ExpenseFrequency.MONTHLY, date(2026, 1, 31)
    ) == date(2026, 2, 28)


def test_compute_next_due_monthly_year_rollover():
    assert ExpenseService.compute_next_due(
        ExpenseFrequency.MONTHLY, date(2026, 12, 10)
    ) == date(2027, 1, 10)


def test_compute_next_due_rejects_unknown_frequency():
    with pytest.raises(ExpenseError):
        ExpenseService.compute_next_due("YEARLY", date(2026, 1, 1))


# ---------------------------------------------------------------------------
# Part B — get_account + charge_expense
# ---------------------------------------------------------------------------

def _make_expense(**overrides):
    defaults = dict(
        name="Rent",
        amount=Decimal("500.00"),
        currency=Currency.EUR,
        account_type=AccountType.BANK,
        frequency=ExpenseFrequency.MONTHLY,
        start_date=date(2026, 1, 1),
    )
    defaults.update(overrides)
    return RecurringExpense.objects.create(**defaults)


@pytest.mark.django_db
def test_charge_expense_moves_money_and_writes_ledger():
    account = Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("2000.00"),
    )
    exp = _make_expense()
    charge = ExpenseService.charge_expense(exp, date(2026, 1, 1))
    account.refresh_from_db()
    assert account.current_balance == Decimal("1500.00")
    assert charge.status == ExpenseChargeStatus.POSTED
    assert charge.amount == Decimal("500.00")
    assert charge.account_transaction is not None
    assert charge.account_transaction.transaction_type == "WITHDRAWAL"
    assert charge.account_transaction.balance_after == Decimal("1500.00")
    exp.refresh_from_db()
    assert exp.next_due_date == date(2026, 2, 1)


@pytest.mark.django_db
def test_charge_expense_allows_negative_balance():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("100.00"),
    )
    exp = _make_expense(amount=Decimal("500.00"))
    charge = ExpenseService.charge_expense(exp, date(2026, 1, 1))
    assert charge.account.current_balance == Decimal("-400.00")


@pytest.mark.django_db
def test_charge_expense_rejects_missing_account():
    exp = _make_expense(account_type=AccountType.CASH, currency=Currency.USD)
    with pytest.raises(ExpenseError, match="No CASH account"):
        ExpenseService.charge_expense(exp, date(2026, 1, 1))


@pytest.mark.django_db
def test_charge_expense_rejects_duplicate_period():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("2000.00"),
    )
    exp = _make_expense()
    ExpenseService.charge_expense(exp, date(2026, 1, 1))
    with pytest.raises(ExpenseError, match="already charged"):
        ExpenseService.charge_expense(exp, date(2026, 1, 1))


# ---------------------------------------------------------------------------
# Part C — process_due_expenses
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_process_due_charges_and_catches_up_missed_periods():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("10000.00"),
    )
    exp = _make_expense(
        frequency=ExpenseFrequency.DAILY,
        amount=Decimal("10.00"),
        start_date=date(2026, 1, 1),
    )
    summary = ExpenseService.process_due_expenses(as_of=date(2026, 1, 4))
    assert summary["charged"] == 4
    assert summary["total_amount"] == Decimal("40.00")
    exp.refresh_from_db()
    assert exp.next_due_date == date(2026, 1, 5)
    assert ExpenseCharge.objects.filter(recurring_expense=exp).count() == 4


@pytest.mark.django_db
def test_process_due_skips_manual_inactive_and_past_end_date():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("10000.00"),
    )
    _make_expense(name="Manual", auto_charge=False)
    _make_expense(name="Inactive", is_active=False)
    _make_expense(name="Ended", end_date=date(2025, 12, 1))
    summary = ExpenseService.process_due_expenses(as_of=date(2026, 1, 1))
    assert summary["charged"] == 0


@pytest.mark.django_db
def test_process_due_records_skipped_when_account_missing():
    exp = _make_expense(account_type=AccountType.CASH, currency=Currency.USD)
    summary = ExpenseService.process_due_expenses(as_of=date(2026, 1, 1))
    assert summary["charged"] == 0
    assert len(summary["skipped"]) == 1
    assert summary["skipped"][0]["expense_id"] == exp.id
    exp.refresh_from_db()
    assert exp.next_due_date == date(2026, 1, 1)  # not advanced on skip


# ---------------------------------------------------------------------------
# Part D — reverse_charge
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reverse_charge_restores_balance():
    account = Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("2000.00"),
    )
    exp = _make_expense()
    charge = ExpenseService.charge_expense(exp, date(2026, 1, 1))
    account.refresh_from_db()
    assert account.current_balance == Decimal("1500.00")
    ExpenseService.reverse_charge(charge)
    account.refresh_from_db()
    charge.refresh_from_db()
    assert account.current_balance == Decimal("2000.00")
    assert charge.status == ExpenseChargeStatus.REVERSED
    deposit = AccountTransaction.objects.get(
        account=account, transaction_type="DEPOSIT"
    )
    assert deposit.balance_after == Decimal("2000.00")


@pytest.mark.django_db
def test_reverse_charge_rejects_double_reverse():
    Account.objects.create(
        account_name="Bank EUR", account_type=AccountType.BANK,
        currency=Currency.EUR, current_balance=Decimal("2000.00"),
    )
    exp = _make_expense()
    charge = ExpenseService.charge_expense(exp, date(2026, 1, 1))
    ExpenseService.reverse_charge(charge)
    with pytest.raises(ExpenseError, match="already reversed"):
        ExpenseService.reverse_charge(charge)
    account = Account.objects.get(account_type=AccountType.BANK, currency=Currency.EUR)
    assert account.current_balance == Decimal("2000.00")  # unchanged by failed reverse
    assert AccountTransaction.objects.filter(account=account).count() == 2  # 1 WITHDRAWAL + 1 DEPOSIT
