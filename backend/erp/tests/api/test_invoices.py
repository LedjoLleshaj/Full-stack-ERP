from rest_framework.test import APIClient

from erp.tests.base import ErpTestCase


class InvoiceTests(ErpTestCase):
    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def test_generate_pdf_for_sale(self):
        sale = self.create_sale()
        resp = self.api.get(f"/erp/transaction/{sale.transaction.id}/invoice/")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp["Content-Disposition"].startswith("attachment;")
        assert len(resp.content) > 100

    def test_generate_html_for_sale(self):
        sale = self.create_sale()
        resp = self.api.get(f"/erp/transaction/{sale.transaction.id}/invoice/", {"output": "html"})
        assert resp.status_code == 200
        assert "text/html" in resp["Content-Type"]
        content = resp.content.decode()
        assert "FATURË" in content
        assert self.client_obj.firstname in content

    def test_invoice_not_found(self):
        resp = self.api.get("/erp/transaction/99999/invoice/")
        assert resp.status_code == 404

    def test_invoice_requires_auth(self):
        sale = self.create_sale()
        anon = APIClient()
        resp = anon.get(f"/erp/transaction/{sale.transaction.id}/invoice/")
        assert resp.status_code in (401, 403)
