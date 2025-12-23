-- DROP DATABASE IF EXISTS selita_fish;
-- postresql

-- CREATE DATABASE selita_fish;

\connect selita_fish;

CREATE TABLE Users   (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);

-- Suppliers/Producers table (must be created before Transaction)
CREATE TABLE Supplier (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    address VARCHAR(255) NOT NULL
);

-- Clients table (must be created before Transaction)
CREATE TABLE Client (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(255) UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
);

-- Account types (where money is stored)
CREATE TABLE Account (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('CASH', 'BANK')),
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')),
    current_balance DECIMAL(10, 2) DEFAULT 0.00,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(account_type, currency) -- One cash account per currency, one bank per currency
);

-- Exchange rates table (synced weekly from external API)
CREATE TABLE exchange_rate (
    id SERIAL PRIMARY KEY,
    from_currency VARCHAR(3) NOT NULL CHECK (from_currency IN ('EUR', 'USD', 'LEK')),
    to_currency VARCHAR(3) NOT NULL CHECK (to_currency IN ('EUR', 'USD', 'LEK')),
    rate DECIMAL(12, 6) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_currency, to_currency)
);

-- Create index for faster rate lookups
CREATE INDEX exchange_rate_pair_idx ON exchange_rate(from_currency, to_currency);

-- Main transaction table (purchases from suppliers or sales to clients)
CREATE TABLE Transaction (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('PURCHASE', 'SALE')),
    -- PURCHASE = buying from supplier (money OUT)
    -- SALE = selling to client (money IN)
    
    supplier_id INTEGER REFERENCES Supplier(id) ON DELETE SET NULL,
    client_id INTEGER REFERENCES Client(id) ON DELETE SET NULL,
    
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')), -- LEK is Albanian Lek
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PARTIAL', 'COMPLETED', 'CANCELLED')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_date TIMESTAMP,
    invoice_number VARCHAR(100),
    notes TEXT,
    
    -- Ensure only one of supplier_id or client_id is set
    CONSTRAINT check_transaction_party CHECK (
        (transaction_type = 'PURCHASE' AND supplier_id IS NOT NULL AND client_id IS NULL) OR
        (transaction_type = 'SALE' AND client_id IS NOT NULL AND supplier_id IS NULL)
    )
);

-- Individual payments that can be linked to one transaction
CREATE TABLE Payment (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES Transaction(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES Account(id), -- Which account was used
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')),
    -- Original payment details (before currency conversion)
    original_amount DECIMAL(10, 2),
    original_currency VARCHAR(3) CHECK (original_currency IN ('EUR', 'USD', 'LEK')),
    exchange_rate DECIMAL(12, 6),  -- Rate used for conversion
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('CASH', 'CARD')),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Account transactions log (all money movements) - must be after Payment
CREATE TABLE AccountTransaction (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES Account(id) ON DELETE CASCADE,
    payment_id INTEGER REFERENCES Payment(id) ON DELETE SET NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER')),
    amount DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL, --has table with possible names
    category VARCHAR(255) NOT NULL, --has table with possible categories
    price DECIMAL(10, 2) NOT NULL, -- price per kg
    description TEXT NOT NULL
);

CREATE TABLE Product_Categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Product_Names (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) UNIQUE NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Product_Categories(id)
);

CREATE TABLE Inventory (
    id SERIAL PRIMARY KEY,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);

CREATE TABLE Sales (
    id SERIAL PRIMARY KEY,
    transaction_id INT NOT NULL REFERENCES Transaction(id) ON DELETE CASCADE,
    prod_id INT NOT NULL,
    prod_price DECIMAL(10, 2) NOT NULL,
    user_id INT NOT NULL,
    quantity INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Restock (
    id SERIAL PRIMARY KEY,
    transaction_id INT NOT NULL REFERENCES Transaction(id) ON DELETE CASCADE,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_price DECIMAL(10, 2) NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);


-- Inserting data
INSERT INTO Users (username, password, email, firstname, lastname, role) VALUES ('adminselita', 'pbkdf2_sha256$870000$tympSs6asDt7DTV4Wyq2kt$/8MfeLLr5m6C+keQIonZhKzJmtsV2doXFl641T9pS1U=', 'admin@selita_fish.com', 'Admin', 'Selita', 'admin');
INSERT INTO Client (firstname, lastname, email, phone, address, city) VALUES ('Ledjo', 'Lleshaj', 'ledjo@selita_fish.com', '0123456789', 'Rruga e Dajlani', 'Durres'), ('Kristjan', 'Gjinaj', 'Kristjan@selita_fish.com', '1234567890', 'Rruga e Dajlani', 'Tirane');
INSERT INTO Product_Categories (category_name) VALUES ('Peshk'), ('Fruta Deti'), ('Gafforre'), ('Kallamar'), ('Midhje'),('Karkaleca'),('Peshk i eger');
INSERT INTO Product_Names (product_name, category_id) VALUES 
('Salmon',1),('Karkaleca',5),('Koce',1),('Midhje',
5),('Peshk i eger',1),('Peshk',1),('Fruta Deti',2),('Gafforre',3),('Kallamar',4),('Karkaleca te vegjel',6),('Peshkaqen',7);
INSERT INTO Product (name, category, price, description) VALUES 
('Salmon', 'Peshk', 10.00, 'Peshk Salmon'),
('Karkaleca', 'Fruta Deti', 15.00, 'Karkaleca nga Mesdheu'),
('Koce', 'Peshk', 20.00, 'Peshk Koce'),
('Midhje', 'Fruta Deti', 5.00, 'Midhje nga Adriatiku'),
('Peshk i eger', 'Peshk i eger', 30.00, 'Pesh i eger nga Adriatiku'),
('Peshk', 'Peshk', 12.00, 'Peshk nga Adriatiku'),
('Fruta Deti', 'Fruta Deti', 8.00, 'Fruta deti nga Adriatiku'),
('Gafforre', 'Gafforre', 25.00, 'Gaffore nga Adriatiku'),
('Kallamar', 'Kallamar', 18.00, 'Kallamar nga Adriatiku'),
('Sepie', 'Fruta Deti', 22.00, 'Sepie nga Adriatiku'),
('Peshkaqen', 'Peshk i eger', 35.00, 'Pesh i eger nga Mesdheu');
INSERT INTO Inventory (prod_id, quantity) VALUES 
(1, 10), (2, 15), (3, 20), (4, 5), (5, 30), (6, 50), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10);

-- Insert Suppliers
INSERT INTO Supplier (firstname, lastname, phone, email, address) VALUES 
('Arben', 'Hoxha', '+355 69 123 4567', 'arben.hoxha@supplier.al', 'Rruga e Kavajes, Durres'),
('Endrit', 'Kola', '+355 69 234 5678', 'endrit.kola@seafood.al', 'Rruga Pavarsia, Vlore'),
('Sokol', 'Muca', '+355 69 345 6789', 'sokol.muca@fishmarket.al', 'Rruga e Portit, Sarande');

-- =====================================================================================
-- CRITICAL: REQUIRED ACCOUNT RECORDS - DO NOT DELETE!
-- These 6 accounts are NECESSARY for the payment system to function.
-- The backend auto-selects the correct account based on payment_method and currency:
--   - CASH payment → CASH account
--   - CARD payment → BANK account
-- Each combination of (CASH/BANK) × (EUR/USD/LEK) must exist.
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

-- Insert Transactions (both PURCHASE from suppliers and SALE to clients)
-- Note: Restock prices are TOTAL COST, not per-kg. E.g., 50 Salmon at 450 EUR total = 9 EUR/kg purchase price
INSERT INTO Transaction (transaction_type, supplier_id, client_id, total_amount, currency, status, invoice_number, notes, completed_date) VALUES 
-- PURCHASES (restocks from suppliers) - restock_price is the TOTAL cost for that restock line
('PURCHASE', 1, NULL, 1480.00, 'EUR', 'COMPLETED', 'PUR-2025-001', 'Purchase of fresh salmon, koce, gafforre, peshkaqen', '2025-11-20 10:30:00'),
('PURCHASE', 2, NULL, 990.00, 'EUR', 'PARTIAL', 'PUR-2025-002', 'Purchase of seafood assortment', NULL),
('PURCHASE', 3, NULL, 1660.00, 'EUR', 'COMPLETED', 'PUR-2025-003', 'Bulk purchase wild fish and seafood', '2025-11-22 14:15:00'),
-- SALES to clients - more realistic amounts to generate positive profit
('SALE', NULL, 1, 1250.00, 'EUR', 'COMPLETED', 'SAL-2025-001', 'Sale to Ledjo Lleshaj - large order', '2025-11-23 09:00:00'),
('SALE', NULL, 2, 980.00, 'EUR', 'COMPLETED', 'SAL-2025-002', 'Sale to Kristjan Gjinaj', '2025-11-24 10:00:00'),
('SALE', NULL, 1, 650.00, 'EUR', 'COMPLETED', 'SAL-2025-003', 'Additional sale to Ledjo', '2025-11-25 11:30:00'),
('SALE', NULL, 2, 420.00, 'EUR', 'PARTIAL', 'SAL-2025-004', 'Small order Kristjan - partial payment', NULL),
('SALE', NULL, 1, 890.00, 'EUR', 'COMPLETED', 'SAL-2025-005', 'Weekend order for Ledjo', '2025-11-26 09:00:00'),
('SALE', NULL, 2, 560.00, 'EUR', 'COMPLETED', 'SAL-2025-006', 'Weekly order Kristjan', '2025-11-27 14:00:00');

-- Insert Payments (linked to transactions)
INSERT INTO Payment (transaction_id, account_id, amount, currency, payment_method, notes) VALUES 
-- Payments for transaction 1 (PURCHASE, completed)
(1, 4, 1480.00, 'EUR', 'CARD', 'Full payment for PUR-2025-001'),
-- Payments for transaction 2 (PURCHASE, partial - 500 of 990 paid)
(2, 1, 500.00, 'EUR', 'CASH', 'Partial payment for PUR-2025-002'),
-- Payments for transaction 3 (PURCHASE, completed)
(3, 4, 1660.00, 'EUR', 'CARD', 'Full payment for PUR-2025-003'),
-- Payments for transaction 4 (SALE, completed)
(4, 1, 1250.00, 'EUR', 'CASH', 'Full payment from client Ledjo'),
-- Payments for transaction 5 (SALE, completed)
(5, 4, 980.00, 'EUR', 'CARD', 'Full payment from client Kristjan'),
-- Payments for transaction 6 (SALE, completed)
(6, 1, 650.00, 'EUR', 'CASH', 'Full payment from Ledjo'),
-- Payments for transaction 7 (SALE, partial - 200 of 420 paid)
(7, 1, 200.00, 'EUR', 'CASH', 'Partial payment from Kristjan'),
-- Payments for transaction 8 (SALE, completed)
(8, 4, 890.00, 'EUR', 'CARD', 'Full payment from Ledjo'),
-- Payments for transaction 9 (SALE, completed)
(9, 1, 560.00, 'EUR', 'CASH', 'Full payment from Kristjan');

-- Insert Account Transactions (track all money movements)
INSERT INTO AccountTransaction (account_id, payment_id, transaction_type, amount, balance_after, notes) VALUES 
-- Initial deposits (capital)
(1, NULL, 'DEPOSIT', 5000.00, 5000.00, 'Initial cash deposit EUR'),
(2, NULL, 'DEPOSIT', 3000.00, 3000.00, 'Initial cash deposit USD'),
(3, NULL, 'DEPOSIT', 150000.00, 150000.00, 'Initial cash deposit LEK'),
(4, NULL, 'DEPOSIT', 25000.00, 25000.00, 'Initial bank deposit EUR'),
(5, NULL, 'DEPOSIT', 15000.00, 15000.00, 'Initial bank deposit USD'),
(6, NULL, 'DEPOSIT', 500000.00, 500000.00, 'Initial bank deposit LEK'),
-- Cash EUR movements
(1, 4, 'DEPOSIT', 1250.00, 6250.00, 'Received payment from sale SAL-2025-001'),
(1, 2, 'WITHDRAWAL', 500.00, 5750.00, 'Payment to supplier for PUR-2025-002'),
(1, 6, 'DEPOSIT', 650.00, 6400.00, 'Received payment from sale SAL-2025-003'),
(1, 7, 'DEPOSIT', 200.00, 6600.00, 'Partial payment from sale SAL-2025-004'),
(1, 9, 'DEPOSIT', 560.00, 7160.00, 'Payment from sale SAL-2025-006'),
-- Bank EUR movements
(4, 1, 'WITHDRAWAL', 1480.00, 23520.00, 'Payment to supplier for PUR-2025-001'),
(4, 3, 'WITHDRAWAL', 1660.00, 21860.00, 'Payment to supplier for PUR-2025-003'),
(4, 5, 'DEPOSIT', 980.00, 22840.00, 'Received payment from client Kristjan'),
(4, 8, 'DEPOSIT', 890.00, 23730.00, 'Received payment from Ledjo');

-- Sales data linked to transactions
-- Prices are per-kg selling prices (higher than purchase per-kg price for profit)
INSERT INTO Sales (transaction_id, prod_id, prod_price, user_id, quantity) VALUES 
-- Sales for transaction 4 (SAL-2025-001: 1250 EUR) - Salmon (50kg@12) + Koce (30kg@22) + Gafforre (5kg@28)
(4, 1, 12.00, 1, 50),   -- Salmon: 50kg × 12 EUR = 600 EUR
(4, 3, 22.00, 1, 25),   -- Koce: 25kg × 22 EUR = 550 EUR
(4, 8, 20.00, 1, 5),    -- Gafforre: 5kg × 20 EUR = 100 EUR (total: 1250 EUR)
-- Sales for transaction 5 (SAL-2025-002: 980 EUR)
(5, 2, 17.00, 1, 20),   -- Karkaleca: 20kg × 17 EUR = 340 EUR
(5, 7, 10.00, 1, 40),   -- Fruta Deti: 40kg × 10 EUR = 400 EUR
(5, 9, 20.00, 1, 12),   -- Kallamar: 12kg × 20 EUR = 240 EUR (total: 980 EUR)
-- Sales for transaction 6 (SAL-2025-003: 650 EUR)
(6, 5, 35.00, 1, 10),   -- Peshk i eger: 10kg × 35 EUR = 350 EUR
(6, 6, 15.00, 1, 20),   -- Peshk: 20kg × 15 EUR = 300 EUR (total: 650 EUR)
-- Sales for transaction 7 (SAL-2025-004: 420 EUR, partial payment)
(7, 4, 7.00, 1, 30),    -- Midhje: 30kg × 7 EUR = 210 EUR
(7, 10, 26.00, 1, 8),   -- Sepie: 8kg × 26 EUR = 208 EUR (total: 418 EUR ≈ 420)
-- Sales for transaction 8 (SAL-2025-005: 890 EUR)
(8, 1, 12.00, 1, 30),   -- Salmon: 30kg × 12 EUR = 360 EUR
(8, 11, 38.00, 1, 8),   -- Peshkaqen: 8kg × 38 EUR = 304 EUR
(8, 8, 28.00, 1, 8),    -- Gafforre: 8kg × 28 EUR = 224 EUR (total: 888 EUR ≈ 890)
-- Sales for transaction 9 (SAL-2025-006: 560 EUR)
(9, 6, 15.00, 1, 25),   -- Peshk: 25kg × 15 EUR = 375 EUR
(9, 4, 7.00, 1, 15),    -- Midhje: 15kg × 7 EUR = 105 EUR
(9, 7, 10.00, 1, 8);    -- Fruta Deti: 8kg × 10 EUR = 80 EUR (total: 560 EUR)

-- Insert Restock data (linked to Transaction records)
-- restock_price is the PER-UNIT purchase price (per kg)
-- Total cost = restock_price × quantity
INSERT INTO Restock (transaction_id, prod_id, quantity, restock_price) VALUES 
-- Restocks for transaction 1 (PUR-2025-001: 1480 EUR total)
(1, 1, 50, 9.00),     -- Salmon: 50kg × 9 EUR/kg = 450 EUR (sells at 10-12 EUR/kg)
(1, 3, 30, 18.00),    -- Koce: 30kg × 18 EUR/kg = 540 EUR (sells at 20-22 EUR/kg)
(1, 8, 20, 20.00),    -- Gafforre: 20kg × 20 EUR/kg = 400 EUR (sells at 25-28 EUR/kg)
(1, 11, 10, 9.00),    -- Peshkaqen: 10kg × 9 EUR/kg = 90 EUR (sells at 35-38 EUR/kg)
-- Total: 450+540+400+90 = 1480 EUR ✓
-- Restocks for transaction 2 (PUR-2025-002: 990 EUR total, partial payment)
(2, 2, 30, 12.00),    -- Karkaleca: 30kg × 12 EUR/kg = 360 EUR (sells at 15-17 EUR/kg)
(2, 4, 50, 3.00),     -- Midhje: 50kg × 3 EUR/kg = 150 EUR (sells at 5-7 EUR/kg)
(2, 9, 40, 12.00),    -- Kallamar: 40kg × 12 EUR/kg = 480 EUR (sells at 18-20 EUR/kg)
-- Total: 360+150+480 = 990 EUR ✓
-- Restocks for transaction 3 (PUR-2025-003: 1660 EUR total)
(3, 5, 20, 20.00),    -- Peshk i eger: 20kg × 20 EUR/kg = 400 EUR (sells at 30-35 EUR/kg)
(3, 6, 80, 8.00),     -- Peshk: 80kg × 8 EUR/kg = 640 EUR (sells at 12-15 EUR/kg)
(3, 7, 60, 6.00),     -- Fruta Deti: 60kg × 6 EUR/kg = 360 EUR (sells at 8-10 EUR/kg)
(3, 10, 20, 13.00);   -- Sepie: 20kg × 13 EUR/kg = 260 EUR (sells at 22-26 EUR/kg)
-- Total: 400+640+360+260 = 1660 EUR ✓

