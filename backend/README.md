# Selita Fish - Backend

This is the backend API for the Selita Fish application, built with Django and Django REST Framework. It provides a comprehensive RESTful API for managing users, suppliers, clients, accounts, transactions, payments, inventory, sales, and reports.

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
cd selita-fish/backend
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
DB_NAME=selita_fish
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
