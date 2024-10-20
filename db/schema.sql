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

CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, --has table with possible names
    category VARCHAR(255) NOT NULL, --has table with possible categories
    price DECIMAL(10, 2) NOT NULL, -- price per kg
    description TEXT NOT NULL
);

CREATE TABLE Product_Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Product_Names (
    product_name_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Product_Categories(category_id)
);


CREATE TABLE Inventory (
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);

CREATE TABLE Sales (
    id SERIAL PRIMARY KEY,
    prod_id INT NOT NULL,
    user_id INT NOT NULL,
    quantity INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Restock (
    id SERIAL PRIMARY KEY,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);

-- Inserting data
INSERT INTO Users (username, password, email, firstname, lastname, role) VALUES ('admin', 'admin', 'admin@selita_fish.com', 'Admin', 'Admin', 'admin');
INSERT INTO Product_Categories (category_name) VALUES ('Fish'), ('Seafood'), ('Shellfish'), ('Crustaceans'), ('Molluscs');
INSERT INTO Product_Names (product_name, category_id) VALUES ('Salmon', 1), ('Tuna', 1), ('Swordfish', 1), ('Cod', 1), ('Haddock', 1), ('Mackerel', 1), ('Sardines', 1), ('Anchovies', 1), ('Prawns', 2), ('Shrimp', 2), ('Crab', 3), ('Lobster', 3), ('Crayfish', 3), ('Mussels', 4), ('Oysters', 4), ('Clams', 4), ('Scallops', 4), ('Squid', 5), ('Octopus', 5);
INSERT INTO Product (name, category, price, description) VALUES ('Salmon', 'Fish', 10.00, 'Fresh salmon fillets'), ('Tuna', 'Fish', 12.00, 'Fresh tuna steaks'), ('Swordfish', 'Fish', 15.00, 'Fresh swordfish steaks'), ('Cod', 'Fish', 8.00, 'Fresh cod fillets'), ('Haddock', 'Fish', 7.00, 'Fresh haddock fillets'), ('Mackerel', 'Fish', 6.00, 'Fresh mackerel fillets'), ('Sardines', 'Fish', 5.00, 'Fresh sardines'), ('Anchovies', 'Fish', 4.00, 'Fresh anchovies'), ('Prawns', 'Seafood', 20.00, 'Fresh prawns'), ('Shrimp', 'Seafood', 18.00, 'Fresh shrimp'), ('Crab', 'Shellfish', 25.00, 'Fresh crab'), ('Lobster', 'Shellfish', 30.00, 'Fresh lobster'), ('Crayfish', 'Shellfish', 22.00, 'Fresh crayfish'), ('Mussels', 'Crustaceans', 12.00, 'Fresh mussels'), ('Oysters', 'Crustaceans', 14.00, 'Fresh oysters'), ('Clams', 'Crustaceans', 10.00, 'Fresh clams'), ('Scallops', 'Crustaceans', 16.00, 'Fresh scallops'), ('Squid', 'Molluscs', 8.00, 'Fresh squid'), ('Octopus', 'Molluscs', 10.00, 'Fresh octopus'), ('Merluc', 'Fish', 4.00, 'Fresh anchovies');
INSERT INTO Inventory (prod_id, quantity) VALUES (1, 100), (2, 100), (3, 100), (4, 100), (5, 100), (6, 100), (7, 100), (8, 100), (9, 100), (10, 100), (11, 100), (12, 100), (13, 100), (14, 100), (15, 100), (16, 100), (17, 100), (18, 100), (19, 100);
INSERT INTO Sales (prod_id, user_id, quantity) VALUES (1, 1, 10), (2, 1, 10), (3, 1, 10), (4, 1, 10), (5, 1, 10), (6, 1, 10), (7, 1, 10), (8, 1, 10), (9, 1, 10), (10, 1, 10), (11, 1, 10), (12, 1, 10), (13, 1, 10), (14, 1, 10), (15, 1, 10), (16, 1, 10), (17, 1, 10), (18, 1, 10), (19, 1, 10);
INSERT INTO Restock (prod_id, quantity) VALUES (1, 100), (2, 100), (3, 100), (4, 100), (5, 100), (6, 100), (7, 100), (8, 100), (9, 100), (10, 100), (11, 100), (12, 100), (13, 100), (14, 100), (15, 100), (16, 100), (17, 100), (18, 100), (19, 100);



