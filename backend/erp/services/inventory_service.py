"""
Inventory service for centralized inventory management.

This module consolidates inventory update logic that was previously duplicated
across sales.py, restocks.py, and inventory.py.
"""

from decimal import Decimal

from django.db import transaction as db_transaction

from erp.models import Inventory, Product


class InventoryError(Exception):
    """Custom exception for inventory errors."""
    pass


class InventoryService:
    """Centralized inventory management logic."""
    
    @staticmethod
    def get_or_create_inventory(product: Product) -> Inventory:
        """
        Get or create an inventory record for a product.
        
        Args:
            product: The Product to get inventory for
            
        Returns:
            Inventory object
        """
        inventory, created = Inventory.objects.get_or_create(
            prod=product,
            defaults={"quantity": 0}
        )
        return inventory
    
    @staticmethod
    def get_inventory_quantity(product: Product) -> Decimal:
        """
        Get the current inventory quantity for a product.
        
        Args:
            product: The Product to check
            
        Returns:
            Current quantity (Decimal) or 0 if no inventory record
        """
        try:
            inventory = Inventory.objects.get(prod=product)
            return inventory.quantity
        except Inventory.DoesNotExist:
            return Decimal("0")
    
    @classmethod
    @db_transaction.atomic
    def reduce_inventory(
        cls,
        product: Product,
        quantity: Decimal,
        allow_negative: bool = False
    ) -> Decimal:
        """
        Reduce inventory for a product (used for sales).
        
        Args:
            product: The Product to reduce inventory for
            quantity: Amount to reduce
            allow_negative: If False, raises error when insufficient inventory
            
        Returns:
            New inventory quantity
            
        Raises:
            InventoryError if insufficient inventory and allow_negative is False
        """
        inventory = cls.get_or_create_inventory(product)
        
        if not allow_negative and inventory.quantity < quantity:
            raise InventoryError(
                f"Insufficient inventory for {product.name}. "
                f"Available: {inventory.quantity}, Requested: {quantity}"
            )
        
        inventory.quantity -= quantity
        inventory.save()
        return inventory.quantity
    
    @classmethod
    @db_transaction.atomic
    def add_inventory(
        cls,
        product: Product,
        quantity: Decimal
    ) -> Decimal:
        """
        Add to inventory for a product (used for restocks).
        
        Args:
            product: The Product to add inventory for
            quantity: Amount to add
            
        Returns:
            New inventory quantity
        """
        inventory = cls.get_or_create_inventory(product)
        inventory.quantity += quantity
        inventory.save()
        return inventory.quantity
    
    @classmethod
    @db_transaction.atomic
    def set_inventory(
        cls,
        product: Product,
        quantity: Decimal
    ) -> Decimal:
        """
        Set inventory to a specific quantity.
        
        Args:
            product: The Product to set inventory for
            quantity: New quantity value
            
        Returns:
            New inventory quantity
        """
        inventory = cls.get_or_create_inventory(product)
        inventory.quantity = quantity
        inventory.save()
        return inventory.quantity
    
    @classmethod
    def available_stock(cls, product: Product) -> int:
        """
        Return the current on-hand quantity for a product.

        The authoritative on-hand quantity is stored in Inventory.quantity
        for that product. Updated by sales (reduce) and restocks (add).

        Args:
            product: The Product to check

        Returns:
            Current on-hand quantity (int), or 0 if no inventory record.
        """
        try:
            inventory = Inventory.objects.get(prod=product)
            return inventory.quantity
        except Inventory.DoesNotExist:
            return 0

    @classmethod
    def check_availability(
        cls,
        product: Product,
        required_quantity: Decimal
    ) -> bool:
        """
        Check if sufficient inventory is available.

        Args:
            product: The Product to check
            required_quantity: Amount needed

        Returns:
            True if sufficient inventory is available
        """
        current = cls.get_inventory_quantity(product)
        return current >= required_quantity
