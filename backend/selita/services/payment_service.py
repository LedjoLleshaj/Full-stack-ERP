"""
Payment service for centralized payment processing.

This module consolidates all payment logic that was previously duplicated
across sales.py, restocks.py, and inventory.py (~300 lines of repeated code).
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from django.db import transaction as db_transaction
from django.utils import timezone
from django.db.models import Sum

from selita.models import Payment, Account, Transaction
from selita.utils.currency import get_exchange_rate


class PaymentError(Exception):
    """Custom exception for payment processing errors."""
    pass


class PaymentService:
    """Centralized payment processing logic."""
    
    @staticmethod
    def calculate_remaining_balance(transaction: Transaction) -> Decimal:
        """Calculate remaining balance for a transaction."""
        total_paid = Payment.objects.filter(
            transaction=transaction
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        return transaction.total_amount - total_paid
    
    @staticmethod
    def get_account_for_payment(payment_method: str, currency: str) -> Account:
        """
        Get the appropriate account for a payment.
        
        Args:
            payment_method: CASH or BANK
            currency: EUR, USD, or LEK
            
        Returns:
            Account object
            
        Raises:
            PaymentError if no matching account found
        """
        account_type = "CASH" if payment_method == "CASH" else "BANK"
        try:
            return Account.objects.get(account_type=account_type, currency=currency)
        except Account.DoesNotExist:
            raise PaymentError(f"No {account_type} account found for {currency}")
    
    @classmethod
    @db_transaction.atomic
    def create_payment(
        cls,
        transaction: Transaction,
        amount: Decimal,
        payment_currency: str,
        payment_method: str = "CASH",
        notes: str = "",
        pay_remaining: bool = False,
        tolerance: Decimal = Decimal("0.01")
    ) -> Dict[str, Any]:
        """
        Create a payment for a transaction.
        
        Handles:
        - Currency conversion between payment and transaction currencies
        - Account selection based on payment method
        - Account balance updates
        - Transaction status updates (PENDING -> PARTIAL -> COMPLETED)
        
        Args:
            transaction: The Transaction to pay
            amount: Payment amount in payment_currency
            payment_currency: Currency of the payment
            payment_method: CASH or BANK
            notes: Optional notes for the payment
            pay_remaining: If True, adjusts for small rounding differences
            tolerance: Rounding tolerance for comparisons
        
        Returns:
            Dict with payment details:
                - payment_id: ID of created payment
                - transaction_status: New status of transaction
                - total_paid: Total amount paid so far
                - remaining: Remaining balance
        
        Raises:
            PaymentError: For validation errors
        """
        if amount <= 0:
            raise PaymentError("Payment amount must be greater than zero")
        
        if transaction.status == "COMPLETED":
            raise PaymentError("Transaction is already fully paid")
        
        if transaction.status == "CANCELLED":
            raise PaymentError("Cannot pay a cancelled transaction")
        
        transaction_currency = transaction.currency
        
        # Calculate current state
        remaining = cls.calculate_remaining_balance(transaction)
        
        # Currency conversion
        if payment_currency != transaction_currency:
            exchange_rate = get_exchange_rate(payment_currency, transaction_currency)
            amount_in_transaction_currency = amount * exchange_rate
        else:
            exchange_rate = Decimal("1.0")
            amount_in_transaction_currency = amount
        
        # Handle pay_remaining flag - adjust for rounding differences
        if pay_remaining:
            tolerance_amount = remaining * Decimal("0.05")  # 5% tolerance
            if abs(amount_in_transaction_currency - remaining) <= tolerance_amount:
                amount_in_transaction_currency = remaining
        
        # Validate amount doesn't exceed remaining
        if amount_in_transaction_currency > remaining + tolerance:
            raise PaymentError(
                f"Payment amount ({amount_in_transaction_currency:.2f} {transaction_currency}) "
                f"exceeds remaining balance ({remaining:.2f} {transaction_currency})"
            )
        
        # Get account
        account = cls.get_account_for_payment(payment_method, payment_currency)
        
        # Create payment record
        payment = Payment.objects.create(
            transaction=transaction,
            account=account,
            amount=amount_in_transaction_currency,
            currency=transaction_currency,
            original_amount=amount if payment_currency != transaction_currency else None,
            original_currency=payment_currency if payment_currency != transaction_currency else None,
            exchange_rate=exchange_rate if payment_currency != transaction_currency else None,
            payment_method=payment_method,
            notes=notes,
        )
        
        # Update account balance
        if transaction.transaction_type == "SALE":
            account.current_balance += amount  # Money in
        else:  # PURCHASE
            account.current_balance -= amount  # Money out
        account.save()
        
        # Update transaction status
        total_paid = Payment.objects.filter(
            transaction=transaction
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        
        remaining_after = transaction.total_amount - total_paid
        
        if remaining_after <= tolerance:
            transaction.status = "COMPLETED"
            transaction.completed_date = timezone.now()
            remaining_after = Decimal("0.00")
        elif total_paid > 0:
            transaction.status = "PARTIAL"
        transaction.save()
        
        return {
            "payment_id": payment.id,
            "transaction_status": transaction.status,
            "total_paid": float(total_paid),
            "remaining": float(remaining_after),
        }
    
    @classmethod
    def process_initial_payment(
        cls,
        transaction: Transaction,
        payment_data: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Process initial payment when creating a sale or restock.
        
        Args:
            transaction: The newly created Transaction
            payment_data: Dict with keys: amount, currency, payment_method
                         Can be None if no payment is being made
        
        Returns:
            Payment result dict or None if no payment made
        """
        if not payment_data:
            return None
        
        amount = Decimal(str(payment_data.get("amount", 0)))
        if amount <= 0:
            return None
        
        return cls.create_payment(
            transaction=transaction,
            amount=amount,
            payment_currency=payment_data.get("currency", transaction.currency),
            payment_method=payment_data.get("payment_method", "CASH"),
            notes=payment_data.get("notes", ""),
        )
