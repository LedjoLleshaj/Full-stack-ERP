from django.urls import path

from .api import (
    account_transactions,
    accounts,
    auth,
    clients,
    exchange_rates,
    health,
    inventory,
    invoices,
    payments,
    products,
    quotations,
    reports,
    restocks,
    sales,
    suppliers,
    transactions,
    users,
)

urlpatterns = [
    # ======== AUTHENTICATION ========
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"), # Disabled in favor of cookie auth
    path("api/token/refresh/", auth.refresh_token_view, name="token_refresh"),
    path("login", auth.login, name="login"),
    path("health/", health.health),
    path("logout", auth.logout_view, name="logout"),
    
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
    path("update-product/<str:pk>", products.updateProduct),
    path("delete-product/<str:pk>", products.deleteProduct),
    path("update-price/<str:pk>", products.updatePrice),
    path("product-categories", products.getProductCategories),
    path("product-names", products.getProductNames),
    path("add-product-category", products.addProductCategory),
    path("update-product-category/<str:pk>", products.updateProductCategory),
    path("delete-product-category/<str:pk>", products.deleteProductCategory),
    path("add-product-name", products.addProductName),
    path("update-product-name/<str:pk>", products.updateProductName),
    path("delete-product-name/<str:pk>", products.deleteProductName),
    path("productbycategory/<str:category>", products.getProductsByCategory),
    path("productbyname/<str:name>", products.getProductByName),
    path("filterbycategories", products.filterByCategories),
    path("checkdisponibility/<str:pk>", products.checkDisponibility),
    path("product-history/<str:pk>", products.getProductHistory),

    
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
    path("update-sale/<str:pk>", sales.updateSale),
    path("delete-sale/<str:pk>", sales.deleteSale),
    path("pay-sale/<str:pk>", sales.paySale),
    path("last-sold-price", sales.getLastSoldPrice),
    path("sale-details/<str:pk>", sales.getSaleDetails),
    
    # ======== RESTOCKS ========
    path("restocks", restocks.getRestocks),
    path("restock/<str:pk>", restocks.getRestock),
    path("add-restock", restocks.addRestock),
    path("update-restock/<str:pk>", restocks.updateRestock),
    path("delete-restock/<str:pk>", restocks.deleteRestock),
    path("restocks-by-supplier/<str:supplier_id>", restocks.getRestocksBySupplier),
    path("pay-restock/<str:pk>", restocks.payRestock),
    
    # ======== REPORTS ========
    path("report/sales/", reports.sales_report),
    path("dashboard-stats", reports.dashboard_stats),
    path("daily-profit", reports.daily_profit),
    path("paid-vs-unpaid", reports.paid_vs_unpaid),
    path("top-products", reports.top_products),
    path("profit-by-category", reports.profit_by_category),
    path("top-clients", reports.top_clients),
    
    # ======== INVOICES ========
    path("transaction/<str:pk>/invoice/", invoices.generate_invoice),

    # ======== QUOTATIONS ========
    path("quotations", quotations.list_quotations),
    path("quotation/<str:pk>", quotations.get_quotation),
    path("create-quotation", quotations.create_quotation),
    path("update-quotation/<str:pk>", quotations.update_quotation),
    path("delete-quotation/<str:pk>", quotations.delete_quotation),
    path("quotation/<str:pk>/status", quotations.update_status),
    path("quotation/<str:pk>/convert", quotations.convert_to_sale),

    # ======== EXCHANGE RATES ========
    path("exchange-rates", exchange_rates.get_exchange_rates),
    path("exchange-rate/<str:from_currency>/<str:to_currency>", exchange_rates.get_exchange_rate),
    path("convert-currency", exchange_rates.convert_currency),
]
