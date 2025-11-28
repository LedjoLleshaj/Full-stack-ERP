from django.db import models


# Reusable choice constants
CURRENCY_CHOICES = [
    ('EUR', 'Euro'),
    ('USD', 'US Dollar'),
    ('ALL', 'Albanian Lek'),
]


# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['username'], name='users_username_idx'),
            models.Index(fields=['email'], name='users_email_idx'),
        ]

    def __str__(self):
        return self.username


class Supplier(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = "supplier"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['lastname', 'firstname']
        indexes = [
            models.Index(fields=['lastname', 'firstname'], name='supplier_name_idx'),
            models.Index(fields=['phone'], name='supplier_phone_idx'),
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Client(models.Model):
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)

    class Meta:
        db_table = "client"
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['lastname', 'firstname']
        indexes = [
            models.Index(fields=['lastname', 'firstname'], name='client_name_idx'),
            models.Index(fields=['phone'], name='client_phone_idx'),
            models.Index(fields=['city'], name='client_city_idx'),
        ]

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
    ]
    
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ['account_type', 'currency']
        constraints = [
            models.UniqueConstraint(fields=["account_type", "currency"], name="unique_account_type_currency")
        ]
        indexes = [
            models.Index(fields=['account_type', 'currency'], name='account_type_curr_idx'),
        ]

    def __str__(self):
        return f"{self.account_name} ({self.currency})"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "transaction"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['transaction_type'], name='trans_type_idx'),
            models.Index(fields=['status'], name='trans_status_idx'),
            models.Index(fields=['invoice_number'], name='trans_invoice_idx'),
            models.Index(fields=['-created_date'], name='trans_created_idx'),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.invoice_number or self.id}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_method'], name='payment_method_idx'),
            models.Index(fields=['-payment_date'], name='payment_date_idx'),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency}"


class AccountTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_transactions')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='account_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "accounttransaction"
        verbose_name = "Account Transaction"
        verbose_name_plural = "Account Transactions"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_type'], name='acct_trans_type_idx'),
            models.Index(fields=['-transaction_date'], name='acct_trans_date_idx'),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} (Balance: {self.balance_after})"


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    class Meta:
        db_table = "product"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_product_name")
        ]
        indexes = [
            models.Index(fields=['category'], name='product_category_idx'),
            models.Index(fields=['name'], name='product_name_idx'),
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
        ordering = ['-restock_date']
        indexes = [
            models.Index(fields=['-restock_date'], name='inventory_date_idx'),
        ]

    def __str__(self):
        return f"{self.id},{self.prod}, {self.quantity}, {self.restock_date}"


class Product_Categories(models.Model):
    category_name = models.CharField(max_length=200)

    class Meta:
        db_table = "product_categories"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['category_name']

    def __str__(self):
        return self.category_name


class Product_Names(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Product_Categories, on_delete=models.CASCADE, related_name='product_names')

    class Meta:
        db_table = "product_names"
        verbose_name = "Product Name"
        verbose_name_plural = "Product Names"
        ordering = ['product_name']

    def __str__(self):
        return f"{self.product_name}, {self.category}"


class Sales(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    prod_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sales')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sales"
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['is_paid'], name='sales_paid_idx'),
            models.Index(fields=['-sale_date'], name='sales_date_idx'),
        ]

    def __str__(self):
        return f"{self.prod}, {self.user}, {self.quantity}, {self.sale_date}"


class Restock(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='restocks')
    quantity = models.IntegerField()
    restock_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='restocks')
    restock_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "restock"
        verbose_name = "Restock"
        verbose_name_plural = "Restocks"
        ordering = ['-restock_date']
        indexes = [
            models.Index(fields=['-restock_date'], name='restock_date_idx'),
        ]

    def __str__(self):
        return f"{self.prod}, {self.quantity}, {self.restock_price}, {self.restock_date}"
