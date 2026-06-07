-- DROP DATABASE IF EXISTS erp_db;
-- postresql

-- CREATE DATABASE erp_db;

\connect erp_db;

CREATE TABLE Users   (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Suppliers/Producers table (must be created before Transaction)
CREATE TABLE Supplier (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    phone VARCHAR(25),
    email VARCHAR(100),
    address VARCHAR(150) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL
);

CREATE INDEX supplier_active_idx ON Supplier(is_active);

-- Clients table (must be created before Transaction)
CREATE TABLE Client (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(25) UNIQUE NOT NULL,
    address VARCHAR(150) NOT NULL,
    city VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL
);

CREATE INDEX client_active_idx ON Client(is_active);

-- Account types (where money is stored)
CREATE TABLE Account (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(50) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('CASH', 'BANK')),
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')),
    current_balance DECIMAL(8, 2) DEFAULT 0.00,
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
-- Note: Restock prices are TOTAL COST, not per-kg. E.g., 50 Salmon at 450 EUR total = 9 EUR/kg purchase price
CREATE TABLE Transaction (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('PURCHASE', 'SALE')),
    -- PURCHASE = buying from supplier (money OUT)
    -- SALE = selling to client (money IN)
    
    supplier_id INTEGER REFERENCES Supplier(id) ON DELETE SET NULL,
    client_id INTEGER REFERENCES Client(id) ON DELETE SET NULL,
    
    total_amount DECIMAL(8, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')), -- LEK is Albanian Lek
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PARTIAL', 'COMPLETED', 'CANCELLED')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_date TIMESTAMP,
    invoice_number VARCHAR(50),
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
    amount DECIMAL(8, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'LEK')),
    -- Original payment details (before currency conversion)
    original_amount DECIMAL(8, 2),
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
    amount DECIMAL(8, 2) NOT NULL,
    balance_after DECIMAL(8, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL, --has table with possible names
    category VARCHAR(50) NOT NULL, --has table with possible categories
    price DECIMAL(8, 2) NOT NULL, -- price per kg
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL -- soft delete flag
);

CREATE TABLE Product_Categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Product_Names (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE NOT NULL,
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
    prod_price DECIMAL(8, 2) NOT NULL,
    user_id INT NOT NULL,
    quantity INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (prod_id) REFERENCES Product(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Restock (
    id SERIAL PRIMARY KEY,
    transaction_id INT NOT NULL REFERENCES Transaction(id) ON DELETE CASCADE,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_price DECIMAL(8, 2) NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);


-- =====================================================================================
-- INDEXES FOR QUERY OPTIMIZATION
-- These indexes match those defined in Django models.py for consistency
-- =====================================================================================

-- Users indexes
CREATE INDEX users_username_idx ON Users(username);
CREATE INDEX users_email_idx ON Users(email);

-- Supplier indexes
CREATE INDEX supplier_name_idx ON Supplier(lastname, firstname);
CREATE INDEX supplier_phone_idx ON Supplier(phone);

-- Client indexes
CREATE INDEX client_name_idx ON Client(lastname, firstname);
CREATE INDEX client_phone_idx ON Client(phone);
CREATE INDEX client_city_idx ON Client(city);

-- Account indexes
CREATE INDEX account_type_curr_idx ON Account(account_type, currency);

-- Transaction indexes
CREATE INDEX trans_type_idx ON Transaction(transaction_type);
CREATE INDEX trans_status_idx ON Transaction(status);
CREATE INDEX trans_invoice_idx ON Transaction(invoice_number);
CREATE INDEX trans_created_idx ON Transaction(created_date DESC);

-- Payment indexes
CREATE INDEX payment_method_idx ON Payment(payment_method);
CREATE INDEX payment_date_idx ON Payment(payment_date DESC);

-- AccountTransaction indexes
CREATE INDEX acct_trans_type_idx ON AccountTransaction(transaction_type);
CREATE INDEX acct_trans_date_idx ON AccountTransaction(transaction_date DESC);

-- Product indexes
CREATE INDEX product_category_idx ON Product(category);
CREATE INDEX product_name_idx ON Product(name);
CREATE INDEX product_active_idx ON Product(is_active);

-- Inventory indexes
CREATE INDEX inventory_date_idx ON Inventory(restock_date DESC);

-- Sales indexes (FK indexes auto-created by PostgreSQL)
CREATE INDEX sales_date_idx ON Sales(sale_date DESC);

-- Restock indexes (FK indexes auto-created by PostgreSQL)
CREATE INDEX restock_date_idx ON Restock(restock_date DESC);

-- =====================================================================================
-- PERFORMANCE INDEXES (Essential only)
-- These target the most common query patterns for debt tracking and payments
-- =====================================================================================

-- For client debt queries (finding unpaid transactions per client)
CREATE INDEX trans_client_status_idx ON Transaction(client_id, status);

-- For payment lookup by transaction (used in debt calculations)
CREATE INDEX payment_transaction_idx ON Payment(transaction_id);

-- Partial index: Only unpaid transactions (smaller, faster for debt queries)
CREATE INDEX trans_unpaid_idx ON Transaction(client_id, total_amount) 
WHERE status IN ('PENDING', 'PARTIAL');


-- Inserting data
INSERT INTO Users (username, password, email, firstname, lastname, role) VALUES ('admin', 'pbkdf2_sha256$870000$tympSs6asDt7DTV4Wyq2kt$/8MfeLLr5m6C+keQIonZhKzJmtsV2doXFl641T9pS1U=', 'admin@example.com', 'Admin', 'User', 'admin');
-- INSERT INTO Client (firstname, lastname, email, phone, address, city) VALUES ('Ledjo', 'Lleshaj', 'ledjo@erp_db.com', '0123456789', 'Rruga e Dajlani', 'Durres'), ('Kristjan', 'Gjinaj', 'Kristjan@erp_db.com', '1234567890', 'Rruga e Dajlani', 'Tirane');
INSERT INTO Product_Categories (category_name) VALUES ('Peshk'), ('Fruta Deti'), ('Gafforre'), ('Kallamar'), ('Midhje'),('Karkaleca'),('Peshk i eger');
INSERT INTO Product_Names (product_name, category_id) VALUES 
('Salmon',1),('Karkaleca',5),('Koce',1),('Midhje',
5),('Peshk i eger',1),('Peshk',1),('Fruta Deti',2),('Gafforre',3),('Kallamar',4),('Karkaleca te vegjel',6),('Peshkaqen',7);

-- Insert Suppliers
-- INSERT INTO Supplier (firstname, lastname, phone, email, address) VALUES 
-- ('Arben', 'Hoxha', '+355 69 123 4567', 'arben.hoxha@supplier.al', 'Rruga e Kavajes, Durres'),
-- ('Endrit', 'Kola', '+355 69 234 5678', 'endrit.kola@seafood.al', 'Rruga Pavarsia, Vlore'),
-- ('Sokol', 'Muca', '+355 69 345 6789', 'sokol.muca@fishmarket.al', 'Rruga e Portit, Sarande');

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

