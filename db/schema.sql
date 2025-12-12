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

-- Insert Transactions (both PURCHASE from suppliers and SALE to clients)
INSERT INTO Transaction (transaction_type, supplier_id, client_id, total_amount, currency, status, invoice_number, notes, completed_date) VALUES 
('PURCHASE', 1, NULL, 1500.00, 'EUR', 'COMPLETED', 'PUR-2025-001', 'Purchase of fresh salmon and koce', '2025-11-20 10:30:00'),
('PURCHASE', 2, NULL, 800.00, 'EUR', 'PARTIAL', 'PUR-2025-002', 'Purchase of seafood assortment', NULL),
('PURCHASE', 3, NULL, 2000.00, 'LEK', 'COMPLETED', 'PUR-2025-003', 'Bulk purchase wild fish', '2025-11-22 14:15:00'),
('SALE', NULL, 1, 500.00, 'EUR', 'COMPLETED', 'SAL-2025-001', 'Sale to Ledjo Lleshaj', '2025-11-23 09:00:00'),
('SALE', NULL, 2, 750.00, 'EUR', 'PARTIAL', 'SAL-2025-002', 'Sale to Kristjan Gjinaj', NULL),
('SALE', NULL, 1, 300.00, 'USD', 'COMPLETED', 'SAL-2025-003', 'Additional sale to Ledjo', '2025-11-25 11:30:00');

-- Insert Payments (linked to transactions)
INSERT INTO Payment (transaction_id, account_id, amount, currency, payment_method, notes) VALUES 
-- Payments for transaction 1 (PURCHASE, completed)
(1, 4, 1500.00, 'EUR', 'CARD', 'Full payment for PUR-2025-001'),
-- Payments for transaction 2 (PURCHASE, partial)
(2, 1, 400.00, 'EUR', 'CASH', 'Partial payment for PUR-2025-002'),
-- Payments for transaction 3 (PURCHASE, completed)
(3, 6, 2000.00, 'LEK', 'CARD', 'Full payment for PUR-2025-003'),
-- Payments for transaction 4 (SALE, completed)
(4, 1, 500.00, 'EUR', 'CASH', 'Full payment from client Ledjo'),
-- Payments for transaction 5 (SALE, partial)
(5, 4, 400.00, 'EUR', 'CARD', 'Partial payment from client Kristjan'),
-- Payments for transaction 6 (SALE, completed)
(6, 2, 300.00, 'USD', 'CASH', 'Payment from Ledjo in USD');

-- Insert Account Transactions (track all money movements)
INSERT INTO AccountTransaction (account_id, payment_id, transaction_type, amount, balance_after, notes) VALUES 
-- Cash EUR account movements
(1, 4, 'DEPOSIT', 500.00, 5500.00, 'Received payment from sale SAL-2025-001'),
(1, 2, 'WITHDRAWAL', 400.00, 5100.00, 'Payment to supplier for PUR-2025-002'),
-- Cash USD account movements
(2, 6, 'DEPOSIT', 300.00, 3300.00, 'Received payment from sale SAL-2025-003'),
-- Bank EUR account movements
(4, 5, 'DEPOSIT', 400.00, 25400.00, 'Received partial payment from client'),
(4, 1, 'WITHDRAWAL', 1500.00, 23900.00, 'Payment to supplier for PUR-2025-001'),
-- Bank ALL account movements
(6, 3, 'WITHDRAWAL', 2000.00, 498000.00, 'Payment to supplier for PUR-2025-003'),
-- Additional deposits (initial capital)
(1, NULL, 'DEPOSIT', 5000.00, 5000.00, 'Initial cash deposit EUR'),
(2, NULL, 'DEPOSIT', 3000.00, 3000.00, 'Initial cash deposit USD'),
(3, NULL, 'DEPOSIT', 150000.00, 150000.00, 'Initial cash deposit LEK'),
(4, NULL, 'DEPOSIT', 25000.00, 25000.00, 'Initial bank deposit EUR'),
(5, NULL, 'DEPOSIT', 15000.00, 15000.00, 'Initial bank deposit USD'),
(6, NULL, 'DEPOSIT', 500000.00, 500000.00, 'Initial bank deposit LEK');

-- Sales data linked to transactions
INSERT INTO Sales (transaction_id, prod_id, prod_price, user_id, quantity) VALUES 
-- Sales for transaction 4 (SAL-2025-001, completed)
(4, 1, 10.00, 1, 20),
(4, 3, 20.00, 1, 15),
-- Sales for transaction 5 (SAL-2025-002, partial payment)
(5, 2, 15.00, 1, 30),
(5, 7, 8.00, 1, 40),
-- Sales for transaction 6 (SAL-2025-003, completed)
(6, 5, 30.00, 1, 10);

-- Insert Restock data (linked to Transaction records)
INSERT INTO Restock (transaction_id, prod_id, quantity, restock_price) VALUES 
-- Restocks for transaction 1 (PUR-2025-001)
(1, 1, 50, 450.00),  -- Salmon restock
(1, 3, 30, 550.00),  -- Koce restock
(1, 8, 10, 240.00),  -- Gafforre restock
(1, 11, 8, 240.00),  -- Peshkaqen restock
-- Restocks for transaction 2 (PUR-2025-002, partial payment)
(2, 2, 20, 280.00),  -- Karkaleca restock
(2, 4, 40, 120.00),  -- Midhje restock
(2, 9, 35, 590.00),  -- Kallamar restock
-- Restocks for transaction 3 (PUR-2025-003)
(3, 5, 15, 420.00),  -- Peshk i eger restock
(3, 6, 60, 660.00),  -- Peshk restock
(3, 7, 25, 180.00),  -- Fruta Deti restock
(3, 10, 20, 400.00); -- Sepie restock

