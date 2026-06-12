"""
Payment service for centralized payment processing.

This module consolidates all payment logic that was previously duplicated
across sales.py, restocks.py, and inventory.py (~300 lines of repeated code).
"""

from decimal import Decimal
from typing import Any

from django.db import transaction as db_transaction
from django.db.models import Sum
from django.utils import timezone

from erp.constants import TransactionStatus, TransactionType
from erp.models import Account, Payment, Sales, Transaction
from erp.utils.currency import get_exchange_rate


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
            raise PaymentError(f"No {account_type} account found for {currency}") from None
    @classmethod
    @db_transaction.atomic
    def reverse_all_payments(
        cls,
        transaction: Transaction
    ) -> dict[str, Any]:
        """
        Reverse all payments for a transaction.
        
        This is used when deleting a sale or restock to restore account balances
        to their state before the payments were made.
        
        Args:
            transaction: The Transaction whose payments should be reversed
        
        Returns:
            Dict with reversal details:
                - total_reversed: Total amount reversed (in transaction currency)
                - accounts_affected: List of account IDs that were modified
                - payment_count: Number of payments that were reversed
        """
        # Get all payments for this transaction
        payments = Payment.objects.filter(transaction=transaction).select_related('account')
        
        if not payments.exists():
            return {
                "total_reversed": 0.0,
                "accounts_affected": [],
                "payment_count": 0,
            }
        
        total_reversed = Decimal("0")
        accounts_affected = []
        
        # Reverse each payment's effect on account balance
        for payment in payments:
            account = payment.account
            
            # Determine the original payment amount (considering currency conversion)
            payment_amount = payment.original_amount if payment.original_amount else payment.amount
            
            # Reverse the account balance change
            if transaction.transaction_type == "SALE":
                # Sale: we received money, now remove it (reverse revenue)
                account.current_balance -= payment_amount
            else:  # PURCHASE
                # Purchase: we paid money, now add it back (get refund)
                account.current_balance += payment_amount
            
            account.save()
            
            if account.id not in accounts_affected:
                accounts_affected.append(account.id)
            
            total_reversed += payment.amount
        
        payment_count = payments.count()
        
        # Delete all payments (or they'll be cascade deleted with transaction)
        # We explicitly delete here to be clear about the operation
        payments.delete()
        
        return {
            "total_reversed": float(total_reversed),
            "accounts_affected": accounts_affected,
            "payment_count": payment_count,
        }

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
    ) -> dict[str, Any]:
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
        payment_data: dict[str, Any] | None
    ) -> dict[str, Any] | None:
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
    
    @staticmethod
    def calculate_total_paid(transaction: Transaction) -> Decimal:
        """
        Calculate total amount paid for a transaction.
        
        Args:
            transaction: The Transaction to calculate payments for
        
        Returns:
            Total amount paid as Decimal
        """
        total = Payment.objects.filter(
            transaction=transaction
        ).aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0")

    @classmethod
    @db_transaction.atomic
    def update_payment(
        cls,
        payment: Payment,
        amount: Decimal,  # New amount in payment currency
        currency: str,    # New currency for the payment
        payment_method: str = None,  # New payment method (CASH or CARD)
        notes: str = ""
    ) -> dict[str, Any]:
        """
        Update an existing payment's amount, currency, payment method and notes.
        
        Handles:
        - Reversing old account balance from the original account
        - Finding/Updating correct account based on new currency AND payment method
        - Calculating new balance adjustment
        - Recalculating transaction status
        
        Per schema: CASH payment -> CASH account, CARD payment -> BANK account
        """
        if amount <= 0:
            raise PaymentError("Payment amount must be greater than zero")
        
        # Use provided payment_method or keep the existing one
        new_payment_method = payment_method if payment_method else payment.payment_method
            
        transaction = payment.transaction
        old_account = payment.account
        
        # 1. Reverse old account balance
        # What was the ACTUAL amount added/removed from the account?
        old_actual_amount = payment.original_amount if payment.original_amount else payment.amount
        
        if transaction.transaction_type == "SALE":
            old_account.current_balance -= old_actual_amount # Reverse money in
        else: # PURCHASE
            old_account.current_balance += old_actual_amount # Reverse money out
        old_account.save()
            
        # 2. Get new account (might be different if currency OR payment_method changed)
        new_account = cls.get_account_for_payment(new_payment_method, currency)
        
        # 3. Calculate new amount in transaction currency
        transaction_currency = transaction.currency
        if currency != transaction_currency:
            exchange_rate = get_exchange_rate(currency, transaction_currency)
            amount_in_transaction_currency = (amount * exchange_rate).quantize(Decimal("0.01"))
        else:
            exchange_rate = Decimal("1.0")
            amount_in_transaction_currency = amount
            
        # 4. Validate that new total doesn't exceed transaction total
        # Recalculate total paid excluding THIS payment
        other_payments_total = Payment.objects.filter(
            transaction=transaction
        ).exclude(id=payment.id).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")
        
        new_total_paid = other_payments_total + amount_in_transaction_currency
        
        if new_total_paid > transaction.total_amount + Decimal("0.01"):
            raise PaymentError(
                f"New total paid ({new_total_paid:.2f}) exceeds transaction total ({transaction.total_amount:.2f})"
            )
            
        # 5. Update new account balance
        if transaction.transaction_type == "SALE":
            new_account.current_balance += amount # Money in
        else: # PURCHASE
            new_account.current_balance -= amount # Money out
        new_account.save()
        
        # 6. Update payment record
        payment.account = new_account
        payment.amount = amount_in_transaction_currency
        payment.currency = transaction_currency
        payment.original_amount = amount if currency != transaction_currency else None
        payment.original_currency = currency if currency != transaction_currency else None
        payment.exchange_rate = exchange_rate if currency != transaction_currency else None
        payment.payment_method = new_payment_method
        payment.notes = notes
        payment.save()
        
        # 7. Update transaction status
        if new_total_paid >= transaction.total_amount - Decimal("0.01"):
            transaction.status = "COMPLETED"
            if not transaction.completed_date:
                transaction.completed_date = timezone.now()
        elif new_total_paid > 0:
            transaction.status = "PARTIAL"
        else:
            transaction.status = "PENDING"
            transaction.completed_date = None
        transaction.save()
        
        return {
            "payment_id": payment.id,
            "transaction_status": transaction.status,
            "total_paid": float(new_total_paid),
        }

    @classmethod
    @db_transaction.atomic
    def delete_payment(cls, payment: Payment) -> dict[str, Any]:
        """
        Delete a payment and reverse its effect on accounting.
        """
        transaction = payment.transaction
        account = payment.account
        amount = payment.amount
        
        # Reverse account balance
        # If the payment has original_amount, it means it was a currency conversion payment.
        # We must reverse the amount that was actually taken from the account.
        reversal_amount = payment.original_amount if payment.original_amount else amount
        
        if transaction.transaction_type == "SALE":
            account.current_balance -= reversal_amount
        else: # PURCHASE
            account.current_balance += reversal_amount
        account.save()
        
        # Delete payment
        payment.delete()
        
        # Recalculate transaction status
        total_paid = cls.calculate_total_paid(transaction)
        if total_paid <= Decimal("0.01"):
            transaction.status = "PENDING"
            transaction.completed_date = None
        elif total_paid < transaction.total_amount - Decimal("0.01"):
            transaction.status = "PARTIAL"
            transaction.completed_date = None
        else:
            # Still completed? (rare if deleting a valid payment)
            transaction.status = "COMPLETED"
            
        transaction.save()
        
        return {
            "transaction_status": transaction.status,
            "total_paid": float(total_paid),
        }

    @classmethod
    @db_transaction.atomic
    def update_transaction_status(
        cls, 
        transaction: Transaction, 
        new_total_amount: Decimal, 
        transaction_currency: str
    ) -> Transaction:
        """
        Update transaction amount, currency, and recalculate status.
        
        This centralizes the logic used in both sales.updateSale and restocks.updateRestock.
        
        Args:
            transaction: Transaction object to update
            new_total_amount: New total amount (e.g. price * quantity)
            transaction_currency: Currency for the transaction
        
        Returns:
            Updated Transaction object (saved)
            
        Raises:
            PaymentError: If validation fails (e.g. new amount < total paid)
        """
        # 1. Detect if it was fully paid before update
        tolerance = Decimal("0.10")  # Increased tolerance for currency rounding
        total_paid_before = cls.calculate_total_paid(transaction)
        was_completed = (transaction.total_amount <= total_paid_before + Decimal("0.01"))
        
        # 2. Detect currency change
        old_currency = transaction.currency
        currency_changed = (old_currency != transaction_currency)
        
        # 3. If currency changed, convert all existing payments to the new currency
        if currency_changed:
            from erp.utils.currency import get_exchange_rate
            rate = get_exchange_rate(old_currency, transaction_currency)
            
            payments = list(Payment.objects.filter(transaction=transaction).order_by('id'))
            for payment in payments:
                # If this is the first time we change currency, preserve the initial payment details
                # so that deletions later can reverse the correct account balance.
                if payment.original_amount is None:
                    payment.original_amount = payment.amount
                    payment.original_currency = old_currency
                
                payment.amount = (payment.amount * rate).quantize(Decimal("0.01"))
                payment.currency = transaction_currency
                payment.save()
            
            # Re-calculate total paid after simple conversion
            total_paid = cls.calculate_total_paid(transaction)
            
            # If it was completed before, and we have a tiny rounding discrepancy,
            # adjust the last payment to make it exactly match the new total.
            # This prevents rounding drift from flipping status to PARTIAL.
            if was_completed and payments:
                # new_total_amount is the goal
                discrepancy = new_total_amount - total_paid
                if abs(discrepancy) <= tolerance:
                    last_payment = payments[-1]
                    last_payment.amount += discrepancy
                    last_payment.save()
                    total_paid = new_total_amount # Exactly matched now
        else:
            total_paid = total_paid_before

        # Validation: Cannot reduce total below what's already paid (with tolerance)
        if new_total_amount < total_paid - tolerance:
             raise PaymentError(
                f"Cannot reduce total to {float(new_total_amount):.2f} {transaction_currency}. "
                f"Already paid {float(total_paid):.2f} {transaction_currency}."
            )
            
        # Update details
        transaction.total_amount = new_total_amount
        transaction.currency = transaction_currency
        
        # Recalculate status
        if new_total_amount <= total_paid + tolerance:
            transaction.status = "COMPLETED"
            if not transaction.completed_date:
                transaction.completed_date = timezone.now()
        elif total_paid > tolerance:
            transaction.status = "PARTIAL"
        else:
            transaction.status = "PENDING"
            transaction.completed_date = None
            
        transaction.save()
        return transaction

    @classmethod
    @db_transaction.atomic
    def process_return(
        cls,
        original_transaction: Transaction,
        return_items: list[dict],
        refund_method: str,
        refund_currency: str,
        user,
    ) -> dict[str, Any]:
        from erp.services.inventory_service import InventoryService

        if original_transaction.transaction_type != TransactionType.SALE:
            raise PaymentError("Returns can only be created for sale transactions")

        if original_transaction.status in (TransactionStatus.CANCELLED, TransactionStatus.REFUNDED):
            raise PaymentError(
                f"Cannot return a {original_transaction.status.lower()} transaction"
            )

        if not return_items:
            raise PaymentError("No return items provided")

        total_return_value = Decimal("0")
        return_sales_data = []
        inventory_restored = []

        for item in return_items:
            sale_line = Sales.objects.select_related("prod", "tax_rate").get(
                id=item["sale_line_id"]
            )

            if sale_line.transaction_id != original_transaction.id:
                raise PaymentError(
                    f"Sale line {sale_line.id} does not belong to this transaction"
                )

            return_qty = Decimal(str(item["quantity"]))
            if return_qty <= 0:
                raise PaymentError("Return quantity must be greater than zero")

            already_returned = Sales.objects.filter(
                transaction__original_transaction=original_transaction,
                transaction__transaction_type=TransactionType.RETURN,
                prod=sale_line.prod,
            ).aggregate(total=Sum("quantity"))["total"] or 0

            max_returnable = sale_line.quantity - already_returned
            if return_qty > max_returnable:
                raise PaymentError(
                    f"Cannot return {return_qty} of {sale_line.prod.name}. "
                    f"Max returnable: {max_returnable}"
                )

            subtotal = sale_line.prod_price * return_qty
            tax_amount = Decimal("0")
            if sale_line.tax_rate and sale_line.tax_rate.rate > 0:
                tax_amount = (subtotal * sale_line.tax_rate.rate / Decimal("100")).quantize(
                    Decimal("0.01")
                )
            line_return_value = subtotal + tax_amount

            total_return_value += line_return_value
            return_sales_data.append({
                "prod": sale_line.prod,
                "prod_price": sale_line.prod_price,
                "quantity": return_qty,
                "tax_rate": sale_line.tax_rate,
                "tax_amount": tax_amount,
            })
            inventory_restored.append({
                "product": sale_line.prod.name,
                "quantity": int(return_qty),
            })

        return_transaction = Transaction.objects.create(
            transaction_type=TransactionType.RETURN,
            client=original_transaction.client,
            total_amount=total_return_value,
            currency=original_transaction.currency,
            status=TransactionStatus.COMPLETED,
            original_transaction=original_transaction,
            notes=f"Return against transaction #{original_transaction.id}",
        )

        for data in return_sales_data:
            Sales.objects.create(
                transaction=return_transaction,
                prod=data["prod"],
                prod_price=data["prod_price"],
                user=user,
                quantity=data["quantity"],
                tax_rate=data["tax_rate"],
                tax_amount=data["tax_amount"],
            )
            InventoryService.add_inventory(data["prod"], data["quantity"])

        total_paid = cls.calculate_total_paid(original_transaction)
        original_transaction.total_amount -= total_return_value
        new_total = original_transaction.total_amount

        refund_amount = max(Decimal("0"), total_paid - new_total)

        if refund_amount > 0:
            account = cls.get_account_for_payment(refund_method, refund_currency)

            if refund_currency != original_transaction.currency:
                exchange_rate = get_exchange_rate(
                    original_transaction.currency, refund_currency
                )
                refund_in_payment_currency = (refund_amount * exchange_rate).quantize(
                    Decimal("0.01")
                )
            else:
                exchange_rate = Decimal("1.0")
                refund_in_payment_currency = refund_amount

            Payment.objects.create(
                transaction=return_transaction,
                account=account,
                amount=refund_amount,
                currency=original_transaction.currency,
                original_amount=refund_in_payment_currency if refund_currency != original_transaction.currency else None,
                original_currency=refund_currency if refund_currency != original_transaction.currency else None,
                exchange_rate=exchange_rate if refund_currency != original_transaction.currency else None,
                payment_method=refund_method,
                notes=f"Refund for return #{return_transaction.id}",
            )

            account.current_balance -= refund_in_payment_currency
            account.save()

        tolerance = Decimal("0.01")
        if new_total <= tolerance:
            original_transaction.status = TransactionStatus.REFUNDED
            original_transaction.total_amount = Decimal("0.00")
        elif total_paid >= new_total - tolerance:
            original_transaction.status = TransactionStatus.COMPLETED
        elif total_paid > tolerance:
            original_transaction.status = TransactionStatus.PARTIAL
        else:
            original_transaction.status = TransactionStatus.PENDING

        original_transaction.save()

        return {
            "return_transaction_id": return_transaction.id,
            "return_value": float(total_return_value),
            "refund_amount": float(refund_amount),
            "inventory_restored": inventory_restored,
            "original_transaction_status": original_transaction.status,
        }
