"""
Unit tests for model validation and data-model integrity (Phase 4).

Tests money field widths, quantity validators, stock enforcement,
and catalog FK backfill.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from erp.constants import TransactionStatus, TransactionType
from erp.models import (
    Account,
    Inventory,
    Product,
    Product_Categories,
    Restock,
    Sales,
    Transaction,
    User,
)
from erp.services.inventory_service import InventoryError, InventoryService


@pytest.mark.django_db
def test_account_holds_millions():
    a = Account(account_name="Cash", account_type="CASH", currency="LEK",
                current_balance=Decimal("12345678.90"))
    a.full_clean()
    a.save()
    assert a.current_balance == Decimal("12345678.90")


@pytest.mark.django_db
def test_negative_quantity_rejected():
    user = User.objects.create_user(username="tester", password="pass", firstname="T", lastname="U")
    prod = Product.objects.create(name="TestProd", category="Cat", price=Decimal("10.00"), description="d")
    Inventory.objects.create(prod=prod, quantity=100)
    txn = Transaction.objects.create(
        transaction_type=TransactionType.SALE, total_amount=Decimal("10.00"),
        currency="EUR", status=TransactionStatus.PENDING
    )
    sale = Sales(transaction=txn, prod=prod, prod_price=Decimal("10.00"), user=user, quantity=-5)
    with pytest.raises(ValidationError):
        sale.full_clean()


@pytest.mark.django_db
def test_zero_quantity_rejected():
    user = User.objects.create_user(username="tester2", password="pass", firstname="T", lastname="U")
    prod = Product.objects.create(name="TestProd2", category="Cat", price=Decimal("10.00"), description="d")
    Inventory.objects.create(prod=prod, quantity=100)
    txn = Transaction.objects.create(
        transaction_type=TransactionType.SALE, total_amount=Decimal("10.00"),
        currency="EUR", status=TransactionStatus.PENDING
    )
    sale = Sales(transaction=txn, prod=prod, prod_price=Decimal("10.00"), user=user, quantity=0)
    with pytest.raises(ValidationError):
        sale.full_clean()


@pytest.mark.django_db
def test_negative_price_rejected():
    prod = Product(name="BadPrice", category="Cat", price=Decimal("-1.00"), description="d")
    with pytest.raises(ValidationError):
        prod.full_clean()


@pytest.mark.django_db
def test_zero_price_rejected():
    prod = Product(name="ZeroPrice", category="Cat", price=Decimal("0.00"), description="d")
    with pytest.raises(ValidationError):
        prod.full_clean()


@pytest.mark.django_db
def test_overselling_rejected():
    prod = Product.objects.create(name="LimitedProd", category="Cat", price=Decimal("10.00"), description="d")
    Inventory.objects.create(prod=prod, quantity=5)
    with pytest.raises(InventoryError):
        InventoryService.reduce_inventory(prod, 10)


@pytest.mark.django_db
def test_available_stock_returns_correct_quantity():
    prod = Product.objects.create(name="StockProd", category="Cat", price=Decimal("10.00"), description="d")
    Inventory.objects.create(prod=prod, quantity=42)
    assert InventoryService.available_stock(prod) == 42


@pytest.mark.django_db
def test_available_stock_returns_zero_when_no_inventory():
    prod = Product.objects.create(name="NoProd", category="Cat", price=Decimal("10.00"), description="d")
    assert InventoryService.available_stock(prod) == 0


@pytest.mark.django_db
def test_category_fk_backfill():
    cat = Product_Categories.objects.create(category_name="Electronics")
    prod = Product.objects.create(name="Phone", category="Electronics", price=Decimal("500.00"), description="d", category_fk=cat)
    assert prod.category_fk == cat


@pytest.mark.django_db
def test_restock_negative_quantity_rejected():
    prod = Product.objects.create(name="RestockProd", category="Cat", price=Decimal("10.00"), description="d")
    txn = Transaction.objects.create(
        transaction_type=TransactionType.PURCHASE, total_amount=Decimal("100.00"),
        currency="EUR", status=TransactionStatus.PENDING
    )
    restock = Restock(transaction=txn, prod=prod, quantity=-3, restock_price=Decimal("5.00"))
    with pytest.raises(ValidationError):
        restock.full_clean()


@pytest.mark.django_db
def test_restock_negative_price_rejected():
    prod = Product.objects.create(name="RestockProd2", category="Cat", price=Decimal("10.00"), description="d")
    txn = Transaction.objects.create(
        transaction_type=TransactionType.PURCHASE, total_amount=Decimal("100.00"),
        currency="EUR", status=TransactionStatus.PENDING
    )
    restock = Restock(transaction=txn, prod=prod, quantity=10, restock_price=Decimal("-1.00"))
    with pytest.raises(ValidationError):
        restock.full_clean()
