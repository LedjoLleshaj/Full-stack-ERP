"""
Expense service for recurring-expense money processing.

Mirrors PaymentService conventions: a custom error type, atomic money
movement, and an auditable AccountTransaction ledger entry per charge.
"""

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db import transaction as db_transaction
from django.utils import timezone

from erp.constants import ExpenseChargeStatus, ExpenseFrequency
from erp.models import Account, AccountTransaction, ExpenseCharge, RecurringExpense


class ExpenseError(Exception):
    """Custom exception for expense processing errors."""

    pass


class ExpenseService:
    """Centralized recurring-expense processing logic."""

    @staticmethod
    def compute_next_due(frequency: str, from_date: date) -> date:
        """Return the next due date after `from_date` for the given frequency."""
        if frequency == ExpenseFrequency.DAILY:
            return from_date + timedelta(days=1)
        if frequency == ExpenseFrequency.WEEKLY:
            return from_date + timedelta(days=7)
        if frequency == ExpenseFrequency.MONTHLY:
            month = from_date.month + 1
            year = from_date.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            last_day = calendar.monthrange(year, month)[1]
            return date(year, month, min(from_date.day, last_day))
        raise ExpenseError(f"Unknown expense frequency: {frequency}")

    @staticmethod
    def get_account(account_type: str, currency: str) -> Account:
        """Resolve the company Account for an expense; raise if missing."""
        try:
            return Account.objects.get(account_type=account_type, currency=currency)
        except Account.DoesNotExist:
            raise ExpenseError(
                f"No {account_type} account found for {currency}"
            ) from None

    @classmethod
    @db_transaction.atomic
    def charge_expense(
        cls, expense: RecurringExpense, period_date: date
    ) -> ExpenseCharge:
        """
        Post a single charge for `expense` covering `period_date`.

        Resolves the paying account, writes a WITHDRAWAL ledger entry
        (balance may go negative), records an ExpenseCharge audit row,
        and advances the expense's next_due_date.
        """
        if ExpenseCharge.objects.filter(
            recurring_expense=expense, period_date=period_date
        ).exists():
            raise ExpenseError(
                f"Expense '{expense.name}' already charged for {period_date}"
            )

        account = cls.get_account(expense.account_type, expense.currency)
        new_balance = account.current_balance - expense.amount

        ledger = AccountTransaction.objects.create(
            account=account,
            transaction_type="WITHDRAWAL",
            amount=expense.amount,
            balance_after=new_balance,
            payment=None,
            notes=f"Recurring expense: {expense.name} ({period_date})",
        )

        account.current_balance = new_balance
        account.save(update_fields=["current_balance"])

        charge = ExpenseCharge.objects.create(
            recurring_expense=expense,
            account=account,
            amount=expense.amount,
            currency=expense.currency,
            period_date=period_date,
            account_transaction=ledger,
            status=ExpenseChargeStatus.POSTED,
        )

        expense.next_due_date = cls.compute_next_due(expense.frequency, period_date)
        expense.save(update_fields=["next_due_date"])

        return charge

    @classmethod
    def process_due_expenses(cls, as_of: date | None = None) -> dict[str, Any]:
        """
        Charge every active auto expense whose next_due_date <= as_of,
        catching up each missed period. Returns a summary dict whose
        ``total_amount`` is a Decimal.

        Each charge is committed individually (charge_expense is atomic, but
        this method is not): a mid-batch failure leaves earlier charges
        committed. A failed expense is recorded in ``skipped`` and processing
        continues with the next expense.
        """
        as_of = as_of or timezone.localdate()
        summary: dict[str, Any] = {
            "charged": 0,
            "total_amount": Decimal("0"),
            "charges": [],
            "skipped": [],
        }

        expenses = RecurringExpense.objects.filter(
            is_active=True, auto_charge=True, next_due_date__lte=as_of
        )

        for expense in expenses:
            while expense.next_due_date <= as_of and (
                expense.end_date is None or expense.next_due_date <= expense.end_date
            ):
                period = expense.next_due_date
                try:
                    charge = cls.charge_expense(expense, period)
                except Exception as exc:  # noqa: BLE001
                    summary["skipped"].append(
                        {
                            "expense_id": expense.id,
                            "name": expense.name,
                            "reason": str(exc),
                        }
                    )
                    break  # next_due_date did not advance; stop catching up this expense
                summary["charged"] += 1
                summary["total_amount"] += charge.amount
                summary["charges"].append(charge.id)

        return summary

    @classmethod
    @db_transaction.atomic
    def reverse_charge(cls, charge: ExpenseCharge) -> None:
        """Restore the account balance for a charge and mark it REVERSED."""
        if charge.status == ExpenseChargeStatus.REVERSED:
            raise ExpenseError("Charge already reversed")

        account = charge.account
        new_balance = account.current_balance + charge.amount

        AccountTransaction.objects.create(
            account=account,
            transaction_type="DEPOSIT",
            amount=charge.amount,
            balance_after=new_balance,
            payment=None,
            notes=f"Reversal of expense charge #{charge.id}",
        )

        account.current_balance = new_balance
        account.save(update_fields=["current_balance"])

        charge.status = ExpenseChargeStatus.REVERSED
        charge.save(update_fields=["status"])
