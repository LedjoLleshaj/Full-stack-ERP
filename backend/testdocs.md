# Unit Test Plan - Selita Fish Backend

This document tracks the unit testing campaign for the `backend/selita` application.

---

## Summary

**Total API Modules**: 14  
**Total Models**: 11  
**Existing Test Files**: 5

### Existing Tests

- [test_models.py](file:///backend/selita/tests/unit/test_models.py) - Client, Product, Category, Sale, Inventory (partial)
- [test_serializers.py](file:///backend/selita/tests/unit/test_serializers.py)
- [test_auth.py](file:///backend/selita/tests/api/test_auth.py)
- [test_clients.py](file:///backend/selita/tests/api/test_clients.py)
- [test_sales_workflow.py](file:///backend/selita/tests/integration/test_sales_workflow.py)

---

## Unit Tests - Models

> [!NOTE]
> Location: `backend/selita/tests/unit/models/`

### ExchangeRate Model
- [x] Test creation with valid currency pairs
- [x] Test unique constraint on currency pairs
- [x] Test rate precision (6 decimal places)
- [x] Test `__str__` method
- [x] Test `last_updated` auto-update
- [x] Test all currency pair combinations
- [x] Test rate update

### Users Model
- [x] Test user creation
- [x] Test `is_authenticated` property
- [x] Test `__str__` method
- [x] Test ordering (newest first)
- [x] Test user update

### Supplier Model
- [x] Test supplier creation
- [x] Test optional fields (phone, email)
- [x] Test `__str__` method
- [x] Test ordering (lastname, firstname)
- [x] Test supplier update

### Client Model
- [x] Test client creation
- [x] Test unique email/phone constraints
- [x] Test `__str__` method
- [x] Test optional email field
- [x] Test ordering (lastname, firstname)

### Account Model
- [x] Test account creation (CASH/BANK types)
- [x] Test unique constraint on account_type + currency
- [x] Test default balance (0.00)
- [x] Test `__str__` method
- [x] Test ordering (account_type, currency)

### Transaction Model
- [x] Test transaction creation (PURCHASE/SALE)
- [x] Test status choices (PENDING, PARTIAL, COMPLETED, CANCELLED)
- [x] Test default status is PENDING
- [x] Test `__str__` method (with/without invoice)
- [x] Test ordering (-created_date)

### Payment Model
- [x] Test payment creation
- [x] Test payment method choices (CASH/CARD)
- [x] Test currency conversion fields
- [x] Test `__str__` method
- [x] Test ordering (-payment_date)

### AccountTransaction Model
- [x] Test creation (DEPOSIT, WITHDRAWAL, TRANSFER)
- [x] Test balance tracking
- [x] Test related payment link
- [x] Test `__str__` method
- [x] Test ordering (-transaction_date)
- [x] Test optional payment field

### Product Model
- [x] Test product creation
- [x] Test unique name constraint
- [x] Test price precision
- [x] Test `__str__` method
- [x] Test ordering (category, name)

### Inventory Model
- [x] Test inventory creation
- [x] Test product relationship
- [x] Test quantity tracking
- [x] Test `__str__` method
- [x] Test ordering (-restock_date)

### Restock Model
- [x] Test restock creation
- [x] Test transaction relationship
- [x] Test price per unit tracking
- [x] Test `__str__` method
- [x] Test ordering (-restock_date)

### Sales Model
- [x] Test sale creation
- [x] Test transaction relationship
- [x] Test product price at time of sale
- [x] Test `__str__` method
- [x] Test ordering (-sale_date)

---

## Unit Tests - Serializers

> [!NOTE]
> Location: `backend/selita/tests/unit/serializers/`

- [x] ClientSerializer tests (serialization, deserialization, validation)
- [x] ProductSerializer tests (serialization, deserialization)
- [x] SupplierSerializer tests (serialization, deserialization)
- [x] AccountSerializer tests (serialization, read-only fields)
- [x] TransactionSerializer tests (serialization)
- [x] PaymentSerializer tests (serialization)
- [x] UserSerializer tests (serialization)
- [x] SalesSerializer tests (serialization, read-only date)
- [x] InventorySerializer tests (serialization, read-only date)
- [x] RestockSerializer tests (serialization, read-only date)

---

## API Tests - Endpoints

> [!NOTE]
> Location: `backend/selita/tests/api/`

### Auth API (`auth.py`)
- [x] Test login with valid credentials
- [x] Test login with invalid credentials
- [x] Test login with missing fields
- [x] Test logout
- [x] Test token refresh

### Clients API (`clients.py`)
- [x] Test `getClients` - list all clients with unpaid balance
- [x] Test `getClient` - single client with totals
- [x] Test `addClient` - create new client
- [x] Test `addClient` - validation errors
- [x] Test `updateClient` - modify client data
- [x] Test `updateClient` - client not found
- [x] Test `deleteClient` - remove client
- [x] Test `getClientSales` - sales history
- [x] Test unauthenticated access

### Suppliers API (`suppliers.py`)
- [x] Test `getSuppliers` - list all suppliers
- [x] Test `getSupplier` - single supplier
- [x] Test `getSupplier` - not found
- [x] Test `addSupplier` - create supplier
- [x] Test `updateSupplier` - modify supplier
- [x] Test `updateSupplier` - not found
- [x] Test `deleteSupplier` - remove supplier
- [x] Test `deleteSupplier` - not found

### Products API (`products.py`)
- [x] Test `getProducts` - list all products
- [x] Test `getProduct` - single product
- [x] Test `getProduct` - not found
- [x] Test `addProduct` - create product
- [x] Test `updatePrice` - modify price
- [x] Test `getProductCategories` - list categories
- [x] Test `getProductNames` - list product names
- [x] Test `getProductsByCategory` - filter by category
- [x] Test `getProductByName` - find by name
- [x] Test `checkDisponibility` - inventory check

### Accounts API (`accounts.py`)
- [x] Test `getAccounts` - list all accounts
- [x] Test `getAccount` - single account
- [x] Test `getAccount` - not found
- [x] Test `addAccount` - create account
- [x] Test `updateAccount` - modify account
- [x] Test `deleteAccount` - remove account
- [x] Test `deleteAccount` - not found

### Transactions API (`transactions.py`)
- [x] Test `getTransactions` - list all
- [x] Test `getTransaction` - single transaction
- [x] Test `getTransaction` - not found
- [x] Test `getTransactionPayments` - list payments
- [x] Test `addTransaction` - create transaction
- [x] Test `updateTransaction` - modify transaction
- [x] Test `deleteTransaction` - remove transaction
- [x] Test `deleteTransaction` - not found

### Inventory API (`inventory.py`)
- [x] Test `getInventory` - list inventory
- [x] Test `getProductsFromInventory` - with product details
- [x] Test `addProductToInventory` - restock flow

### Sales API (`sales.py`)
- [x] Test `getSales` - list all sales
- [x] Test `getSale` - single sale
- [x] Test `getSale` - not found
- [x] Test `getSaleDetails` - full sale with payments
- [x] Test `getProductsFromSales` - products info
- [x] Test `getUsersFromSales` - users info
- [x] Test `createSale` - paid sale flow
- [x] Test `createSale` - unpaid sale (debt)
- [x] Test `paySale` - payment
- [x] Test `getLastSoldPrice` - last price for product/client

### Reports API (`reports.py`)
- [x] Test `dashboard-stats` - dashboard statistics
- [x] Test `daily-profit` - daily profit data
- [x] Test `paid-vs-unpaid` - paid vs unpaid stats
- [x] Test `top-products` - top products
- [x] Test `profit-by-category` - profit by category
- [x] Test `top-clients` - top clients
- [x] Test `report/sales/` - sales report
- [x] Test `report/sales/` - with date filter

### Payments API (`payments.py`)
- [x] Test `getPayments` - list all payments
- [x] Test `getPayment` - single payment details
- [x] Test `getPayment` - not found
- [x] Test `addPayment` - create payment
- [x] Test `updatePayment` - modify payment
- [x] Test `deletePayment` - remove payment
- [x] Test `deletePayment` - not found

### Reports API (additional coverage)
- [x] Test `sales_report` - date range filtering
- [x] Test `sales_report` - CSV export format
- [x] Test `dashboard_stats` - totals calculation
- [x] Test `daily_profit` - 30 day profit data
- [x] Test `paid_vs_unpaid` - payment status breakdown
- [x] Test `top_products` - by quantity sold
- [x] Test `profit_by_category` - category profit calc
- [x] Test `top_clients` - by purchase amount

### Exchange Rates API (`exchange_rates.py`)
- [x] Test get exchange rates
- [x] Test get single exchange rate
- [x] Test exchange rate not found
- [x] Test convert currency

### Restocks API (`restocks.py`)
- [x] Test get restocks list
- [x] Test get single restock
- [x] Test restock not found
- [x] Test add restock
- [x] Test update restock
- [x] Test delete restock
- [x] Test delete restock not found

### Users API (`users.py`)
- [x] Test get users list
- [x] Test get single user
- [x] Test user not found
- [x] Test create user
- [x] Test update user
- [x] Test delete user
- [x] Test delete user not found

### Account Transactions API (`account_transactions.py`)
- [x] Test list account transactions
- [x] Test get single account transaction
- [x] Test account transaction not found
- [x] Test get transactions by account
- [x] Test add account transaction
- [x] Test delete account transaction
- [x] Test delete account transaction not found

---

## Integration Tests

> [!NOTE]
> Location: `backend/selita/tests/integration/`

### Sales Workflow (Existing)
- [x] Basic sales workflow test

### Additional Integration Tests
- [ ] Complete purchase-to-sale flow
- [ ] Debt payment workflow
- [ ] Multi-currency transaction flow
- [ ] Inventory restock with supplier

---

## Run Tests Command

```bash
cd /home/ledjo/Desktop/selita-fish/backend
python manage.py test selita.tests
```

### Run Specific Test Categories

```bash
# Unit tests only
python manage.py test selita.tests.unit

# API tests only
python manage.py test selita.tests.api

# Integration tests only
python manage.py test selita.tests.integration
```
