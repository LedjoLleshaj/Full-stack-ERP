import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from erp.constants import Currency, TransactionStatus, TransactionType
from erp.models import Client, PaymentTerms, Transaction, User


class TestPaymentTermsAPI(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="termsuser",
            password="testpass123",
            firstname="Terms",
            lastname="Tester",
            role="ADMIN",
        )
        cls.net30 = PaymentTerms.objects.create(
            name="Net 30", days=30, description="Payment due in 30 days"
        )
        cls.cod = PaymentTerms.objects.create(
            name="COD", days=0, description="Cash on delivery"
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_payment_terms(self):
        resp = self.client.get("/api/v1/payment-terms/")
        assert resp.status_code == 200
        results = resp.data["results"]
        assert len(results) == 2

    def test_create_payment_terms(self):
        resp = self.client.post("/api/v1/payment-terms/", {
            "name": "Net 60",
            "days": 60,
            "description": "Payment due in 60 days",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["name"] == "Net 60"
        assert resp.data["days"] == 60

    def test_update_payment_terms(self):
        resp = self.client.patch(f"/api/v1/payment-terms/{self.net30.id}/", {
            "days": 45,
        })
        assert resp.status_code == 200
        assert resp.data["days"] == 45

    def test_delete_payment_terms(self):
        tmp = PaymentTerms.objects.create(name="Temp", days=7)
        resp = self.client.delete(f"/api/v1/payment-terms/{tmp.id}/")
        assert resp.status_code == 204

    def test_inactive_terms_hidden(self):
        PaymentTerms.objects.create(name="Inactive", days=99, is_active=False)
        resp = self.client.get("/api/v1/payment-terms/")
        names = [r["name"] for r in resp.data["results"]]
        assert "Inactive" not in names


class TestDueDateAutoCalculation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="duedateuser",
            password="testpass123",
            firstname="Due",
            lastname="Date",
            role="ADMIN",
        )
        cls.net30 = PaymentTerms.objects.create(name="Net 30", days=30)
        cls.cod = PaymentTerms.objects.create(name="COD", days=0)
        cls.client_obj = Client.objects.create(
            firstname="Test", lastname="Client",
            phone="5551234", address="123 St", city="Tirana",
        )

    def test_due_date_set_from_payment_terms(self):
        txn = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency=Currency.EUR,
            payment_terms=self.net30,
        )
        assert txn.due_date is not None
        expected = txn.created_date.date() + datetime.timedelta(days=30)
        assert txn.due_date == expected

    def test_due_date_zero_days(self):
        txn = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("50.00"),
            currency=Currency.EUR,
            payment_terms=self.cod,
        )
        assert txn.due_date == txn.created_date.date()

    def test_explicit_due_date_not_overridden(self):
        explicit = datetime.date(2026, 12, 31)
        txn = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency=Currency.EUR,
            payment_terms=self.net30,
            due_date=explicit,
        )
        assert txn.due_date == explicit

    def test_no_payment_terms_no_due_date(self):
        txn = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency=Currency.EUR,
        )
        assert txn.due_date is None


class TestOverdueEndpoint(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="overdueuser",
            password="testpass123",
            firstname="Overdue",
            lastname="Tester",
            role="ADMIN",
        )
        cls.client_obj = Client.objects.create(
            firstname="Over", lastname="Due",
            phone="5559999", address="789 St", city="Tirana",
        )
        cls.net30 = PaymentTerms.objects.create(name="Net 30", days=30)

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def test_overdue_returns_past_due_unpaid(self):
        txn = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
            due_date=datetime.date(2020, 1, 1),
        )
        resp = self.api.get("/api/v1/transactions/overdue/")
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.data]
        assert txn.id in ids

    def test_overdue_excludes_completed(self):
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency=Currency.EUR,
            status=TransactionStatus.COMPLETED,
            due_date=datetime.date(2020, 1, 1),
        )
        resp = self.api.get("/api/v1/transactions/overdue/")
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_overdue_excludes_future_due(self):
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
            due_date=datetime.date(2099, 12, 31),
        )
        resp = self.api.get("/api/v1/transactions/overdue/")
        assert resp.status_code == 200
        assert len(resp.data) == 0


class TestAgingReport(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="aginguser",
            password="testpass123",
            firstname="Aging",
            lastname="Tester",
            role="ADMIN",
        )
        cls.client_obj = Client.objects.create(
            firstname="Aging", lastname="Client",
            phone="5558888", address="321 St", city="Tirana",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def test_aging_report_buckets(self):
        today = timezone.now().date()
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
            due_date=today + datetime.timedelta(days=5),
        )
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
            due_date=today - datetime.timedelta(days=15),
        )
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("300.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PARTIAL,
            due_date=today - datetime.timedelta(days=45),
        )
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("400.00"),
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
            due_date=today - datetime.timedelta(days=100),
        )

        resp = self.api.get("/api/v1/transactions/aging-report/")
        assert resp.status_code == 200
        data = resp.data
        assert data["summary"]["current"]["count"] == 1
        assert data["summary"]["1_30"]["count"] == 1
        assert data["summary"]["31_60"]["count"] == 1
        assert data["summary"]["over_90"]["count"] == 1

    def test_aging_excludes_completed(self):
        today = timezone.now().date()
        Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("500.00"),
            currency=Currency.EUR,
            status=TransactionStatus.COMPLETED,
            due_date=today - datetime.timedelta(days=10),
        )
        resp = self.api.get("/api/v1/transactions/aging-report/")
        assert resp.status_code == 200
        summary = resp.data["summary"]
        total = sum(b["count"] for b in summary.values())
        assert total == 0
