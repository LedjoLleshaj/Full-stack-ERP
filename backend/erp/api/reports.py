from datetime import date

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.constants import TransactionStatus, TransactionType
from erp.utils.currency import convert_to_eur_with_rates, get_all_rates_dict
from erp.utils.responses import api_error_handler

from ..models import Account, Payment, Sales, Transaction
from ..serializers import SalesReportSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Fix: Access client through transaction, not directly on sale
    sales_qs = Sales.objects.select_related("prod", "transaction", "transaction__client", "tax_rate")

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
        TransactionStatus.COMPLETED: "✅ Paguar",
        TransactionStatus.PARTIAL: "⚠️ Paguar pjeserisht",
        TransactionStatus.PENDING: "❌ Pa paguar",
        TransactionStatus.CANCELLED: "🚫 Anuluar"
    }
    
    for sale in sales_qs:
        # Get client from transaction (may be null)
        client = sale.transaction.client if sale.transaction else None
        client_name = f"{client.firstname} {client.lastname}" if client else "N/A"
        client_address = client.address if client else "N/A"
        
        # Get payment status from transaction
        transaction_status = sale.transaction.status if sale.transaction else TransactionStatus.PENDING
        payment_status = status_map.get(transaction_status, "N/A")
        
        report_data.append({
            "Produkti": sale.prod.name,
            "Sasia": sale.quantity,
            "Cmimi shitje": float(sale.prod_price),
            "Totali": float(sale.total),
            "TVSH": float(sale.tax_amount),
            "Totali me TVSH": float(sale.total) + float(sale.tax_amount),
            "Data e shitjes": sale.sale_date.date().isoformat(),
            "Klienti": client_name,
            "Adresa e klientit": client_address,
            "Statusi i pageses": payment_status,
        })

    SalesReportSerializer(report_data, many=True)
    return Response(report_data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def dashboard_stats(request):
    from decimal import Decimal
    
    today = date.today()
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()

    # Get ALL transactions at once (1 query)
    all_transactions = list(Transaction.objects.exclude(status="CANCELLED"))
    
    # Calculate metrics in memory (no additional queries)
    revenue_today = Decimal("0")
    revenue_month = Decimal("0")
    total_sales = Decimal("0")
    total_purchases = Decimal("0")
    pending_sale_ids = []
    pending_sales_map = {}
    
    for trans in all_transactions:
        amount_eur = convert_to_eur_with_rates(trans.total_amount, trans.currency, rates)
        
        if trans.transaction_type == TransactionType.SALE:
            total_sales += amount_eur
            
            # Check if created today
            if trans.created_date and trans.created_date.date() == today:
                revenue_today += amount_eur
            
            # Check if created this month
            if trans.created_date and trans.created_date.year == today.year and trans.created_date.month == today.month:
                revenue_month += amount_eur
            
            # Track pending sales for debt calculation
            if trans.status in TransactionStatus.UNPAID_STATUSES:
                pending_sale_ids.append(trans.id)
                pending_sales_map[trans.id] = {
                    "total": trans.total_amount,
                    "currency": trans.currency
                }
                
        elif trans.transaction_type == TransactionType.PURCHASE:
            total_purchases += amount_eur

    profit = total_sales - total_purchases

    # Get account balances (1 query)
    accounts = Account.objects.all().values('account_type', 'currency', 'current_balance', 'account_name')
    account_balances = [
        {
            "name": acc['account_name'],
            "type": acc['account_type'],
            "currency": acc['currency'],
            "balance": float(acc['current_balance']),
        }
        for acc in accounts
    ]

    # Calculate debt - get all payments for pending sales (1 query)
    debt = Decimal("0")
    if pending_sale_ids:
        from django.db.models import Sum
        payments_by_trans = dict(
            Payment.objects.filter(transaction_id__in=pending_sale_ids)
            .values('transaction_id')
            .annotate(total_paid=Sum('amount'))
            .values_list('transaction_id', 'total_paid')
        )
        
        for trans_id, sale_info in pending_sales_map.items():
            paid = payments_by_trans.get(trans_id, Decimal("0")) or Decimal("0")
            remaining = sale_info["total"] - paid
            if remaining > 0:
                debt += convert_to_eur_with_rates(remaining, sale_info["currency"], rates)

    data = {
        "revenue_today": revenue_today,
        "revenue_month": revenue_month,
        "profit": profit,
        "accounts": account_balances,
        "debt": debt,
    }

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def daily_profit(request):
    """
    Get daily profit data for a specified time period.
    Query params:
    - days: Number of days to look back (default: 30, max: 365, use 0 for all time)
    Returns an array of {date, sales, purchases, profit} objects for chart visualization.
    """
    from datetime import timedelta
    from decimal import Decimal
    
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
    
    # Cache exchange rates upfront (1 query instead of N queries)
    rates = get_all_rates_dict()
    
    # Get all transactions in the date range (2 queries total)
    sales = Transaction.objects.filter(
        transaction_type=TransactionType.SALE,
        created_date__date__gte=start_date,
        created_date__date__lte=today
    ).exclude(status="CANCELLED")
    
    purchases = Transaction.objects.filter(
        transaction_type="PURCHASE",
        created_date__date__gte=start_date,
        created_date__date__lte=today
    ).exclude(status="CANCELLED")
    
    # Build daily sales totals (in EUR) - no additional queries
    daily_sales = {}
    for sale in sales:
        sale_date = sale.created_date.date()
        amount_eur = convert_to_eur_with_rates(sale.total_amount, sale.currency, rates)
        daily_sales[sale_date] = daily_sales.get(sale_date, Decimal("0")) + amount_eur
    
    # Build daily purchase totals (in EUR) - no additional queries
    daily_purchases = {}
    for purchase in purchases:
        purchase_date = purchase.created_date.date()
        amount_eur = convert_to_eur_with_rates(purchase.total_amount, purchase.currency, rates)
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
@permission_classes([IsAuthenticated])
@api_error_handler
def paid_vs_unpaid(request):
    """
    Get paid vs unpaid sales statistics for pie chart visualization.
    
    Categories:
    - Paid: Completed sales total + paid portions of partial sales
    - Partial: Remaining debt on partial sales only
    - Unpaid: Pending sales total (nothing paid yet)
    """
    from decimal import Decimal
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
    # Get all sales transactions with prefetched payments (2 queries total)
    all_sales = Transaction.objects.filter(
        transaction_type=TransactionType.SALE
    ).exclude(status="CANCELLED").prefetch_related('payments')
    
    # Initialize counters
    paid_amount = Decimal("0")
    paid_count = 0  # Count of fully paid sales
    unpaid_amount = Decimal("0")
    unpaid_count = 0  # Count of pending sales
    partial_remaining = Decimal("0")  # Remaining debt on partial sales
    partial_count = 0  # Count of partial sales
    
    for sale in all_sales:
        amount_eur = convert_to_eur_with_rates(sale.total_amount, sale.currency, rates)
        
        if sale.status == TransactionStatus.COMPLETED:
            # Fully paid - entire amount goes to "Paid"
            paid_amount += amount_eur
            paid_count += 1
        elif sale.status == TransactionStatus.PARTIAL:
            # Get total payments from prefetched data (no additional query)
            payments_made = sum(p.amount for p in sale.payments.all())
            
            # Convert payments to EUR
            payments_eur = convert_to_eur_with_rates(payments_made, sale.currency, rates)
            
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
@permission_classes([IsAuthenticated])
@api_error_handler
def top_products(request):
    """
    Get the top 5 best-selling products by quantity sold.
    Returns product names and their total quantities sold.
    """
    
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
@permission_classes([IsAuthenticated])
@api_error_handler
def profit_by_category(request):
    """
    Get profit by product category.
    Returns category names and their total profit (sales revenue - purchase cost).
    Optimized to use fewer database queries.
    """
    from collections import defaultdict
    from decimal import Decimal

    from ..models import Product, Restock
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
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
            category_revenue[category] += convert_to_eur_with_rates(amount, currency, rates)
    
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
            category_cost[category] += convert_to_eur_with_rates(total_cost, currency, rates)
    
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
@permission_classes([IsAuthenticated])
@api_error_handler
def top_clients(request):
    """
    Get the top 5 clients by total purchase amount.
    Returns client names and their total purchase amounts.
    Optimized to use minimal database queries.
    """
    from collections import defaultdict
    from decimal import Decimal
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
    # Get all sale transactions with client info in ONE query
    transactions = Transaction.objects.filter(
        transaction_type=TransactionType.SALE,
        client__isnull=False
    ).exclude(status="CANCELLED").select_related('client')
    
    # Aggregate in memory (no additional queries)
    client_data = defaultdict(lambda: {"total": Decimal("0"), "count": 0, "name": ""})
    
    for trans in transactions:
        client_id = trans.client_id
        amount_eur = convert_to_eur_with_rates(trans.total_amount, trans.currency, rates)
        client_data[client_id]["total"] += amount_eur
        client_data[client_id]["count"] += 1
        client_data[client_id]["name"] = f"{trans.client.firstname} {trans.client.lastname}"
    
    # Build result list
    client_totals = [
        {
            "name": data["name"],
            "total_amount": float(data["total"]),
            "transaction_count": data["count"]
        }
        for data in client_data.values()
        if data["total"] > 0
    ]
    
    # Sort by total amount descending and take top 5
    client_totals.sort(key=lambda x: x['total_amount'], reverse=True)
    top_5 = client_totals[:5]
    
    return Response(top_5)
