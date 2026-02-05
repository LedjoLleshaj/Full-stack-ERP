from django.db import models
from selita.constants import (
    Currency, TransactionStatus, TransactionType, 
    AccountType, PaymentMethod
)


# Use centralized constants
CURRENCY_CHOICES = Currency.CHOICES


class ExchangeRate(models.Model):
    """
    Stores currency exchange rates.
    Rates are stored relative to a base currency.
    Updated weekly via management command.
    """
    from_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    to_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exchange_rate"
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"
        constraints = [
            models.UniqueConstraint(
                fields=["from_currency", "to_currency"],
                name="unique_currency_pair"
            )
        ]
        indexes = [
            models.Index(
                fields=["from_currency", "to_currency"],
                name="exchange_rate_pair_idx"
            ),
        ]

    def __str__(self):
        return f"{self.from_currency} → {self.to_currency}: {self.rate}"


# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    role = models.CharField(max_length=20)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["username"], name="users_username_idx"),
            models.Index(fields=["email"], name="users_email_idx"),
        ]

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        """
        Always return True for authenticated users from the JWT token.
        This is required for Django REST Framework's IsAuthenticated permission class.
        """
        return True


class Supplier(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "supplier"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["lastname", "firstname"]
        indexes = [
            models.Index(fields=["lastname", "firstname"], name="supplier_name_idx"),
            models.Index(fields=["phone"], name="supplier_phone_idx"),
            models.Index(fields=["is_active"], name="supplier_active_idx"),
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Client(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=25, unique=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "client"
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["lastname", "firstname"]
        indexes = [
            models.Index(fields=["lastname", "firstname"], name="client_name_idx"),
            models.Index(fields=["phone"], name="client_phone_idx"),
            models.Index(fields=["city"], name="client_city_idx"),
            models.Index(fields=["is_active"], name="client_active_idx"),
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Account(models.Model):
    account_name = models.CharField(max_length=50)
    account_type = models.CharField(max_length=20, choices=AccountType.CHOICES)
    currency = models.CharField(max_length=3, choices=Currency.CHOICES)
    current_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ["account_type", "currency"]
        constraints = [
            models.UniqueConstraint(
                fields=["account_type", "currency"], name="unique_account_type_currency"
            )
        ]
        indexes = [
            models.Index(
                fields=["account_type", "currency"], name="account_type_curr_idx"
            ),
        ]

    def __str__(self):
        return f"{self.account_name} ({self.currency})"


class Transaction(models.Model):
    transaction_type = models.CharField(max_length=20, choices=TransactionType.CHOICES)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.CHOICES)
    status = models.CharField(max_length=20, choices=TransactionStatus.CHOICES, default=TransactionStatus.PENDING)
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "transaction"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["transaction_type"], name="trans_type_idx"),
            models.Index(fields=["status"], name="trans_status_idx"),
            models.Index(fields=["invoice_number"], name="trans_invoice_idx"),
            models.Index(fields=["-created_date"], name="trans_created_idx"),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.invoice_number or self.id}"


class Payment(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="payments"
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)  # Amount in transaction currency
    currency = models.CharField(max_length=3, choices=Currency.CHOICES)  # Transaction currency
    # Original payment details (before currency conversion)
    original_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    original_currency = models.CharField(max_length=3, choices=Currency.CHOICES, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)  # Rate used for conversion
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["payment_method"], name="payment_method_idx"),
            models.Index(fields=["-payment_date"], name="payment_date_idx"),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency}"


class AccountTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER", "Transfer"),
    ]

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="account_transactions"
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    balance_after = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "accounttransaction"
        verbose_name = "Account Transaction"
        verbose_name_plural = "Account Transactions"
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["transaction_type"], name="acct_trans_type_idx"),
            models.Index(fields=["-transaction_date"], name="acct_trans_date_idx"),
        ]

    def __str__(self):
        return (
            f"{self.transaction_type} - {self.amount} (Balance: {self.balance_after})"
        )


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField(default=True)  # Soft delete flag

    class Meta:
        db_table = "product"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_product_name")
        ]
        indexes = [
            models.Index(fields=["category"], name="product_category_idx"),
            models.Index(fields=["name"], name="product_name_idx"),
            models.Index(fields=["is_active"], name="product_active_idx"),
        ]

    def __str__(self):
        return self.name


class Inventory(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    restock_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory"
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory"
        ordering = ["-restock_date"]
        indexes = [
            models.Index(fields=["-restock_date"], name="inventory_date_idx"),
        ]

    def __str__(self):
        return f"{self.id},{self.prod}, {self.quantity}, {self.restock_date}"


class Product_Categories(models.Model):
    category_name = models.CharField(max_length=50)

    class Meta:
        db_table = "product_categories"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


class Product_Names(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Product_Categories, on_delete=models.CASCADE, related_name="product_names"
    )

    class Meta:
        db_table = "product_names"
        verbose_name = "Product Name"
        verbose_name_plural = "Product Names"
        ordering = ["product_name"]

    def __str__(self):
        return f"{self.product_name}, {self.category}"


class Sales(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="sales"
    )
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    prod_price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sales")
    quantity = models.IntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "sales"
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ["-sale_date"]
        indexes = [
            models.Index(fields=["-sale_date"], name="sales_date_idx"),
        ]

    def __str__(self):
        return f"{self.prod}, {self.user}, {self.quantity}, {self.sale_date}"


class Restock(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="restocks"
    )
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="restocks")
    quantity = models.IntegerField()
    restock_price = models.DecimalField(max_digits=8, decimal_places=2)
    restock_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "restock"
        verbose_name = "Restock"
        verbose_name_plural = "Restocks"
        ordering = ["-restock_date"]
        indexes = [
            models.Index(fields=["-restock_date"], name="restock_date_idx"),
        ]

    def __str__(self):
        return (
            f"{self.prod}, {self.quantity}, {self.restock_price}, {self.restock_date}"
        )
