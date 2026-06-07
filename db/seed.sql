-- Seed data for development. Schema is managed by Django migrations.
-- Load with: docker compose exec -T db psql -U postgres -d erp_db < db/seed.sql

-- Default admin user (password: admin)
INSERT INTO Users (username, password, email, firstname, lastname, role) VALUES ('admin', 'pbkdf2_sha256$870000$tympSs6asDt7DTV4Wyq2kt$/8MfeLLr5m6C+keQIonZhKzJmtsV2doXFl641T9pS1U=', 'admin@example.com', 'Admin', 'User', 'admin');

-- Product categories
INSERT INTO Product_Categories (category_name) VALUES ('Peshk'), ('Fruta Deti'), ('Gafforre'), ('Kallamar'), ('Midhje'),('Karkaleca'),('Peshk i eger');

-- Product names linked to categories
INSERT INTO Product_Names (product_name, category_id) VALUES
('Salmon',1),('Karkaleca',5),('Koce',1),('Midhje',
5),('Peshk i eger',1),('Peshk',1),('Fruta Deti',2),('Gafforre',3),('Kallamar',4),('Karkaleca te vegjel',6),('Peshkaqen',7);

-- =====================================================================================
-- CRITICAL: REQUIRED ACCOUNT RECORDS - DO NOT DELETE!
-- These 6 accounts are NECESSARY for the payment system to function.
-- The backend auto-selects the correct account based on payment_method and currency:
--   - CASH payment -> CASH account
--   - CARD payment -> BANK account
-- Each combination of (CASH/BANK) x (EUR/USD/LEK) must exist.
-- Without these records, creating paid sales will fail with error:
-- "No CASH/BANK account found for currency EUR/USD/LEK"
-- =====================================================================================
INSERT INTO Account (account_name, account_type, currency, current_balance, notes) VALUES
('Cash EUR', 'CASH', 'EUR', 0.00, 'Main cash account in Euros'),
('Cash USD', 'CASH', 'USD', 0.00, 'Cash account in US Dollars'),
('Cash LEK', 'CASH', 'LEK', 0.00, 'Cash account in Albanian Lek'),
('Bank EUR', 'BANK', 'EUR', 0.00, 'Bank account in Euros'),
('Bank USD', 'BANK', 'USD', 0.00, 'Bank account in US Dollars'),
('Bank LEK', 'BANK', 'LEK', 0.00, 'Bank account in Albanian Lek');

-- =====================================================================================
-- EXCHANGE RATES - Synced from ExchangeRate-API (Dec 2025)
-- These rates should be updated weekly using: python manage.py sync_exchange_rates
-- Rates are stored as from_currency -> to_currency conversions
-- =====================================================================================
INSERT INTO exchange_rate (from_currency, to_currency, rate) VALUES
-- EUR rates
('EUR', 'EUR', 1.000000),
('EUR', 'USD', 1.163900),
('EUR', 'LEK', 95.373500),
-- USD rates
('USD', 'EUR', 0.851900),
('USD', 'USD', 1.000000),
('USD', 'LEK', 82.234800),
-- LEK rates
('LEK', 'EUR', 0.010380),
('LEK', 'USD', 0.012160),
('LEK', 'LEK', 1.000000);
