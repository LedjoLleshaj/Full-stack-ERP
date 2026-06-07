"""
Currency conversion utilities for the ERP backend.

This module centralizes all currency conversion logic, replacing the
duplicated convert_to_eur functions that were spread across multiple files.
"""

from decimal import Decimal
from functools import lru_cache
from typing import Dict, Optional
from django.db.models import Case, When, F, Value, DecimalField


@lru_cache(maxsize=32)
def get_exchange_rate(from_currency: str, to_currency: str) -> Decimal:
    """
    Get cached exchange rate between currencies.
    
    Args:
        from_currency: Source currency code (EUR, USD, LEK)
        to_currency: Target currency code (EUR, USD, LEK)
    
    Returns:
        Exchange rate as Decimal
    """
    if from_currency == to_currency:
        return Decimal("1")
    
    # Import here to avoid circular imports
    from erp.models import ExchangeRate
    
    try:
        rate = ExchangeRate.objects.get(
            from_currency=from_currency, 
            to_currency=to_currency
        )
        return rate.rate
    except ExchangeRate.DoesNotExist:
        # Try reverse rate
        try:
            rate = ExchangeRate.objects.get(
                from_currency=to_currency,
                to_currency=from_currency
            )
            return Decimal("1") / rate.rate
        except ExchangeRate.DoesNotExist:
            return Decimal("1")


def convert_to_eur(amount, currency: str) -> Decimal:
    """
    Convert amount from any currency to EUR.
    
    Args:
        amount: Amount to convert (can be Decimal, float, int, or str)
        currency: Source currency code
    
    Returns:
        Amount in EUR as Decimal
    """
    if amount is None:
        return Decimal("0")
    return Decimal(str(amount)) * get_exchange_rate(currency, "EUR")


def convert_currency(amount, from_currency: str, to_currency: str) -> Decimal:
    """
    Convert amount between any two currencies.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        Converted amount as Decimal
    """
    if amount is None:
        return Decimal("0")
    return Decimal(str(amount)) * get_exchange_rate(from_currency, to_currency)


def clear_rate_cache():
    """Clear the exchange rate cache. Call after exchange rates are updated."""
    get_exchange_rate.cache_clear()


def get_all_rates_dict() -> Dict[str, Decimal]:
    """
    Get all exchange rates as a dictionary for bulk operations.
    
    Returns:
        Dict with keys like 'LEK_EUR' and Decimal rate values
    """
    from erp.models import ExchangeRate
    
    rates = {}
    for rate in ExchangeRate.objects.all():
        rates[f"{rate.from_currency}_{rate.to_currency}"] = rate.rate
    return rates


def convert_to_eur_with_rates(amount, currency: str, rates: Dict[str, Decimal]) -> Decimal:
    """
    Convert amount to EUR using a pre-fetched rates dictionary.
    
    Use this when you need to convert many amounts in a loop to avoid
    repeated database queries. First call get_all_rates_dict() once,
    then pass the result to this function for each conversion.
    
    Args:
        amount: Amount to convert (can be Decimal, float, int, or str)
        currency: Source currency code
        rates: Pre-fetched rates dict from get_all_rates_dict()
    
    Returns:
        Amount in EUR as Decimal
        
    Example:
        rates = get_all_rates_dict()
        for transaction in transactions:
            eur_amount = convert_to_eur_with_rates(
                transaction.total_amount, 
                transaction.currency, 
                rates
            )
    """
    if amount is None:
        return Decimal("0")
    if currency == "EUR":
        return Decimal(str(amount))
    rate_key = f"{currency}_EUR"
    rate = rates.get(rate_key, Decimal("1"))
    return Decimal(str(amount)) * rate


def build_eur_conversion_case(amount_field: str, currency_field: str):
    """
    Build a Django Case expression for converting amounts to EUR in database queries.
    
    This allows currency conversion to happen at the database level instead of
    in Python loops, which is much more efficient for aggregations.
    
    Args:
        amount_field: Name of the field containing the amount
        currency_field: Name of the field containing the currency code
    
    Returns:
        Django Case expression
    
    Example:
        Transaction.objects.annotate(
            amount_eur=build_eur_conversion_case('total_amount', 'currency')
        ).aggregate(total=Sum('amount_eur'))
    """
    rates = get_all_rates_dict()
    
    return Case(
        When(**{currency_field: 'EUR'}, then=F(amount_field)),
        When(**{currency_field: 'USD'}, then=F(amount_field) * Value(rates.get('USD_EUR', Decimal('1')))),
        When(**{currency_field: 'LEK'}, then=F(amount_field) * Value(rates.get('LEK_EUR', Decimal('0.0089')))),
        default=F(amount_field),
        output_field=DecimalField(max_digits=15, decimal_places=2)
    )
