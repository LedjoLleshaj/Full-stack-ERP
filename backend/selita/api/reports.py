# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Sales
from ..serializers import SalesReportSerializer
from django.db.models import F, ExpressionWrapper, DecimalField


@api_view(["GET"])
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    sales_qs = Sales.objects.select_related("prod", "client")

    if start_date and end_date:
        sales_qs = sales_qs.filter(sale_date__range=[start_date, end_date])

    # Annotate total per sale
    sales_qs = sales_qs.annotate(
        total=ExpressionWrapper(
            F("quantity") * F("prod_price"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    report_data = [
        {
            "Produkti": sale.prod.name,
            "Sasia": sale.quantity,
            "Cmimi shitje": float(sale.prod_price),
            "Totali": float(sale.total),
            "Data e shitjes": sale.sale_date.date().isoformat(),  # <-- keep only date
            "Klienti": f"{sale.client.firstname} {sale.client.lastname}",
            "Adresa e klientit": sale.client.address,
            "Paguar": "po" if sale.is_paid else "jo",
        }
        for sale in sales_qs
    ]

    serializer = SalesReportSerializer(report_data, many=True)
    return Response(report_data)
