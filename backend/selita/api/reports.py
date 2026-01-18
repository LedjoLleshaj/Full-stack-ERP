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
    # Convert all amounts to EUR before summing
    pending_sales = Transaction.objects.filter(
        transaction_type="SALE",
        status__in=["PENDING", "PARTIAL"]
    )
    
    debt = Decimal("0")
    for sale in pending_sales:
        # Get total payments made for this transaction
        payments_made = Payment.objects.filter(
            transaction=sale
        ).aggregate(sum_val=Sum("amount"))["sum_val"] or Decimal("0")
        
        # Calculate remaining for this transaction
        remaining = sale.total_amount - payments_made
        if remaining > 0:
            # Convert to EUR
            debt += convert_to_eur(remaining, sale.currency)

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
    Get daily profit data for a specified time period.
    Query params:
    - days: Number of days to look back (default: 30, max: 365, use 0 for all time)
    Returns an array of {date, sales, purchases, profit} objects for chart visualization.
    """
    from ..models import ExchangeRate
    from decimal import Decimal
    from datetime import timedelta
    
    today = date.today()
    
    # Get days parameter (default 30, max 365, 0 = all time)
    days_param = request.GET.get('days', '30')
    try:
        days = int(days_param)
    except ValueError:
        days = 30
    
    if days == 0:
        # All time - get earliest transaction date
        earliest = Transaction.objects.order_by('created_date').first()
        if earliest:
            start_date = earliest.created_date.date()
        else:
            start_date = today - timedelta(days=30)
    else:
        days = min(max(days, 1), 365)  # Clamp between 1 and 365
        start_date = today - timedelta(days=days)
    
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
            "sales": float(sales_amount),
            "purchases": float(purchases_amount),
            "profit": float(profit)
        })
        current_date += timedelta(days=1)
    
    return Response(result)


@api_view(["GET"])
def paid_vs_unpaid(request):
    """
    Get paid vs unpaid sales statistics for pie chart visualization.
    
    Categories:
    - Paid: Completed sales total + paid portions of partial sales
    - Partial: Remaining debt on partial sales only
    - Unpaid: Pending sales total (nothing paid yet)
    """
    from ..models import ExchangeRate
    from decimal import Decimal
    from django.db.models import Sum
    
    def convert_to_eur(amount, currency):
        """Convert amount from any currency to EUR"""
        if currency == "EUR":
            return amount
        try:
            rate = ExchangeRate.objects.get(from_currency=currency, to_currency="EUR")
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            return amount
    
    # Get all sales transactions (excluding cancelled)
    all_sales = Transaction.objects.filter(
        transaction_type="SALE"
    ).exclude(status="CANCELLED")
    
    # Initialize counters
    paid_amount = Decimal("0")
    paid_count = 0  # Count of fully paid sales
    unpaid_amount = Decimal("0")
    unpaid_count = 0  # Count of pending sales
    partial_remaining = Decimal("0")  # Remaining debt on partial sales
    partial_count = 0  # Count of partial sales
    
    for sale in all_sales:
        amount_eur = convert_to_eur(sale.total_amount, sale.currency)
        
        if sale.status == "COMPLETED":
            # Fully paid - entire amount goes to "Paid"
            paid_amount += amount_eur
            paid_count += 1
        elif sale.status == "PARTIAL":
            # Get total payments made for this sale
            payments_made = Payment.objects.filter(transaction=sale).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")
            
            # Convert payments to EUR (assuming payments are in same currency as sale)
            payments_eur = convert_to_eur(payments_made, sale.currency)
            
            # Add paid portion to "Paid"
            paid_amount += payments_eur
            
            # Calculate remaining debt for "Partial"
            remaining = amount_eur - payments_eur
            partial_remaining += remaining
            partial_count += 1
        else:  # PENDING - nothing paid yet
            unpaid_amount += amount_eur
            unpaid_count += 1
    
    data = {
        "paid": {
            "amount": float(paid_amount),
            "count": paid_count,
            "label": "Paguar"
        },
        "partial": {
            "amount": float(partial_remaining),
            "count": partial_count,
            "label": "Pjesërisht"
        },
        "unpaid": {
            "amount": float(unpaid_amount),
            "count": unpaid_count,
            "label": "Pa Paguar"
        },
        "total": {
            "amount": float(paid_amount + partial_remaining + unpaid_amount),
            "count": paid_count + partial_count + unpaid_count
        }
    }
    
    return Response(data)


@api_view(["GET"])
def top_products(request):
    """
    Get the top 5 best-selling products by quantity sold.
    Returns product names and their total quantities sold.
    """
    from django.db.models import Sum
    
    # Get all sales, group by product, sum quantities, order by total quantity
    top_products_data = (
        Sales.objects
        .exclude(transaction__status="CANCELLED")
        .values('prod__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    
    result = []
    for item in top_products_data:
        result.append({
            "name": item['prod__name'],
            "quantity": float(item['total_quantity'])
        })
    
    return Response(result)


@api_view(["GET"])
def profit_by_category(request):
    """
    Get profit by product category.
    Returns category names and their total profit (sales revenue - purchase cost).
    Optimized to use fewer database queries.
    """
    from ..models import Product, Restock
    from selita.utils.currency import get_all_rates_dict, convert_to_eur
    from decimal import Decimal
    from collections import defaultdict
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
    def convert_eur(amount, currency):
        """Fast conversion using cached rates"""
        if currency == "EUR":
            return Decimal(str(amount))
        rate_key = f"{currency}_EUR"
        rate = rates.get(rate_key, Decimal("1"))
        return Decimal(str(amount)) * rate
    
    # Get all categories (1 query)
    categories = set(Product.objects.values_list('category', flat=True))
    
    # Initialize aggregation dictionaries
    category_revenue = defaultdict(lambda: Decimal("0"))
    category_cost = defaultdict(lambda: Decimal("0"))
    
    # Process all sales at once with prefetched transactions (1 query)
    sales = (
        Sales.objects
        .select_related('prod', 'transaction')
        .exclude(transaction__status="CANCELLED")
        .only('prod__category', 'quantity', 'prod_price', 'transaction__currency')
    )
    
    for sale in sales:
        category = sale.prod.category if sale.prod else None
        if category:
            currency = sale.transaction.currency if sale.transaction else "EUR"
            amount = sale.quantity * sale.prod_price
            category_revenue[category] += convert_eur(amount, currency)
    
    # Process all restocks at once with prefetched transactions (1 query)
    restocks = (
        Restock.objects
        .select_related('prod', 'transaction')
        .exclude(transaction__status="CANCELLED")
        .only('prod__category', 'quantity', 'restock_price', 'transaction__currency')
    )
    
    for restock in restocks:
        category = restock.prod.category if restock.prod else None
        if category:
            currency = restock.transaction.currency if restock.transaction else "EUR"
            total_cost = restock.restock_price * restock.quantity
            category_cost[category] += convert_eur(total_cost, currency)
    
    # Build result
    result = []
    for category_name in categories:
        revenue = category_revenue.get(category_name, Decimal("0"))
        cost = category_cost.get(category_name, Decimal("0"))
        profit = revenue - cost
        
        if revenue > 0 or cost > 0:  # Only include categories with data
            result.append({
                "name": category_name,
                "profit": float(profit),
                "revenue": float(revenue),
                "cost": float(cost)
            })
    
    # Sort by profit descending
    result.sort(key=lambda x: x['profit'], reverse=True)
    
    return Response(result)


@api_view(["GET"])
def top_clients(request):
    """
    Get the top 5 clients by total purchase amount.
    Returns client names and their total purchase amounts.
    """
    from ..models import Client, ExchangeRate
    from decimal import Decimal
    
    def convert_to_eur(amount, currency):
        """Convert amount from any currency to EUR"""
        if currency == "EUR":
            return amount
        try:
            rate = ExchangeRate.objects.get(from_currency=currency, to_currency="EUR")
            return amount * rate.rate
        except ExchangeRate.DoesNotExist:
            return amount
    
    # Get all clients with their transactions
    clients = Client.objects.all()
    
    client_totals = []
    for client in clients:
        # Get all completed/partial sales transactions for this client
        client_transactions = Transaction.objects.filter(
            client=client,
            transaction_type="SALE"
        ).exclude(status="CANCELLED")
        
        total_amount = Decimal("0")
        transaction_count = 0
        for transaction in client_transactions:
            total_amount += convert_to_eur(transaction.total_amount, transaction.currency)
            transaction_count += 1
        
        if total_amount > 0:
            client_totals.append({
                "name": f"{client.firstname} {client.lastname}",
                "total_amount": float(total_amount),
                "transaction_count": transaction_count
            })
    
    # Sort by total amount descending and take top 5
    client_totals.sort(key=lambda x: x['total_amount'], reverse=True)
    top_5 = client_totals[:5]
    
    return Response(top_5)

