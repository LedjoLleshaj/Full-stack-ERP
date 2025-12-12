from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Sales, Transaction, Account, Payment
from ..serializers import SalesReportSerializer
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from datetime import date


@api_view(["GET"])
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Fix: Access client through transaction, not directly on sale
    sales_qs = Sales.objects.select_related("prod", "transaction", "transaction__client")

    # Handle date filtering with smart defaults
    if start_date and end_date:
        sales_qs = sales_qs.filter(sale_date__range=[start_date, end_date])
    elif start_date:
        # Only start_date provided - use today as end_date
        sales_qs = sales_qs.filter(sale_date__range=[start_date, date.today()])
    elif end_date:
        # Only end_date provided - filter up to end_date
        sales_qs = sales_qs.filter(sale_date__lte=end_date)

    # Annotate total per sale
    sales_qs = sales_qs.annotate(
        total=ExpressionWrapper(
            F("quantity") * F("prod_price"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )

    report_data = []
    
    # Status labels in Albanian with emoji indicators
    status_map = {
        "COMPLETED": "✅ Paguar",
        "PARTIAL": "⚠️ Paguar pjeserisht",
        "PENDING": "❌ Pa paguar",
        "CANCELLED": "🚫 Anuluar"
    }
    
    for sale in sales_qs:
        # Get client from transaction (may be null)
        client = sale.transaction.client if sale.transaction else None
        client_name = f"{client.firstname} {client.lastname}" if client else "N/A"
        client_address = client.address if client else "N/A"
        
        # Get payment status from transaction
        transaction_status = sale.transaction.status if sale.transaction else "PENDING"
        payment_status = status_map.get(transaction_status, "N/A")
        
        report_data.append({
            "Produkti": sale.prod.name,
            "Sasia": sale.quantity,
            "Cmimi shitje": float(sale.prod_price),
            "Totali": float(sale.total),
            "Data e shitjes": sale.sale_date.date().isoformat(),
            "Klienti": client_name,
            "Adresa e klientit": client_address,
            "Statusi i pageses": payment_status,
        })

    serializer = SalesReportSerializer(report_data, many=True)
    return Response(report_data)


@api_view(["GET"])
def dashboard_stats(request):
    today = date.today()

    # 1. Revenue Today
    revenue_today = Transaction.objects.filter(
        transaction_type="SALE",
        created_date__date=today
    ).exclude(status="CANCELLED").aggregate(sum_val=Sum("total_amount"))["sum_val"] or 0

    # 2. Revenue Month
    revenue_month = Transaction.objects.filter(
        transaction_type="SALE",
        created_date__year=today.year,
        created_date__month=today.month
    ).exclude(status="CANCELLED").aggregate(sum_val=Sum("total_amount"))["sum_val"] or 0

    # 3. Profit (Total Sales - Total Purchases)
    # Note: This is a simplified "Cash Flow" profit.
    total_sales = Transaction.objects.filter(
        transaction_type="SALE"
    ).exclude(status="CANCELLED").aggregate(sum_val=Sum("total_amount"))["sum_val"] or 0

    total_purchases = Transaction.objects.filter(
        transaction_type="PURCHASE"
    ).exclude(status="CANCELLED").aggregate(sum_val=Sum("total_amount"))["sum_val"] or 0

    profit = total_sales - total_purchases

    # 4. Cash Balance
    cash_balance = Account.objects.filter(
        account_type="CASH"
    ).aggregate(sum_val=Sum("current_balance"))["sum_val"] or 0

    # 5. Bank Balance
    bank_balance = Account.objects.filter(
        account_type="BANK"
    ).aggregate(sum_val=Sum("current_balance"))["sum_val"] or 0

    # 6. Debt (Total pending/partial sales amount - Total paid for those sales)
    pending_sales = Transaction.objects.filter(
        transaction_type="SALE",
        status__in=["PENDING", "PARTIAL"]
    )
    
    # Calculate total expected from pending sales
    total_pending_amount = pending_sales.aggregate(sum_val=Sum("total_amount"))["sum_val"] or 0
    
    # Calculate what has been paid so far for these specific transactions
    paid_towards_pending = Payment.objects.filter(
        transaction__in=pending_sales
    ).aggregate(sum_val=Sum("amount"))["sum_val"] or 0
    
    debt = total_pending_amount - paid_towards_pending

    data = {
        "revenue_today": revenue_today,
        "revenue_month": revenue_month,
        "profit": profit,
        "cash_balance": cash_balance,
        "bank_balance": bank_balance,
        "debt": debt,
    }

    return Response(data)
