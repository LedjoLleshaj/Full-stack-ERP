# Selita Fish Database

This directory contains the database schema and configuration for the Selita Fish application. The project uses **PostgreSQL** as the relational database management system.

## 🚀 How to Run

The database is containerized using Docker. To start the database:

```bash
docker-compose up -d
```

### Access Credentials
- **Host**: `localhost` (or `db` if accessing from another container)
- **Port**: `5432`
- **Database Name**: `selita_fish`
- **Username**: `REDACTED`
- **Password**: `REDACTED`

> **Note:** If port `5432` is already in use on your host machine, you may need to stop the existing service:
> ```bash
> sudo fuser -k 5432/tcp
> ```

## 🗄️ Database Schema

The database consists of the following tables designed to manage the fish market's operations, including inventory, sales, and financial tracking.

### Core Entities
- **`Users`**: System users (Admins, Staff) with role-based access.
- **`Supplier`**: External entities from whom products are purchased.
- **`Client`**: Customers to whom products are sold.

### Product & Inventory Management
- **`Product`**: The main product catalog (e.g., Salmon, Koce).
- **`Product_Categories`**: Categories for products (e.g., Peshk, Fruta Deti).
- **`Product_Names`**: Pre-defined names for products linked to categories.
- **`Inventory`**: Tracks current stock levels for each product.
- **`Restock`**: Logs inventory replenishment events, linked to payments.

### Financial Management
- **`Account`**: Financial accounts (Cash or Bank) in different currencies (EUR, USD, ALL).
- **`Transaction`**: Records of all financial exchanges.
  - Types: `PURCHASE` (from Supplier) or `SALE` (to Client).
  - Statuses: `PENDING`, `PARTIAL`, `COMPLETED`, `CANCELLED`.
- **`Payment`**: Individual payments linked to a specific Transaction and Account.
- **`AccountTransaction`**: A ledger of all money movements (Deposits, Withdrawals, Transfers) affecting account balances.
- **`Sales`**: Records of product sales to clients, linked to Users and Products.

## 🔗 Relationships

- **Transactions** link to either a **Supplier** (for purchases) or a **Client** (for sales).
- **Payments** belong to a **Transaction** and are made from/to a specific **Account**.
- **Restocks** are linked to a **Product** and a **Payment** (cost of goods).
- **Sales** are linked to a **Product**, **Client**, and the **User** who processed the sale.
- **Inventory** is updated based on **Restocks** (in) and **Sales** (out).

## 📝 Initial Data

The schema includes initial seed data for:
- Default Admin User
- Sample Clients and Suppliers
- Product Categories and Names
- Initial Inventory and Sales history
- Default Accounts (Cash/Bank in EUR, USD, ALL) with initial balances
