"""
Management command to charge all due recurring expenses.
Run with: python manage.py charge_due_expenses [--dry-run]

Schedule this to run daily (e.g. via cron) to post recurring expenses
automatically. Mirrors sync_exchange_rates scheduling.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from erp.models import RecurringExpense
from erp.services.expense_service import ExpenseService


class Command(BaseCommand):
    help = "Charge all due recurring expenses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be charged without making changes",
        )

    def handle(self, *args, **options):
        as_of = timezone.localdate()

        if options["dry_run"]:
            due = RecurringExpense.objects.filter(
                is_active=True, auto_charge=True, next_due_date__lte=as_of
            )
            self.stdout.write(
                self.style.WARNING(f"DRY RUN ({as_of}) - {due.count()} expense(s) due:")
            )
            for exp in due:
                self.stdout.write(
                    f"  {exp.name}: {exp.amount} {exp.currency} "
                    f"(due {exp.next_due_date}, {exp.account_type})"
                )
            return

        summary = ExpenseService.process_due_expenses(as_of=as_of)
        self.stdout.write(
            self.style.SUCCESS(
                f"Charged {summary['charged']} expense occurrence(s), "
                f"total {summary['total_amount']}."
            )
        )
        for skipped in summary["skipped"]:
            self.stdout.write(
                self.style.WARNING(f"  Skipped {skipped['name']}: {skipped['reason']}")
            )
