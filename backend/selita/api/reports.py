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
    from ..models import ExchangeRate
    from decimal import Decimal
    
    today = date.today()
    
    def convert_to_eur(amount, currency):
        """Convert amount from any currency to EUR"""
        if currency == "EUR":
            return amount
        try:
            rate = ExchangeRate.objects.get(from_currency=currency, to_currency="EUR")
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            # Fallback: return as-is if no rate found
            return amount

    # 1. Revenue Today - convert all currencies to EUR
    revenue_today = Decimal("0")
    today_sales = Transaction.objects.filter(
        transaction_type="SALE",
        created_date__date=today
    ).exclude(status="CANCELLED")
    for sale in today_sales:
        revenue_today += convert_to_eur(sale.total_amount, sale.currency)

    # 2. Revenue Month - convert all currencies to EUR
    revenue_month = Decimal("0")
    month_sales = Transaction.objects.filter(
        transaction_type="SALE",
        created_date__year=today.year,
        created_date__month=today.month
    ).exclude(status="CANCELLED")
    for sale in month_sales:
        revenue_month += convert_to_eur(sale.total_amount, sale.currency)

    # 3. Profit (Total Sales - Total Purchases) - convert all currencies to EUR
    total_sales = Decimal("0")
    all_sales = Transaction.objects.filter(
        transaction_type="SALE"
    ).exclude(status="CANCELLED")
    for sale in all_sales:
        total_sales += convert_to_eur(sale.total_amount, sale.currency)

    total_purchases = Decimal("0")
    all_purchases = Transaction.objects.filter(
        transaction_type="PURCHASE"
    ).exclude(status="CANCELLED")
    for purchase in all_purchases:
        total_purchases += convert_to_eur(purchase.total_amount, purchase.currency)

    profit = total_sales - total_purchases

    # 4. Get all accounts with individual balances (grouped by type and currency)
    accounts = Account.objects.all().values('account_type', 'currency', 'current_balance', 'account_name')
    
    # Build account balances list
    account_balances = []
    for acc in accounts:
        account_balances.append({
            "name": acc['account_name'],
            "type": acc['account_type'],
            "currency": acc['currency'],
            "balance": float(acc['current_balance']),
        })

    # 5. Debt (Total pending/partial sales amount - Total paid for those sales)
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
        "accounts": account_balances,  # All accounts with individual balances
        "debt": debt,
    }

    return Response(data)


@api_view(["GET"])
def daily_profit(request):
    """
    Get daily profit data for the past 30 days.
    Returns an array of {date, profit} objects for chart visualization.
    """
    from ..models import ExchangeRate
    from decimal import Decimal
    from datetime import timedelta
    
    today = date.today()
    start_date = today - timedelta(days=30)
    
    def convert_to_eur(amount, currency):
        """Convert amount from any currency to EUR"""
        if currency == "EUR":
            return amount
        try:
            rate = ExchangeRate.objects.get(from_currency=currency, to_currency="EUR")
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            return amount
    
    # Get all transactions in the date range
    sales = Transaction.objects.filter(
        transaction_type="SALE",
        created_date__date__gte=start_date,
        created_date__date__lte=today
    ).exclude(status="CANCELLED")
    
    purchases = Transaction.objects.filter(
        transaction_type="PURCHASE",
        created_date__date__gte=start_date,
        created_date__date__lte=today
    ).exclude(status="CANCELLED")
    
    # Build daily sales totals (in EUR)
    daily_sales = {}
    for sale in sales:
        sale_date = sale.created_date.date()
        amount_eur = convert_to_eur(sale.total_amount, sale.currency)
        daily_sales[sale_date] = daily_sales.get(sale_date, Decimal("0")) + amount_eur
    
    # Build daily purchase totals (in EUR)
    daily_purchases = {}
    for purchase in purchases:
        purchase_date = purchase.created_date.date()
        amount_eur = convert_to_eur(purchase.total_amount, purchase.currency)
        daily_purchases[purchase_date] = daily_purchases.get(purchase_date, Decimal("0")) + amount_eur
    
    # Build result with all dates in range
    result = []
    current_date = start_date
    while current_date <= today:
        sales_amount = daily_sales.get(current_date, Decimal("0"))
        purchases_amount = daily_purchases.get(current_date, Decimal("0"))
        profit = sales_amount - purchases_amount
        
        result.append({
            "date": current_date.isoformat(),
            "profit": float(profit)
        })
        current_date += timedelta(days=1)
    
    return Response(result)

