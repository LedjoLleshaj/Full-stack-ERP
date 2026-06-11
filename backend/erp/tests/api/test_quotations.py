from datetime import date, timedelta

from rest_framework.test import APIClient

from erp.models import Inventory, Quotation, Sales, Transaction
from erp.tests.base import ErpTestCase


class QuotationTests(ErpTestCase):
    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def _create_quotation(self, **overrides):
        defaults = {
            "client": self.client_obj.id,
            "currency": "EUR",
            "valid_until": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Test quotation",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 5,
                    "unit_price": "15.00",
                    "tax_rate": self.tax_rate.id,
                    "tax_amount": "0",
                }
            ],
        }
        defaults.update(overrides)
        return self.api.post("/erp/create-quotation", data=defaults, format="json")

    def test_create_quotation(self):
        resp = self._create_quotation()
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "DRAFT"
        assert data["client"] == self.client_obj.id
        assert len(data["items"]) == 1

    def test_list_quotations(self):
        self._create_quotation()
        resp = self.api.get("/erp/quotations")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_quotation_detail(self):
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]
        resp = self.api.get(f"/erp/quotation/{qid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == qid
        assert len(resp.json()["items"]) == 1

    def test_update_status(self):
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]
        resp = self.api.post(f"/erp/quotation/{qid}/status", data={"status": "SENT"}, format="json")
        assert resp.status_code == 200
        assert resp.json()["status"] == "SENT"

    def test_convert_to_sale(self):
        Inventory.objects.create(prod=self.product, quantity=100)
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]

        self.api.post(f"/erp/quotation/{qid}/status", data={"status": "ACCEPTED"}, format="json")

        resp = self.api.post(f"/erp/quotation/{qid}/convert", format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert "transaction_id" in data

        quotation = Quotation.objects.get(id=qid)
        assert quotation.status == "CONVERTED"
        assert quotation.converted_transaction is not None
        assert Transaction.objects.filter(id=data["transaction_id"]).exists()
        assert Sales.objects.filter(transaction_id=data["transaction_id"]).exists()

    def test_convert_draft_rejected(self):
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]
        resp = self.api.post(f"/erp/quotation/{qid}/convert", format="json")
        assert resp.status_code == 400

    def test_delete_quotation(self):
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]
        resp = self.api.delete(f"/erp/delete-quotation/{qid}")
        assert resp.status_code == 200
        assert not Quotation.objects.filter(id=qid).exists()

    def test_delete_converted_rejected(self):
        Inventory.objects.create(prod=self.product, quantity=100)
        create_resp = self._create_quotation()
        qid = create_resp.json()["id"]

        self.api.post(f"/erp/quotation/{qid}/status", data={"status": "ACCEPTED"}, format="json")
        self.api.post(f"/erp/quotation/{qid}/convert", format="json")

        resp = self.api.delete(f"/erp/delete-quotation/{qid}")
        assert resp.status_code == 400
