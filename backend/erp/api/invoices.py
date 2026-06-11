from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from erp.models import Transaction
from erp.services.invoice_service import InvoiceService
from erp.utils.responses import api_error_handler, not_found_response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def generate_invoice(request, pk):
    try:
        transaction = Transaction.objects.select_related("client", "supplier").get(id=pk)
    except Transaction.DoesNotExist:
        return not_found_response("Transaction")

    fmt = request.query_params.get("output", "pdf")
    invoice_number = transaction.invoice_number or f"INV-{transaction.id:06d}"

    if fmt == "html":
        html = InvoiceService.render_html(transaction)
        return HttpResponse(html, content_type="text/html")

    pdf_buffer = InvoiceService.generate_pdf(transaction)
    response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{invoice_number}.pdf"'
    return response
