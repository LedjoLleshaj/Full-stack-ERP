-- Database Cleanup Script for ERP System
-- This script wipes transactional data and dynamic master data while preserving system configuration.

-- 1. Wipe Transactional Data (Order matters for foreign keys)
TRUNCATE TABLE Sales CASCADE;
TRUNCATE TABLE Restock CASCADE;
TRUNCATE TABLE Inventory CASCADE;
TRUNCATE TABLE AccountTransaction CASCADE;
TRUNCATE TABLE Payment CASCADE;
TRUNCATE TABLE Transaction CASCADE;

-- 2. Wipe Dynamic Master Data
-- TRUNCATE TABLE Client CASCADE;
-- TRUNCATE TABLE Supplier CASCADE;
TRUNCATE TABLE Product CASCADE;

-- 3. Reset Account Balances
UPDATE Account SET current_balance = 0.00;

-- 4. Reset Sequences (for ID columns)
-- This ensures new records start from ID 1
ALTER SEQUENCE sales_id_seq RESTART WITH 1;
ALTER SEQUENCE restock_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;
ALTER SEQUENCE accounttransaction_id_seq RESTART WITH 1;
ALTER SEQUENCE payment_id_seq RESTART WITH 1;
ALTER SEQUENCE transaction_id_seq RESTART WITH 1;
-- ALTER SEQUENCE client_id_seq RESTART WITH 1;
-- ALTER SEQUENCE supplier_id_seq RESTART WITH 1;
ALTER SEQUENCE product_id_seq RESTART WITH 1;

-- NOTE: The following tables are PRESERVED:
-- - Users (admin access)
-- - Product_Categories (configuration)
-- - Product_Names (configuration)
-- - exchange_rate (synced data)
-- - Client (master data)
-- - Supplier (master data)
