# ERP System - Backend

This is the backend API for the ERP System application, built with Django and Django REST Framework. It provides a comprehensive RESTful API for managing users, suppliers, clients, accounts, transactions, payments, inventory, sales, and reports.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Authentication](#authentication)
- [Admin Panel](#admin-panel)
- [Currency Exchange System](#-currency-exchange-system)
- [Multi-Currency Payments](#-multi-currency-payments)

## ✨ Features

- **Full CRUD Operations** for 13 models (Users, Clients, Suppliers, Products, etc.)
- **JWT Authentication** (Access & Refresh tokens)
- **Role-Based Access Control**
- **Automatic Inventory Management** (Restocks update inventory)
- **Financial Tracking** (Accounts, Transactions, Payments)
- **Reporting** (Sales reports)
- **Django Admin Interface** for easy data management

## 🛠 Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional, for database)

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd erp/backend
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

You can use the provided Docker Compose file to start a PostgreSQL instance:

```bash
cd ../db
docker-compose up -d
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend` directory (copy from `.env.example` if available):

```bash
# Django Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True

# Database Configuration
DB_NAME=erp_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=0.0.0.0
DB_PORT=5432

# JWT Configuration
ALGORITHM=HS256
```

### 6. Run Migrations

Apply the database migrations to create the schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (for Admin)

```bash
python manage.py createsuperuser
```

## ▶️ Running the Application

Start the development server:

```bash
python manage.py runserver 0.0.0.0:8080
```

The API will be available at `http://localhost:8080`.

## 📚 API Documentation

The API is organized by resource type. All endpoints are prefixed with the base URL (e.g., `http://localhost:8080/`).

### Authentication

- `POST /api/token/` - Obtain Access & Refresh tokens
- `POST /api/token/refresh/` - Refresh Access token
- `POST /login` - Custom login endpoint

### Users

- `GET /users` - List all users
- `GET /user/<id>` - Get user details
- `POST /create-user` - Create new user
- `PUT /update-user/<id>` - Update user
- `DELETE /delete-user/<id>` - Delete user

### Suppliers

- `GET /suppliers` - List all suppliers
- `GET /supplier/<id>` - Get supplier details
- `POST /add-supplier` - Add new supplier
- `PUT /update-supplier/<id>` - Update supplier
- `DELETE /delete-supplier/<id>` - Delete supplier

### Clients

- `GET /clients` - List all clients
- `GET /client/<id>` - Get client details
- `GET /client-sales/<id>` - Get sales for a client
- `POST /add-client` - Add new client
- `PUT /update-client/<id>` - Update client
- `DELETE /delete-client/<id>` - Delete client

### Accounts

- `GET /accounts` - List all accounts
- `GET /account/<id>` - Get account details (includes recent transactions)
- `POST /add-account` - Add new account
- `PUT /update-account/<id>` - Update account
- `DELETE /delete-account/<id>` - Delete account

### Transactions

- `GET /transactions` - List transactions (filter by `?type=PURCHASE` or `?type=SALE`)
- `GET /transaction/<id>` - Get transaction details
- `GET /transaction-payments/<id>` - Get payments for a transaction
- `POST /add-transaction` - Add new transaction
- `PUT /update-transaction/<id>` - Update transaction
- `DELETE /delete-transaction/<id>` - Delete transaction

### Payments

- `GET /payments` - List all payments
- `GET /payment/<id>` - Get payment details
- `POST /add-payment` - Add new payment
- `PUT /update-payment/<id>` - Update payment
- `DELETE /delete-payment/<id>` - Delete payment

### Account Transactions

- `GET /account-transactions` - List account transactions
- `GET /account-transaction/<id>` - Get details
- `POST /add-account-transaction` - Add transaction (updates account balance)
- `DELETE /delete-account-transaction/<id>` - Delete transaction

### Products

- `GET /products` - List all products
- `GET /product/<id>` - Get product details
- `POST /add-product` - Add new product
- `PUT /update-price/<id>` - Update product price
- `GET /product-categories` - List categories
- `GET /productbycategory/<category>` - Filter by category

### Inventory

- `GET /inventory` - List inventory
- `POST /update-inventory` - Manually update inventory

### Sales

- `GET /sales` - List all sales
- `GET /sale/<id>` - Get sale details
- `POST /create-sale` - Create new sale
- `POST /pay-sale/<id>` - Mark sale as paid

### Restocks

- `GET /restocks` - List restocks
- `GET /restock/<id>` - Get restock details
- `POST /add-restock` - Add restock (automatically updates inventory)
- `PUT /update-restock/<id>` - Update restock
- `DELETE /delete-restock/<id>` - Delete restock

### Reports

- `GET /report/sales/` - Generate sales report

## 🗄 Database Models

The application uses the following main models:

1. **Users**: System users (Admins, Staff)
2. **Supplier**: Product suppliers
3. **Client**: Customers
4. **Account**: Financial accounts (Bank, Cash)
5. **Transaction**: Purchases and Sales records
6. **Payment**: Payments linked to transactions and accounts
7. **AccountTransaction**: Money movement in accounts
8. **Product**: Items for sale
9. **Inventory**: Stock levels
10. **Sales**: Sales records linked to clients and products
11. **Restock**: Inventory replenishment records

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

- Include the token in the header: `Authorization: Bearer <your_access_token>`
- Tokens expire after a set time (configurable in `.env`).
- Use the refresh token to get a new access token without re-logging in.

## 👑 Admin Panel

Django provides a built-in Admin Interface to manage all data.

- URL: `http://localhost:8080/admin`
- Login with the superuser credentials created during setup.
- Features: Search, Filter, Add, Edit, and Delete records for all models.

---

## 💱 Currency Exchange System

The application supports multi-currency transactions with automatic currency conversion for payments.

### Supported Currencies

- **EUR** - Euro
- **USD** - US Dollar  
- **LEK** - Albanian Lek

### Exchange Rate Storage

Exchange rates are stored in the `ExchangeRate` model with the following fields:
- `from_currency` - Source currency code
- `to_currency` - Target currency code
- `rate` - Conversion rate
- `last_updated` - Timestamp of last update

### Syncing Exchange Rates

Rates are fetched from [ExchangeRate-API](https://www.exchangerate-api.com/) and should be synced **weekly**.

```bash
# Sync exchange rates from API
python manage.py sync_exchange_rates

# Preview changes without updating (dry run)
python manage.py sync_exchange_rates --dry-run
```

> **Note:** The API uses "ALL" as the currency code for Albanian Lek (ISO 4217 standard), but the system stores it as "LEK" for user-friendliness. The sync command handles this mapping automatically.

### Automatic Rate Sync (No Cron Required)

The application automatically syncs exchange rates on startup if:
- No rates exist in the database, OR
- Rates are older than 7 days

This is handled in `erp/apps.py` and runs in a background thread 5 seconds after Django starts, so it doesn't block the server startup.

**Console output when rates are synced:**
```
[ExchangeRate] Rates are stale (last updated: 2025-12-10 10:30:00). Syncing...
Fetching exchange rates...
Currency mapping: LEK (database) <-> ALL (API)
  ✓ EUR (EUR) rates fetched
  ✓ USD (USD) rates fetched  
  ✓ LEK (ALL) rates fetched
Exchange rates synchronized: 9 created, 0 updated
[ExchangeRate] Sync complete!
```

**To force a manual sync:**
```bash
python manage.py sync_exchange_rates
```
### Exchange Rate API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/exchange-rates` | GET | Get all exchange rates |
| `/exchange-rate/<from>/<to>` | GET | Get specific rate (e.g., `/exchange-rate/EUR/LEK`) |
| `/convert-currency` | POST | Convert an amount between currencies |

**Example - Convert Currency:**
```json
POST /convert-currency
{
    "amount": 100.00,
    "from_currency": "EUR",
    "to_currency": "LEK"
}

Response:
{
    "original_amount": 100.00,
    "converted_amount": 9537.35,
    "from_currency": "EUR",
    "to_currency": "LEK",
    "rate": 95.3735,
    "last_updated": "2025-12-18T00:00:00Z"
}
```

---

## 💳 Multi-Currency Payments

The system allows paying for sales in a different currency than the transaction currency.

### How It Works

1. **Sale created in EUR** (e.g., 350 EUR total)
2. **Customer pays in LEK** (e.g., 33,380 LEK)
3. **System converts** payment to transaction currency using stored exchange rate
4. **Balance updated** in transaction currency

### Payment Flow (Backend)

When `POST /pay-sale/<id>` is called with a different currency:

1. Fetches exchange rate: `payment_currency → transaction_currency`
2. Converts payment amount: `amount × rate = converted_amount`
3. Validates: `converted_amount ≤ remaining_balance + 0.01` (tolerance for rounding)
4. Creates payment record with converted amount
5. Updates transaction status:
   - **COMPLETED** if remaining ≤ 0.01
   - **PARTIAL** if remaining > 0.01

### Example

```json
POST /pay-sale/3
{
    "amount": 33380.73,
    "currency": "LEK",
    "payment_method": "CASH",
    "notes": "Payment from customer"
}

Response:
{
    "message": "Payment added successfully",
    "payment_id": 5,
    "transaction_status": "COMPLETED",
    "total_paid": 350.00,
    "remaining": 0.00,
    "payment_amount": 33380.73,
    "payment_currency": "LEK",
    "converted_amount": 349.99,
    "transaction_currency": "EUR"
}
```

### Payment Notes

When paying in a different currency, the payment notes automatically include the original amount and exchange rate used:

```
"Original note (Paid: 33380.73 LEK, Rate: 0.0104)"
```

### Frontend Integration

The Sale Details View component (`/sale/:id`) provides:

1. **Currency selector** - Choose payment currency (LEK, EUR, USD)
2. **Live rate display** - Shows current exchange rate when currency differs
3. **Automatic conversion** - Shows equivalent amount in both currencies
4. **Max amount button** - Auto-fills maximum payable amount in selected currency
5. **Partial payments** - Enter any amount up to the maximum

**Flow:**
1. User opens sale details
2. Clicks "Shto Pagesë" (Add Payment)
3. Selects payment currency
4. Exchange rate is fetched and displayed
5. Amount auto-fills to max remaining (converted)
6. User can reduce for partial payment
7. Shows conversion preview: `9,600 LEK → 100 EUR`
8. Submit payment
