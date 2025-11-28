from django.contrib import admin
from .models import (
    Users,
    Supplier,
    Client,
    Account,
    Transaction,
    Payment,
    AccountTransaction,
    Product,
    Product_Categories,
    Product_Names,
    Inventory,
    Sales,
    Restock,
)


# ======== USERS ========
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'firstname', 'lastname', 'role')
    search_fields = ('username', 'email', 'firstname', 'lastname')
    list_filter = ('role',)


# ======== SUPPLIERS ========
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'phone', 'email', 'address')
    search_fields = ('firstname', 'lastname', 'phone', 'email')
    list_filter = ('address',)


# ======== CLIENTS ========
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'phone', 'email', 'city')
    search_fields = ('firstname', 'lastname', 'phone', 'email')
    list_filter = ('city',)


# ======== ACCOUNTS ========
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_name', 'account_type', 'currency', 'current_balance', 'created_date')
    search_fields = ('account_name',)
    list_filter = ('account_type', 'currency', 'created_date')
    readonly_fields = ('created_date',)


# ======== TRANSACTIONS ========
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'invoice_number', 'total_amount', 'currency', 'status', 'created_date')
    search_fields = ('invoice_number',)
    list_filter = ('transaction_type', 'status', 'currency', 'created_date')
    readonly_fields = ('created_date',)


# ======== PAYMENTS ========
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'account', 'amount', 'currency', 'payment_method', 'payment_date')
    search_fields = ('transaction__invoice_number',)
    list_filter = ('payment_method', 'currency', 'payment_date')
    readonly_fields = ('payment_date',)


# ======== ACCOUNT TRANSACTIONS ========
@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'transaction_type', 'amount', 'balance_after', 'transaction_date')
    search_fields = ('account__account_name',)
    list_filter = ('transaction_type', 'transaction_date')
    readonly_fields = ('transaction_date',)


# ======== PRODUCTS ========
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'description')
    search_fields = ('name', 'category')
    list_filter = ('category',)


# ======== PRODUCT CATEGORIES ========
@admin.register(Product_Categories)
class ProductCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name')
    search_fields = ('category_name',)


# ======== PRODUCT NAMES ========
@admin.register(Product_Names)
class ProductNamesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'category')
    search_fields = ('product_name',)
    list_filter = ('category',)


# ======== INVENTORY ========
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'prod', 'quantity', 'restock_date')
    search_fields = ('prod__name',)
    list_filter = ('restock_date',)
    readonly_fields = ('restock_date',)


# ======== SALES ========
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'prod', 'client', 'quantity', 'prod_price', 'is_paid', 'sale_date')
    search_fields = ('prod__name', 'client__firstname', 'client__lastname')
    list_filter = ('is_paid', 'sale_date')
    readonly_fields = ('sale_date',)


# ======== RESTOCKS ========
@admin.register(Restock)
class RestockAdmin(admin.ModelAdmin):
    list_display = ('id', 'prod', 'quantity', 'restock_price', 'payment', 'restock_date')
    search_fields = ('prod__name',)
    list_filter = ('restock_date',)
    readonly_fields = ('restock_date',)
