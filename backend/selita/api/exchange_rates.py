"""
API endpoints for exchange rates.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from selita.models import ExchangeRate, CURRENCY_CHOICES


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_exchange_rates(request):
    """
    Get all exchange rates.
    Returns a dictionary with rates organized by from_currency.
    """
    rates = ExchangeRate.objects.all()
    
    result = {}
    last_updated = None
    
    for rate in rates:
        if rate.from_currency not in result:
            result[rate.from_currency] = {}
        result[rate.from_currency][rate.to_currency] = float(rate.rate)
        
        # Track most recent update
        if last_updated is None or rate.last_updated > last_updated:
            last_updated = rate.last_updated
    
    return Response({
        "rates": result,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "currencies": [code for code, _ in CURRENCY_CHOICES]
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_exchange_rate(request, from_currency, to_currency):
    """
    Get a specific exchange rate between two currencies.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Same currency = rate of 1
    if from_currency == to_currency:
        return Response({
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0
        })
    
    try:
        rate = ExchangeRate.objects.get(
            from_currency=from_currency,
            to_currency=to_currency
        )
        return Response({
            "from_currency": rate.from_currency,
            "to_currency": rate.to_currency,
            "rate": float(rate.rate),
            "last_updated": rate.last_updated.isoformat()
        })
    except ExchangeRate.DoesNotExist:
        return Response(
            {"error": f"Exchange rate not found for {from_currency} to {to_currency}"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def convert_currency(request):
    """
    Convert an amount from one currency to another.
    
    Request body:
    {
        "amount": 100.00,
        "from_currency": "EUR",
        "to_currency": "LEK"
    }
    """
    amount = request.data.get("amount")
    from_currency = request.data.get("from_currency", "").upper()
    to_currency = request.data.get("to_currency", "").upper()
    
    if amount is None:
        return Response(
            {"error": "Amount is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        amount = Decimal(str(amount))
    except:
        return Response(
            {"error": "Invalid amount"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Same currency = no conversion needed
    if from_currency == to_currency:
        return Response({
            "original_amount": float(amount),
            "converted_amount": float(amount),
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0
        })
    
    try:
        rate_obj = ExchangeRate.objects.get(
            from_currency=from_currency,
            to_currency=to_currency
        )
        converted = amount * rate_obj.rate
        
        return Response({
            "original_amount": float(amount),
            "converted_amount": float(converted.quantize(Decimal("0.01"))),
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": float(rate_obj.rate),
            "last_updated": rate_obj.last_updated.isoformat()
        })
    except ExchangeRate.DoesNotExist:
        return Response(
            {"error": f"Exchange rate not found for {from_currency} to {to_currency}. Please run 'python manage.py sync_exchange_rates' to update rates."},
            status=status.HTTP_404_NOT_FOUND
        )
