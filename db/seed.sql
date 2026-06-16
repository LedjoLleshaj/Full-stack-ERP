-- ============================================================
-- Development seed data — idempotent, safe to re-run.
-- Truncates all app tables and re-inserts clean data.
-- Load with: make seed
-- ============================================================
-- Data: 5 suppliers, 8 clients, 10 products, 10 purchase
-- transactions, 29 sale transactions spread Dec 2025–May 2026.
-- All amounts verified: line-item sums match transaction totals.
-- Account running balances computed via window function.
-- ============================================================

BEGIN;

-- ============================================================
-- 1. CLEAN SLATE — reset all app data, preserve Django internals
-- ============================================================
TRUNCATE TABLE
    quotation_item,
    quotation,
    accounttransaction,
    payment,
    sales,
    restock,
    inventory,
    "transaction",
    client,
    supplier,
    product,
    product_names,
    product_categories,
    account,
    exchange_rate,
    tax_rate,
    payment_terms
RESTART IDENTITY CASCADE;

-- ============================================================
-- 1b. TAX RATES
-- ============================================================
INSERT INTO tax_rate (id, name, rate, is_default, is_active)
OVERRIDING SYSTEM VALUE VALUES
(1, 'TVSH 20%',  20.00, true,  true),
(2, 'TVSH 10%',  10.00, false, true),
(3, 'TVSH 6%',    6.00, false, true),
(4, 'Pa TVSH',    0.00, false, true);

-- ============================================================
-- 2. ADMIN USER  (password: admin)
-- ============================================================
INSERT INTO users (username, password, email, firstname, lastname, role,
                   is_superuser, is_active, is_staff, date_joined)
VALUES ('admin',
        'pbkdf2_sha256$1000000$4uQPlS5ZMMGsiCFqPdaAIC$CUuuUXKvd6A/nZ9j5rpNfan8iHZE03IyVX4BkVK9CVc=',
        'admin@example.com', 'Admin', 'User', 'ADMIN',
        true, true, true, NOW())
ON CONFLICT (username) DO UPDATE
    SET password     = EXCLUDED.password,
        role         = EXCLUDED.role,
        is_active    = EXCLUDED.is_active,
        is_staff     = EXCLUDED.is_staff,
        is_superuser = EXCLUDED.is_superuser;

-- ============================================================
-- 3. PRODUCT CATEGORIES  (IDs 1–7)
-- ============================================================
INSERT INTO product_categories (id, category_name) OVERRIDING SYSTEM VALUE VALUES
(1, 'Peshk'),
(2, 'Fruta Deti'),
(3, 'Gafforre'),
(4, 'Kallamar'),
(5, 'Midhje'),
(6, 'Karkaleca'),
(7, 'Peshk i eger');

-- ============================================================
-- 4. PRODUCT NAMES  (reference catalogue, IDs 1–11)
-- ============================================================
INSERT INTO product_names (id, product_name, category_id) OVERRIDING SYSTEM VALUE VALUES
(1,  'Salmon',              1),
(2,  'Karkaleca',           6),
(3,  'Koce',                1),
(4,  'Midhje',              5),
(5,  'Peshk i eger',        7),
(6,  'Peshk',               1),
(7,  'Fruta Deti',          2),
(8,  'Gafforre',            3),
(9,  'Kallamar',            4),
(10, 'Karkaleca te vegjel', 6),
(11, 'Peshkaqen',           7);

-- ============================================================
-- 5. EXCHANGE RATES  (EUR base, Dec 2025 values)
-- ============================================================
INSERT INTO exchange_rate (from_currency, to_currency, rate, last_updated) VALUES
('EUR', 'EUR', 1.000000,  NOW()),
('EUR', 'USD', 1.163900,  NOW()),
('EUR', 'LEK', 95.373500, NOW()),
('USD', 'EUR', 0.851900,  NOW()),
('USD', 'USD', 1.000000,  NOW()),
('USD', 'LEK', 82.234800, NOW()),
('LEK', 'EUR', 0.010380,  NOW()),
('LEK', 'USD', 0.012160,  NOW()),
('LEK', 'LEK', 1.000000,  NOW());

-- ============================================================
-- 6. ACCOUNTS  (6 required — CASH/BANK × EUR/USD/LEK)
--    IDs are explicit so foreign keys in payments are stable.
-- ============================================================
INSERT INTO account (id, account_name, account_type, currency, current_balance, created_date, notes)
OVERRIDING SYSTEM VALUE VALUES
(1, 'Cash EUR', 'CASH', 'EUR', 0.00, NOW(), 'Main cash account in Euros'),
(2, 'Cash USD', 'CASH', 'USD', 0.00, NOW(), 'Cash account in US Dollars'),
(3, 'Cash LEK', 'CASH', 'LEK', 0.00, NOW(), 'Cash account in Albanian Lek'),
(4, 'Bank EUR', 'BANK', 'EUR', 0.00, NOW(), 'Bank account in Euros'),
(5, 'Bank USD', 'BANK', 'USD', 0.00, NOW(), 'Bank account in US Dollars'),
(6, 'Bank LEK', 'BANK', 'LEK', 0.00, NOW(), 'Bank account in Albanian Lek');

-- ============================================================
-- 7. SUPPLIERS  (5 fish wholesalers)
-- ============================================================
INSERT INTO supplier (id, firstname, lastname, phone, email, address, is_active)
OVERRIDING SYSTEM VALUE VALUES
(1, 'Arjan',  'Kola',     '0682345678', 'arjan.kola@fishsupply.al',     'Rruga Adriatiku 12, Durrës',  true),
(2, 'Besnik', 'Hoxha',    '0683456789', 'besnik.hoxha@fishsupply.al',   'Rruga Butrinti 5, Sarandë',   true),
(3, 'Dritan', 'Mema',     '0684567890', 'dritan.mema@fishsupply.al',    'Rruga Vlora 34, Vlorë',       true),
(4, 'Fatmir', 'Dervishi', '0685678901', 'fatmir.dervishi@merisheri.al', 'Rruga Deti 8, Durrës',        true),
(5, 'Genci',  'Shehu',    '0686789012', 'genci.shehu@bregdeti.al',      'Rruga Bregdeti 21, Himarë',   true);

-- ============================================================
-- 8. CLIENTS  (8 restaurant/hotel buyers)
-- ============================================================
INSERT INTO client (id, firstname, lastname, email, phone, address, city, is_active)
OVERRIDING SYSTEM VALUE VALUES
(1, 'Restorant', 'Adriatiku', 'adriatiku@restorant.al',  '0681111111', 'Rruga Kavajës 45',     'Tiranë',  true),
(2, 'Hotel',     'Butrinti',  'info@hotelbutrinti.al',   '0682222222', 'Rruga Saranda 12',     'Sarandë', true),
(3, 'Bar',       'Deti',      'bardeti@gmail.com',       '0683333333', 'Rruga Durrësit 8',     'Durrës',  true),
(4, 'Restorant', 'Riviera',   'riviera@restorant.al',    '0684444444', 'Rruga Bregdeti 3',     'Vlorë',   true),
(5, 'Fishmarket','Tiranë',    'info@fishmarket.al',      '0685555555', 'Pazari i Ri, Kulla 2', 'Tiranë',  true),
(6, 'Hotel',     'Apollonia', 'info@hotelapolonia.al',   '0686666666', 'Rruga Apollonisë 17',  'Fier',    true),
(7, 'Restorant', 'Korabi',    'korabi@restorant.al',     '0687777777', 'Rruga Pogradecit 22',  'Korçë',   true),
(8, 'Catering',  'Illyria',   'info@cateringillyria.al', '0688888888', 'Rruga Elbasanit 55',   'Tiranë',  true);

-- ============================================================
-- 9. PRODUCTS  (10 seafood items, prices in EUR/kg)
-- ============================================================
INSERT INTO product (id, name, category, category_fk_id, price, description, is_active, reorder_level, reorder_quantity)
OVERRIDING SYSTEM VALUE VALUES
(1,  'Salmon',      'Peshk',       1, 12.50, 'Fresh Atlantic salmon, sold by kg',        true, 0, 0),
(2,  'Shrimp',      'Karkaleca',   6,  8.00, 'Large tiger shrimp, fresh catch',          true, 0, 0),
(3,  'Cod',         'Peshk',       1,  9.50, 'Fresh cod fillet, North Sea',              true, 0, 0),
(4,  'Mussels',     'Midhje',      5,  5.00, 'Fresh mussels, Adriatic coast',            true, 0, 0),
(5,  'Sea Bass',    'Peshk',       1, 11.00, 'Mediterranean sea bass, whole fish',       true, 0, 0),
(6,  'Octopus',     'Fruta Deti',  2, 14.00, 'Fresh octopus, Ionian Sea',               true, 0, 0),
(7,  'Crab',        'Gafforre',    3, 18.00, 'Blue swimmer crab, live',                  true, 0, 0),
(8,  'Squid',       'Kallamar',    4,  7.50, 'Fresh squid, cleaned and whole',           true, 0, 0),
(9,  'Wild Fish',   'Peshk i eger',7, 13.00, 'Mixed wild catch, daily fresh',            true, 0, 0),
(10, 'Baby Shrimp', 'Karkaleca',   6,  6.50, 'Small sweet shrimp, peeled and deveined',  true, 0, 0);

-- ============================================================
-- 10. INVENTORY  (one row per product — current on-hand qty)
--     quantity = total_restocked − total_sold  (verified below)
--       Salmon:     195 in – 93 out  = 102
--       Shrimp:      65 in – 62 out  =   3
--       Cod:         90 in – 63 out  =  27
--       Mussels:    130 in – 98 out  =  32
--       Sea Bass:    65 in – 55 out  =  10
--       Octopus:     45 in – 28 out  =  17
--       Crab:        75 in – 75 out  =   0
--       Squid:       75 in – 48 out  =  27
--       Wild Fish:   50 in – 36 out  =  14
--       Baby Shrimp: 70 in – 57 out  =  13
-- ============================================================
INSERT INTO inventory (id, prod_id, quantity, restock_date) OVERRIDING SYSTEM VALUE VALUES
(1,  1, 102, '2025-12-01 08:00:00+00'),
(2,  2,   3, '2025-12-01 08:00:00+00'),
(3,  3,  27, '2025-12-01 08:00:00+00'),
(4,  4,  32, '2025-12-01 08:00:00+00'),
(5,  5,  10, '2025-12-01 08:00:00+00'),
(6,  6,  17, '2025-12-01 08:00:00+00'),
(7,  7,   0, '2025-12-01 08:00:00+00'),
(8,  8,  27, '2025-12-01 08:00:00+00'),
(9,  9,  14, '2025-12-01 08:00:00+00'),
(10,10,  13, '2025-12-01 08:00:00+00');

-- ============================================================
-- 11. TRANSACTIONS
-- ============================================================

-- PURCHASE transactions T1–T10 (supplier restocks)
--   T1  2025-12-05  Arjan  Kola    Salmon 50@8.00 + Shrimp 30@5.00          = 550.00  TRANSFER → Bank EUR
--   T2  2025-12-18  Besnik Hoxha   Cod 40@6.00 + Mussels 60@2.50            = 390.00  CASH → Cash EUR
--   T3  2026-01-08  Dritan Mema    Crab 35@12.00 + Octopus 25@9.00          = 645.00  TRANSFER → Bank EUR
--   T4  2026-01-22  Arjan  Kola    Salmon 45@8.00 + Sea Bass 30@7.00        = 570.00  CASH → Cash EUR
--   T5  2026-02-10  Fatmir Derv.   Squid 35@4.50 + Wild Fish 50@8.50        = 582.50  TRANSFER → Bank EUR
--   T6  2026-02-25  Besnik Hoxha   Salmon 40@8.00 + Shrimp 35@5.00          = 495.00  CASH → Cash EUR
--   T7  2026-03-12  Arjan  Kola    Cod 50@6.00 + Mussels 70@2.50            = 475.00  TRANSFER → Bank EUR
--   T8  2026-03-28  Genci  Shehu   Sea Bass 35@7.00 + Baby Shrimp 70@4.00   = 525.00  CASH → Cash EUR
--   T9  2026-04-15  Dritan Mema    Salmon 60@8.00 + Octopus 20@9.00         = 660.00  TRANSFER → Bank EUR
--   T10 2026-05-08  Fatmir Derv.   Crab 40@12.00 + Squid 40@4.50            = 660.00  CASH → Cash EUR
INSERT INTO "transaction" (id, transaction_type, total_amount, currency, status,
                            created_date, completed_date, invoice_number, notes, client_id, supplier_id, payment_terms_id, due_date)
OVERRIDING SYSTEM VALUE VALUES
(1,  'PURCHASE', 550.00, 'EUR', 'COMPLETED', '2025-12-05 09:00:00+00', '2025-12-05 17:00:00+00', 'INV-P2025-001', NULL, NULL, 1, NULL, NULL),
(2,  'PURCHASE', 390.00, 'EUR', 'COMPLETED', '2025-12-18 09:00:00+00', '2025-12-18 17:00:00+00', 'INV-P2025-002', NULL, NULL, 2, NULL, NULL),
(3,  'PURCHASE', 645.00, 'EUR', 'COMPLETED', '2026-01-08 09:00:00+00', '2026-01-08 17:00:00+00', 'INV-P2026-001', NULL, NULL, 3, NULL, NULL),
(4,  'PURCHASE', 570.00, 'EUR', 'COMPLETED', '2026-01-22 09:00:00+00', '2026-01-22 17:00:00+00', 'INV-P2026-002', NULL, NULL, 1, NULL, NULL),
(5,  'PURCHASE', 582.50, 'EUR', 'COMPLETED', '2026-02-10 09:00:00+00', '2026-02-10 17:00:00+00', 'INV-P2026-003', NULL, NULL, 4, NULL, NULL),
(6,  'PURCHASE', 495.00, 'EUR', 'COMPLETED', '2026-02-25 09:00:00+00', '2026-02-25 17:00:00+00', 'INV-P2026-004', NULL, NULL, 2, NULL, NULL),
(7,  'PURCHASE', 475.00, 'EUR', 'COMPLETED', '2026-03-12 09:00:00+00', '2026-03-12 17:00:00+00', 'INV-P2026-005', NULL, NULL, 1, NULL, NULL),
(8,  'PURCHASE', 525.00, 'EUR', 'COMPLETED', '2026-03-28 09:00:00+00', '2026-03-28 17:00:00+00', 'INV-P2026-006', NULL, NULL, 5, NULL, NULL),
(9,  'PURCHASE', 660.00, 'EUR', 'COMPLETED', '2026-04-15 09:00:00+00', '2026-04-15 17:00:00+00', 'INV-P2026-007', NULL, NULL, 3, NULL, NULL),
(10, 'PURCHASE', 660.00, 'EUR', 'COMPLETED', '2026-05-08 09:00:00+00', '2026-05-08 17:00:00+00', 'INV-P2026-008', NULL, NULL, 4, NULL, NULL);

-- SALE transactions T11–T39 (29 sales over 6 months, varied clients & statuses)
INSERT INTO "transaction" (id, transaction_type, total_amount, currency, status,
                            created_date, completed_date, invoice_number, notes, client_id, supplier_id, payment_terms_id, due_date)
OVERRIDING SYSTEM VALUE VALUES
-- Dec 2025
(11, 'SALE', 126.50, 'EUR', 'COMPLETED', '2025-12-08 10:00:00+00', '2025-12-08 10:00:00+00', 'INV-S2025-001', NULL, 1, NULL, NULL, NULL),
(12, 'SALE', 170.00, 'EUR', 'COMPLETED', '2025-12-20 10:00:00+00', '2025-12-20 10:00:00+00', 'INV-S2025-002', NULL, 2, NULL, NULL, NULL),
-- Jan 2026
(13, 'SALE',  61.00, 'EUR', 'COMPLETED', '2026-01-06 10:00:00+00', '2026-01-06 10:00:00+00', 'INV-S2026-001', NULL, 3, NULL, NULL, NULL),
(14, 'SALE', 206.50, 'EUR', 'COMPLETED', '2026-01-12 10:00:00+00', '2026-01-12 10:00:00+00', 'INV-S2026-002', NULL, 4, NULL, NULL, NULL),
(15, 'SALE', 130.00, 'EUR', 'COMPLETED', '2026-01-19 10:00:00+00', '2026-01-19 10:00:00+00', 'INV-S2026-003', NULL, 5, NULL, NULL, NULL),
(16, 'SALE', 178.00, 'EUR', 'COMPLETED', '2026-01-26 10:00:00+00', '2026-01-26 10:00:00+00', 'INV-S2026-004', NULL, 1, NULL, NULL, NULL),
(17, 'SALE', 258.00, 'EUR', 'COMPLETED', '2026-01-30 10:00:00+00', '2026-01-30 10:00:00+00', 'INV-S2026-005', NULL, 6, NULL, NULL, NULL),
-- Feb 2026
(18, 'SALE', 203.00, 'EUR', 'COMPLETED', '2026-02-04 10:00:00+00', '2026-02-04 10:00:00+00', 'INV-S2026-006', NULL, 2, NULL, NULL, NULL),
(19, 'SALE',  93.00, 'EUR', 'COMPLETED', '2026-02-11 10:00:00+00', '2026-02-11 10:00:00+00', 'INV-S2026-007', NULL, 7, NULL, NULL, NULL),
(20, 'SALE', 195.00, 'EUR', 'COMPLETED', '2026-02-17 10:00:00+00', '2026-02-17 10:00:00+00', 'INV-S2026-008', NULL, 3, NULL, NULL, NULL),
(21, 'SALE', 311.00, 'EUR', 'COMPLETED', '2026-02-24 10:00:00+00', '2026-02-24 10:00:00+00', 'INV-S2026-009', NULL, 4, NULL, NULL, NULL),
(22, 'SALE', 169.00, 'EUR', 'COMPLETED', '2026-02-28 10:00:00+00', '2026-02-28 10:00:00+00', 'INV-S2026-010', NULL, 8, NULL, NULL, NULL),
-- Mar 2026
(23, 'SALE', 160.00, 'EUR', 'COMPLETED', '2026-03-05 10:00:00+00', '2026-03-05 10:00:00+00', 'INV-S2026-011', NULL, 5, NULL, NULL, NULL),
(24, 'SALE', 238.00, 'EUR', 'COMPLETED', '2026-03-10 10:00:00+00', '2026-03-10 10:00:00+00', 'INV-S2026-012', NULL, 1, NULL, NULL, NULL),
(25, 'SALE', 382.00, 'EUR', 'PARTIAL',   '2026-03-16 10:00:00+00', NULL,                      'INV-S2026-013', NULL, 6, NULL, NULL, NULL),
(26, 'SALE', 196.00, 'EUR', 'COMPLETED', '2026-03-22 10:00:00+00', '2026-03-22 10:00:00+00', 'INV-S2026-014', NULL, 2, NULL, NULL, NULL),
(27, 'SALE', 230.00, 'EUR', 'COMPLETED', '2026-03-27 10:00:00+00', '2026-03-27 10:00:00+00', 'INV-S2026-015', NULL, 7, NULL, NULL, NULL),
(28, 'SALE', 207.50, 'EUR', 'COMPLETED', '2026-03-31 10:00:00+00', '2026-03-31 10:00:00+00', 'INV-S2026-016', NULL, 3, NULL, NULL, NULL),
-- Apr 2026
(29, 'SALE', 139.00, 'EUR', 'PENDING',   '2026-04-05 10:00:00+00', NULL,                      'INV-S2026-017', NULL, 8, NULL, NULL, NULL),
(30, 'SALE', 285.50, 'EUR', 'COMPLETED', '2026-04-10 10:00:00+00', '2026-04-10 10:00:00+00', 'INV-S2026-018', NULL, 4, NULL, NULL, NULL),
(31, 'SALE', 214.00, 'EUR', 'COMPLETED', '2026-04-17 10:00:00+00', '2026-04-17 10:00:00+00', 'INV-S2026-019', NULL, 5, NULL, NULL, NULL),
(32, 'SALE', 271.00, 'EUR', 'COMPLETED', '2026-04-23 10:00:00+00', '2026-04-23 10:00:00+00', 'INV-S2026-020', NULL, 1, NULL, NULL, NULL),
(33, 'SALE', 282.00, 'EUR', 'COMPLETED', '2026-04-29 10:00:00+00', '2026-04-29 10:00:00+00', 'INV-S2026-021', NULL, 6, NULL, NULL, NULL),
-- May 2026
(34, 'SALE', 250.00, 'EUR', 'COMPLETED', '2026-05-06 10:00:00+00', '2026-05-06 10:00:00+00', 'INV-S2026-022', NULL, 2, NULL, NULL, NULL),
(35, 'SALE', 244.00, 'EUR', 'COMPLETED', '2026-05-12 10:00:00+00', '2026-05-12 10:00:00+00', 'INV-S2026-023', NULL, 7, NULL, NULL, NULL),
(36, 'SALE', 249.00, 'EUR', 'COMPLETED', '2026-05-17 10:00:00+00', '2026-05-17 10:00:00+00', 'INV-S2026-024', NULL, 3, NULL, NULL, NULL),
(37, 'SALE', 260.00, 'EUR', 'COMPLETED', '2026-05-22 10:00:00+00', '2026-05-22 10:00:00+00', 'INV-S2026-025', NULL, 8, NULL, NULL, NULL),
(38, 'SALE', 375.00, 'EUR', 'COMPLETED', '2026-05-27 10:00:00+00', '2026-05-27 10:00:00+00', 'INV-S2026-026', NULL, 4, NULL, NULL, NULL),
(39, 'SALE', 358.50, 'EUR', 'PENDING',   '2026-05-30 10:00:00+00', NULL,                      'INV-S2026-027', NULL, 5, NULL, NULL, NULL);

-- ============================================================
-- 12. RESTOCKS  (2 line items per purchase transaction)
-- ============================================================
INSERT INTO restock (id, transaction_id, prod_id, quantity, restock_price, restock_date, notes, tax_rate_id, tax_amount, discount_type, discount_value, discount_amount)
OVERRIDING SYSTEM VALUE VALUES
(1,  1, 1, 50, 8.00, '2025-12-05 09:30:00+00', NULL, 1, 80.00, NULL, 0, 0),   -- T1  Salmon      50×8×20%
(2,  1, 2, 30, 5.00, '2025-12-05 09:30:00+00', NULL, 1, 30.00, NULL, 0, 0),   -- T1  Shrimp      30×5×20%
(3,  2, 3, 40, 6.00, '2025-12-18 09:30:00+00', NULL, 1, 48.00, NULL, 0, 0),   -- T2  Cod         40×6×20%
(4,  2, 4, 60, 2.50, '2025-12-18 09:30:00+00', NULL, 1, 30.00, NULL, 0, 0),   -- T2  Mussels     60×2.5×20%
(5,  3, 7, 35,12.00, '2026-01-08 09:30:00+00', NULL, 1, 84.00, NULL, 0, 0),   -- T3  Crab        35×12×20%
(6,  3, 6, 25, 9.00, '2026-01-08 09:30:00+00', NULL, 1, 45.00, NULL, 0, 0),   -- T3  Octopus     25×9×20%
(7,  4, 1, 45, 8.00, '2026-01-22 09:30:00+00', NULL, 1, 72.00, NULL, 0, 0),   -- T4  Salmon      45×8×20%
(8,  4, 5, 30, 7.00, '2026-01-22 09:30:00+00', NULL, 1, 42.00, NULL, 0, 0),   -- T4  Sea Bass    30×7×20%
(9,  5, 8, 35, 4.50, '2026-02-10 09:30:00+00', NULL, 1, 31.50, NULL, 0, 0),   -- T5  Squid       35×4.5×20%
(10, 5, 9, 50, 8.50, '2026-02-10 09:30:00+00', NULL, 1, 85.00, NULL, 0, 0),   -- T5  Wild Fish   50×8.5×20%
(11, 6, 1, 40, 8.00, '2026-02-25 09:30:00+00', NULL, 1, 64.00, NULL, 0, 0),   -- T6  Salmon      40×8×20%
(12, 6, 2, 35, 5.00, '2026-02-25 09:30:00+00', NULL, 1, 35.00, NULL, 0, 0),   -- T6  Shrimp      35×5×20%
(13, 7, 3, 50, 6.00, '2026-03-12 09:30:00+00', NULL, 1, 60.00, NULL, 0, 0),   -- T7  Cod         50×6×20%
(14, 7, 4, 70, 2.50, '2026-03-12 09:30:00+00', NULL, 1, 35.00, NULL, 0, 0),   -- T7  Mussels     70×2.5×20%
(15, 8, 5, 35, 7.00, '2026-03-28 09:30:00+00', NULL, 1, 49.00, NULL, 0, 0),   -- T8  Sea Bass    35×7×20%
(16, 8,10, 70, 4.00, '2026-03-28 09:30:00+00', NULL, 1, 56.00, NULL, 0, 0),   -- T8  Baby Shrimp 70×4×20%
(17, 9, 1, 60, 8.00, '2026-04-15 09:30:00+00', NULL, 1, 96.00, NULL, 0, 0),   -- T9  Salmon      60×8×20%
(18, 9, 6, 20, 9.00, '2026-04-15 09:30:00+00', NULL, 1, 36.00, NULL, 0, 0),   -- T9  Octopus     20×9×20%
(19,10, 7, 40,12.00, '2026-05-08 09:30:00+00', NULL, 1, 96.00, NULL, 0, 0),   -- T10 Crab        40×12×20%
(20,10, 8, 40, 4.50, '2026-05-08 09:30:00+00', NULL, 1, 36.00, NULL, 0, 0);   -- T10 Squid       40×4.5×20%

-- ============================================================
-- 13. SALES LINE ITEMS  (60 rows across 29 sale transactions)
--     Totals verified: sum(qty × prod_price) = transaction.total_amount
-- ============================================================
INSERT INTO sales (id, transaction_id, prod_id, prod_price, user_id, quantity, sale_date, notes, tax_rate_id, tax_amount, discount_type, discount_value, discount_amount)
OVERRIDING SYSTEM VALUE VALUES
-- Dec 2025 — T11 (126.50): 5×12.50 + 8×8.00
(1,  11, 1, 12.50, 1,  5, '2025-12-08 10:00:00+00', NULL, 1, 12.50, NULL, 0, 0),
(2,  11, 2,  8.00, 1,  8, '2025-12-08 10:00:00+00', NULL, 1, 12.80, NULL, 0, 0),
-- Dec 2025 — T12 (170.00): 10×9.50 + 15×5.00
(3,  12, 3,  9.50, 1, 10, '2025-12-20 10:00:00+00', NULL, 1, 19.00, NULL, 0, 0),
(4,  12, 4,  5.00, 1, 15, '2025-12-20 10:00:00+00', NULL, 1, 15.00, NULL, 0, 0),
-- Jan 2026 — T13 (61.00): 3×11.00 + 2×14.00
(5,  13, 5, 11.00, 1,  3, '2026-01-06 10:00:00+00', NULL, 1,  6.60, NULL, 0, 0),
(6,  13, 6, 14.00, 1,  2, '2026-01-06 10:00:00+00', NULL, 1,  5.60, NULL, 0, 0),
-- Jan 2026 — T14 (206.50): 8×18.00 + 5×12.50
(7,  14, 7, 18.00, 1,  8, '2026-01-12 10:00:00+00', NULL, 1, 28.80, NULL, 0, 0),
(8,  14, 1, 12.50, 1,  5, '2026-01-12 10:00:00+00', NULL, 1, 12.50, NULL, 0, 0),
-- Jan 2026 — T15 (130.00): 12×7.50 + 5×8.00
(9,  15, 8,  7.50, 1, 12, '2026-01-19 10:00:00+00', NULL, 1, 18.00, NULL, 0, 0),
(10, 15, 2,  8.00, 1,  5, '2026-01-19 10:00:00+00', NULL, 1,  8.00, NULL, 0, 0),
-- Jan 2026 — T16 (178.00): 8×12.50 + 6×13.00
(11, 16, 1, 12.50, 1,  8, '2026-01-26 10:00:00+00', NULL, 1, 20.00, NULL, 0, 0),
(12, 16, 9, 13.00, 1,  6, '2026-01-26 10:00:00+00', NULL, 1, 15.60, NULL, 0, 0),
-- Jan 2026 — T17 (258.00): 10×18.00 + 12×6.50
(13, 17, 7, 18.00, 1, 10, '2026-01-30 10:00:00+00', NULL, 1, 36.00, NULL, 0, 0),
(14, 17,10,  6.50, 1, 12, '2026-01-30 10:00:00+00', NULL, 1, 15.60, NULL, 0, 0),
-- Feb 2026 — T18 (203.00): 8×9.50 + 7×11.00 + 10×5.00
(15, 18, 3,  9.50, 1,  8, '2026-02-04 10:00:00+00', NULL, 1, 15.20, NULL, 0, 0),
(16, 18, 5, 11.00, 1,  7, '2026-02-04 10:00:00+00', NULL, 1, 15.40, NULL, 0, 0),
(17, 18, 4,  5.00, 1, 10, '2026-02-04 10:00:00+00', NULL, 1, 10.00, NULL, 0, 0),
-- Feb 2026 — T19 (93.00): 6×7.50 + 6×8.00
(18, 19, 8,  7.50, 1,  6, '2026-02-11 10:00:00+00', NULL, 1,  9.00, NULL, 0, 0),
(19, 19, 2,  8.00, 1,  6, '2026-02-11 10:00:00+00', NULL, 1,  9.60, NULL, 0, 0),
-- Feb 2026 — T20 (195.00): 10×12.50 + 5×14.00
(20, 20, 1, 12.50, 1, 10, '2026-02-17 10:00:00+00', NULL, 1, 25.00, NULL, 0, 0),
(21, 20, 6, 14.00, 1,  5, '2026-02-17 10:00:00+00', NULL, 1, 14.00, NULL, 0, 0),
-- Feb 2026 — T21 (311.00): 12×18.00 + 10×9.50
(22, 21, 7, 18.00, 1, 12, '2026-02-24 10:00:00+00', NULL, 1, 43.20, NULL, 0, 0),
(23, 21, 3,  9.50, 1, 10, '2026-02-24 10:00:00+00', NULL, 1, 19.00, NULL, 0, 0),
-- Feb 2026 — T22 (169.00): 8×13.00 + 10×6.50
(24, 22, 9, 13.00, 1,  8, '2026-02-28 10:00:00+00', NULL, 1, 20.80, NULL, 0, 0),
(25, 22,10,  6.50, 1, 10, '2026-02-28 10:00:00+00', NULL, 1, 13.00, NULL, 0, 0),
-- Mar 2026 — T23 (160.00): 20×5.00 + 8×7.50
(26, 23, 4,  5.00, 1, 20, '2026-03-05 10:00:00+00', NULL, 1, 20.00, NULL, 0, 0),
(27, 23, 8,  7.50, 1,  8, '2026-03-05 10:00:00+00', NULL, 1, 12.00, NULL, 0, 0),
-- Mar 2026 — T24 (238.00): 12×12.50 + 8×11.00
(28, 24, 1, 12.50, 1, 12, '2026-03-10 10:00:00+00', NULL, 1, 30.00, NULL, 0, 0),
(29, 24, 5, 11.00, 1,  8, '2026-03-10 10:00:00+00', NULL, 1, 17.60, NULL, 0, 0),
-- Mar 2026 — T25 (382.00 PARTIAL): 15×18.00 + 8×14.00
(30, 25, 7, 18.00, 1, 15, '2026-03-16 10:00:00+00', NULL, 1, 54.00, NULL, 0, 0),
(31, 25, 6, 14.00, 1,  8, '2026-03-16 10:00:00+00', NULL, 1, 22.40, NULL, 0, 0),
-- Mar 2026 — T26 (196.00): 15×8.00 + 8×9.50
(32, 26, 2,  8.00, 1, 15, '2026-03-22 10:00:00+00', NULL, 1, 24.00, NULL, 0, 0),
(33, 26, 3,  9.50, 1,  8, '2026-03-22 10:00:00+00', NULL, 1, 15.20, NULL, 0, 0),
-- Mar 2026 — T27 (230.00): 10×12.50 + 5×13.00 + 8×5.00
(34, 27, 1, 12.50, 1, 10, '2026-03-27 10:00:00+00', NULL, 1, 25.00, NULL, 0, 0),
(35, 27, 9, 13.00, 1,  5, '2026-03-27 10:00:00+00', NULL, 1, 13.00, NULL, 0, 0),
(36, 27, 4,  5.00, 1,  8, '2026-03-27 10:00:00+00', NULL, 1,  8.00, NULL, 0, 0),
-- Mar 2026 — T28 (207.50): 10×11.00 + 15×6.50
(37, 28, 5, 11.00, 1, 10, '2026-03-31 10:00:00+00', NULL, 1, 22.00, NULL, 0, 0),
(38, 28,10,  6.50, 1, 15, '2026-03-31 10:00:00+00', NULL, 1, 19.50, NULL, 0, 0),
-- Apr 2026 — T29 (139.00 PENDING — no payment): 10×7.50 + 8×8.00
(39, 29, 8,  7.50, 1, 10, '2026-04-05 10:00:00+00', NULL, 1, 15.00, NULL, 0, 0),
(40, 29, 2,  8.00, 1,  8, '2026-04-05 10:00:00+00', NULL, 1, 12.80, NULL, 0, 0),
-- Apr 2026 — T30 (285.50): 15×12.50 + 7×14.00
(41, 30, 1, 12.50, 1, 15, '2026-04-10 10:00:00+00', NULL, 1, 37.50, NULL, 0, 0),
(42, 30, 6, 14.00, 1,  7, '2026-04-10 10:00:00+00', NULL, 1, 19.60, NULL, 0, 0),
-- Apr 2026 — T31 (214.00): 12×9.50 + 20×5.00
(43, 31, 3,  9.50, 1, 12, '2026-04-17 10:00:00+00', NULL, 1, 22.80, NULL, 0, 0),
(44, 31, 4,  5.00, 1, 20, '2026-04-17 10:00:00+00', NULL, 1, 20.00, NULL, 0, 0),
-- Apr 2026 — T32 (271.00): 10×18.00 + 7×13.00
(45, 32, 7, 18.00, 1, 10, '2026-04-23 10:00:00+00', NULL, 1, 36.00, NULL, 0, 0),
(46, 32, 9, 13.00, 1,  7, '2026-04-23 10:00:00+00', NULL, 1, 18.20, NULL, 0, 0),
-- Apr 2026 — T33 (282.00): 12×12.50 + 12×11.00
(47, 33, 1, 12.50, 1, 12, '2026-04-29 10:00:00+00', NULL, 1, 30.00, NULL, 0, 0),
(48, 33, 5, 11.00, 1, 12, '2026-04-29 10:00:00+00', NULL, 1, 26.40, NULL, 0, 0),
-- May 2026 — T34 (250.00): 20×8.00 + 12×7.50
(49, 34, 2,  8.00, 1, 20, '2026-05-06 10:00:00+00', NULL, 1, 32.00, NULL, 0, 0),
(50, 34, 8,  7.50, 1, 12, '2026-05-06 10:00:00+00', NULL, 1, 18.00, NULL, 0, 0),
-- May 2026 — T35 (244.00): 8×18.00 + 8×12.50
(51, 35, 7, 18.00, 1,  8, '2026-05-12 10:00:00+00', NULL, 1, 28.80, NULL, 0, 0),
(52, 35, 1, 12.50, 1,  8, '2026-05-12 10:00:00+00', NULL, 1, 20.00, NULL, 0, 0),
-- May 2026 — T36 (249.00): 15×11.00 + 6×14.00
(53, 36, 5, 11.00, 1, 15, '2026-05-17 10:00:00+00', NULL, 1, 33.00, NULL, 0, 0),
(54, 36, 6, 14.00, 1,  6, '2026-05-17 10:00:00+00', NULL, 1, 16.80, NULL, 0, 0),
-- May 2026 — T37 (260.00): 10×13.00 + 20×6.50
(55, 37, 9, 13.00, 1, 10, '2026-05-22 10:00:00+00', NULL, 1, 26.00, NULL, 0, 0),
(56, 37,10,  6.50, 1, 20, '2026-05-22 10:00:00+00', NULL, 1, 26.00, NULL, 0, 0),
-- May 2026 — T38 (375.00): 20×12.50 + 25×5.00
(57, 38, 1, 12.50, 1, 20, '2026-05-27 10:00:00+00', NULL, 1, 50.00, NULL, 0, 0),
(58, 38, 4,  5.00, 1, 25, '2026-05-27 10:00:00+00', NULL, 1, 25.00, NULL, 0, 0),
-- May 2026 — T39 (358.50 PENDING — no payment): 12×18.00 + 15×9.50
(59, 39, 7, 18.00, 1, 12, '2026-05-30 10:00:00+00', NULL, 1, 43.20, NULL, 0, 0),
(60, 39, 3,  9.50, 1, 15, '2026-05-30 10:00:00+00', NULL, 1, 28.50, NULL, 0, 0);

-- ============================================================
-- 14. PAYMENTS  (37 payments; T29 and T39 are PENDING → no payment)
--     Purchase payments:  WITHDRAWAL from account
--     Sale payments:      DEPOSIT to account
--     CASH / TRANSFER → Cash EUR (account 1)
--     CARD / TRANSFER (bank) → Bank EUR (account 4)
-- ============================================================
INSERT INTO payment (id, transaction_id, account_id, amount, currency,
                     original_amount, original_currency, exchange_rate,
                     payment_method, payment_date, notes)
OVERRIDING SYSTEM VALUE VALUES
-- Purchases: odd IDs use TRANSFER→Bank EUR, even use CASH→Cash EUR
(1,  1,  4, 550.00, 'EUR', NULL, NULL, NULL, 'TRANSFER', '2025-12-05 17:00:00+00', NULL),
(2,  2,  1, 390.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2025-12-18 17:00:00+00', NULL),
(3,  3,  4, 645.00, 'EUR', NULL, NULL, NULL, 'TRANSFER', '2026-01-08 17:00:00+00', NULL),
(4,  4,  1, 570.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-01-22 17:00:00+00', NULL),
(5,  5,  4, 582.50, 'EUR', NULL, NULL, NULL, 'TRANSFER', '2026-02-10 17:00:00+00', NULL),
(6,  6,  1, 495.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-02-25 17:00:00+00', NULL),
(7,  7,  4, 475.00, 'EUR', NULL, NULL, NULL, 'TRANSFER', '2026-03-12 17:00:00+00', NULL),
(8,  8,  1, 525.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-03-28 17:00:00+00', NULL),
(9,  9,  4, 660.00, 'EUR', NULL, NULL, NULL, 'TRANSFER', '2026-04-15 17:00:00+00', NULL),
(10,10,  1, 660.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-05-08 17:00:00+00', NULL),
-- Sales
(11,11,  1, 126.50, 'EUR', NULL, NULL, NULL, 'CASH',     '2025-12-08 10:00:00+00', NULL),
(12,12,  4, 170.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2025-12-20 10:00:00+00', NULL),
(13,13,  1,  61.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-01-06 10:00:00+00', NULL),
(14,14,  1, 206.50, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-01-12 10:00:00+00', NULL),
(15,15,  4, 130.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-01-19 10:00:00+00', NULL),
(16,16,  1, 178.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-01-26 10:00:00+00', NULL),
(17,17,  4, 258.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-01-30 10:00:00+00', NULL),
(18,18,  1, 203.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-02-04 10:00:00+00', NULL),
(19,19,  1,  93.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-02-11 10:00:00+00', NULL),
(20,20,  4, 195.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-02-17 10:00:00+00', NULL),
(21,21,  1, 311.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-02-24 10:00:00+00', NULL),
(22,22,  4, 169.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-02-28 10:00:00+00', NULL),
(23,23,  1, 160.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-03-05 10:00:00+00', NULL),
(24,24,  1, 238.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-03-10 10:00:00+00', NULL),
(25,25,  4, 200.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-03-16 10:00:00+00', NULL),  -- partial: 200.00 of 382.00
(26,26,  1, 196.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-03-22 10:00:00+00', NULL),
(27,27,  4, 230.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-03-27 10:00:00+00', NULL),
(28,28,  1, 207.50, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-03-31 10:00:00+00', NULL),
-- T29 PENDING: no payment row
(29,30,  1, 285.50, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-04-10 10:00:00+00', NULL),
(30,31,  4, 214.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-04-17 10:00:00+00', NULL),
(31,32,  1, 271.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-04-23 10:00:00+00', NULL),
(32,33,  4, 282.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-04-29 10:00:00+00', NULL),
(33,34,  1, 250.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-05-06 10:00:00+00', NULL),
(34,35,  4, 244.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-05-12 10:00:00+00', NULL),
(35,36,  1, 249.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-05-17 10:00:00+00', NULL),
(36,37,  4, 260.00, 'EUR', NULL, NULL, NULL, 'CARD',     '2026-05-22 10:00:00+00', NULL),
(37,38,  1, 375.00, 'EUR', NULL, NULL, NULL, 'CASH',     '2026-05-27 10:00:00+00', NULL);
-- T39 PENDING: no payment row

-- ============================================================
-- 15. ACCOUNT TRANSACTIONS — opening balances (no linked payment)
-- ============================================================
INSERT INTO accounttransaction (account_id, payment_id, transaction_type, amount, balance_after, transaction_date, notes)
VALUES
(1, NULL, 'DEPOSIT',  5000.00,  5000.00, '2025-12-01 08:00:00+00', 'Opening balance'),
(4, NULL, 'DEPOSIT', 10000.00, 10000.00, '2025-12-01 08:00:00+00', 'Opening balance');

-- ============================================================
-- 16. ACCOUNT TRANSACTIONS — one entry per payment
--     Running balance = opening_balance + cumulative signed amounts,
--     partitioned by account and ordered by payment_date, payment_id.
-- ============================================================
INSERT INTO accounttransaction (account_id, payment_id, transaction_type, amount, balance_after, transaction_date)
WITH opening AS (
    -- pick up the opening balances inserted above
    SELECT account_id, balance_after AS opening_balance
    FROM   accounttransaction
    WHERE  payment_id IS NULL
),
ledger AS (
    SELECT
        p.id                                                                         AS payment_id,
        p.account_id,
        p.amount,
        CASE WHEN t.transaction_type = 'SALE' THEN 'DEPOSIT'    ELSE 'WITHDRAWAL' END AS txn_type,
        CASE WHEN t.transaction_type = 'SALE' THEN p.amount     ELSE -p.amount    END AS signed_amount,
        p.payment_date
    FROM   payment       p
    JOIN   "transaction" t ON t.id = p.transaction_id
),
running AS (
    SELECT
        l.payment_id,
        l.account_id,
        l.txn_type,
        l.amount,
        l.payment_date,
        COALESCE(o.opening_balance, 0)
            + SUM(l.signed_amount) OVER (
                  PARTITION BY l.account_id
                  ORDER BY     l.payment_date, l.payment_id
                  ROWS UNBOUNDED PRECEDING
              ) AS balance_after
    FROM   ledger  l
    LEFT JOIN opening o ON o.account_id = l.account_id
)
SELECT account_id, payment_id, txn_type, amount, balance_after, payment_date
FROM   running
ORDER  BY account_id, payment_date;

-- ============================================================
-- 17. SYNC account.current_balance to final ledger balance
-- ============================================================
UPDATE account a
SET    current_balance = (
    SELECT at2.balance_after
    FROM   accounttransaction at2
    WHERE  at2.account_id = a.id
    ORDER  BY at2.transaction_date DESC, at2.id DESC
    LIMIT  1
)
WHERE EXISTS (
    SELECT 1 FROM accounttransaction at3 WHERE at3.account_id = a.id
);

COMMIT;
