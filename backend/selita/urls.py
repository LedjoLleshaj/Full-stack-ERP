from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import (
    auth, 
    users, 
    clients, 
    products, 
    inventory, 
    sales, 
    reports,
    suppliers,
    accounts,
    transactions,
    payments,
    account_transactions,
    restocks,
)


urlpatterns = [
    # ======== AUTHENTICATION ========
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"), # Disabled in favor of cookie auth
    path("api/token/refresh/", auth.refresh_token_view, name="token_refresh"),
    path("login", auth.login),
    path("logout", auth.logout_view),
    
    # ======== USERS ========
    path("users", users.getUsers),
    path("user/<str:pk>", users.getUser),
    path("create-user", users.createUser),
    path("update-user/<str:pk>", users.updateUser),
    path("delete-user/<str:pk>", users.deleteUser),
    
    # ======== SUPPLIERS ========
    path("suppliers", suppliers.getSuppliers),
    path("supplier/<str:pk>", suppliers.getSupplier),
    path("add-supplier", suppliers.addSupplier),
    path("update-supplier/<str:pk>", suppliers.updateSupplier),
    path("delete-supplier/<str:pk>", suppliers.deleteSupplier),
    
    # ======== CLIENTS ========
    path("clients", clients.getClients),
    path("client/<str:pk>", clients.getClient),
    path("client-sales/<str:pk>", clients.getClientSales),
    path("add-client", clients.addClient),
    path("update-client/<str:pk>", clients.updateClient),
    path("delete-client/<str:pk>", clients.deleteClient),
    
    # ======== ACCOUNTS ========
    path("accounts", accounts.getAccounts),
    path("account/<str:pk>", accounts.getAccount),
    path("add-account", accounts.addAccount),
    path("update-account/<str:pk>", accounts.updateAccount),
    path("delete-account/<str:pk>", accounts.deleteAccount),
    
    # ======== TRANSACTIONS ========
    path("transactions", transactions.getTransactions),
    path("transaction/<str:pk>", transactions.getTransaction),
    path("transaction-payments/<str:pk>", transactions.getTransactionPayments),
    path("add-transaction", transactions.addTransaction),
    path("update-transaction/<str:pk>", transactions.updateTransaction),
    path("delete-transaction/<str:pk>", transactions.deleteTransaction),
    
    # ======== PAYMENTS ========
    path("payments", payments.getPayments),
    path("payment/<str:pk>", payments.getPayment),
    path("add-payment", payments.addPayment),
    path("update-payment/<str:pk>", payments.updatePayment),
    path("delete-payment/<str:pk>", payments.deletePayment),
    
    # ======== ACCOUNT TRANSACTIONS ========
    path("account-transactions", account_transactions.getAccountTransactions),
    path("account-transaction/<str:pk>", account_transactions.getAccountTransaction),
    path("account-transactions/account/<str:account_id>", account_transactions.getTransactionsByAccount),
    path("add-account-transaction", account_transactions.addAccountTransaction),
    path("delete-account-transaction/<str:pk>", account_transactions.deleteAccountTransaction),
    
    # ======== PRODUCTS ========
    path("products", products.getProducts),
    path("product/<str:pk>", products.getProduct),
    path("add-product", products.addProduct),
    path("update-price/<str:pk>", products.updatePrice),
    path("product-categories", products.getProductCategories),
    path("product-names", products.getProductNames),
    path("productbycategory/<str:category>", products.getProductsByCategory),
    path("productbyname/<str:name>", products.getProductByName),
    path("filterbycategories", products.filterByCategories),
    path("checkdisponibility/<str:pk>", products.checkDisponibility),
    
    # ======== INVENTORY ========
    path("inventory", inventory.getInventory),
    path("productsfrominventory", inventory.getProductsFromInventory),
    path("update-inventory", inventory.addProductToInventory),
    
    # ======== SALES ========
    path("sales", sales.getSales),
    path("sale/<str:pk>", sales.getSale),
    path("salesinfo", sales.getProductsFromSales),
    path("usersfromsales", sales.getUsersFromSales),
    path("create-sale", sales.createSale),
    path("pay-sale/<str:pk>", sales.paySale),
    path("last-sold-price", sales.getLastSoldPrice),
    
    # ======== RESTOCKS ========
    path("restocks", restocks.getRestocks),
    path("restock/<str:pk>", restocks.getRestock),
    path("add-restock", restocks.addRestock),
    path("update-restock/<str:pk>", restocks.updateRestock),
    path("delete-restock/<str:pk>", restocks.deleteRestock),
    
    # ======== REPORTS ========
    path("report/sales/", reports.sales_report),
    path("dashboard-stats", reports.dashboard_stats),
]
