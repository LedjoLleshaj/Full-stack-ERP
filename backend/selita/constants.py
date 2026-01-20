"""
Constants used throughout the Selita backend.

Centralizes magic strings to prevent typos and enable IDE autocomplete.
"""


class TransactionStatus:
    """Status values for Transaction records."""
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    CHOICES = [
        (PENDING, "Pending"),
        (PARTIAL, "Partial"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]
    
    # Statuses that indicate unpaid or partially paid
    UNPAID_STATUSES = [PENDING, PARTIAL]


class TransactionType:
    """Type values for Transaction records."""
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    
    CHOICES = [
        (PURCHASE, "Purchase"),
        (SALE, "Sale"),
    ]


class AccountType:
    """Type values for Account records."""
    CASH = "CASH"
    BANK = "BANK"
    
    CHOICES = [
        (CASH, "Cash"),
        (BANK, "Bank"),
    ]


class PaymentMethod:
    """Payment method values."""
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    
    CHOICES = [
        (CASH, "Cash"),
        (CARD, "Card"),
        (TRANSFER, "Bank Transfer"),
    ]


class Currency:
    """Currency codes."""
    EUR = "EUR"
    USD = "USD"
    LEK = "LEK"
    
    CHOICES = [
        (EUR, "Euro"),
        (USD, "US Dollar"),
        (LEK, "Albanian Lek"),
    ]
    
    # Default currency for the application
    DEFAULT = EUR
