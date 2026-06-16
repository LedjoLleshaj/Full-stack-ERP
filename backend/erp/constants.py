"""
Constants used throughout the ERP backend.

Centralizes magic strings to prevent typos and enable IDE autocomplete.
"""


class TransactionStatus:
    """Status values for Transaction records."""
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

    CHOICES = [
        (PENDING, "Pending"),
        (PARTIAL, "Partial"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
        (REFUNDED, "Refunded"),
    ]

    # Statuses that indicate unpaid or partially paid
    UNPAID_STATUSES = [PENDING, PARTIAL]


class TransactionType:
    """Type values for Transaction records."""
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RETURN = "RETURN"

    CHOICES = [
        (PURCHASE, "Purchase"),
        (SALE, "Sale"),
        (RETURN, "Return"),
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


class UserRole:
    """Role hierarchy for access control. ADMIN > MANAGER > STAFF > VIEWER."""
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    STAFF = "STAFF"
    VIEWER = "VIEWER"

    CHOICES = [
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (STAFF, "Staff"),
        (VIEWER, "Viewer"),
    ]

    MANAGER_AND_ABOVE = {ADMIN, MANAGER}
    STAFF_AND_ABOVE = {ADMIN, MANAGER, STAFF}


class QuotationStatus:
    """Status values for Quotation records."""
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CONVERTED = "CONVERTED"

    CHOICES = [
        (DRAFT, "Draft"),
        (SENT, "Sent"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (EXPIRED, "Expired"),
        (CONVERTED, "Converted"),
    ]

    CONVERTIBLE = {ACCEPTED}


class DiscountType:
    PERCENT = "PERCENT"
    FIXED = "FIXED"

    CHOICES = [
        (PERCENT, "Percentage"),
        (FIXED, "Fixed Amount"),
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
