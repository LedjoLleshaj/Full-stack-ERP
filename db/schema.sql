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
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Product_Names (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
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
INSERT INTO Product_Categories (category_name) VALUES ('Peshk'), ('Fruta Deti'), ('Gafforre'), ('Kallamar'), ('Midhje'),('Karkaleca'),('Peshk i eger');
INSERT INTO Product_Names (product_name, category_id) VALUES 
('Salmon',1),('Karkaleca',5),('Koce',1),('Midhje',
5),('Peshk i eger',1),('Peshk',1),('Fruta Deti',2),('Gafforre',3),('Kallamar',4),('Karkaleca',6),('Peshk i eger',7);
INSERT INTO Product (name, category, price, description) VALUES 
('Salmon', 'Peshk', 10.00, 'Salmon fish from Norway'),
('Karkaleca', 'Fruta Deti', 15.00, 'Shrimp from Mediterranean'),
('Koce', 'Peshk', 20.00, 'Tuna fish from Atlantic'),
('Midhje', 'Fruta Deti', 5.00, 'Mussels from Adriatic'),
('Peshk i eger', 'Peshk i eger', 30.00, 'Wild fish from Adriatic'),
('Peshk', 'Peshk', 12.00, 'Fish from Adriatic'),
('Fruta Deti', 'Fruta Deti', 8.00, 'Seafood from Adriatic'),
('Gafforre', 'Gafforre', 25.00, 'Eel from Adriatic'),
('Kallamar', 'Kallamar', 18.00, 'Squid from Adriatic'),
('Karkaleca', 'Karkaleca', 22.00, 'Crab from Adriatic'),
('Peshk i eger', 'Peshk i eger', 35.00, 'Wild fish from Adriatic');
INSERT INTO Inventory (prod_id, quantity) VALUES 
(1, 100), (2, 100), (3, 100), (4, 100), (5, 100), (6, 100), (7, 100), (8, 100), (9, 100), (10, 100), (11, 100), (12, 100), (13, 100), (14, 100), (15, 100), (16, 100), (17, 100), (18, 100), (19, 100);
INSERT INTO Sales (prod_id, user_id, quantity) VALUES 
(1, 1, 10), (2, 1, 5), (3, 1, 20), (4, 1, 15), (5, 1, 8), (6, 1, 12), (7, 1, 7), (8, 1, 9), (9, 1, 11), (10, 1, 6), (11, 1, 14), (12, 1, 13), (13, 1, 4), (14, 1, 3), (15, 1, 2), (16, 1, 1), (17, 1, 0), (18, 1, -1), (19, 1, -2);
INSERT INTO Restock (prod_id, quantity) VALUES 
(1, 50), (2, 30), (3, 20), (4, 10), (5, 5), (6, 15), (7, 25), (8, 35), (9, 45), (10, 55), (11, 65), (12, 75), (13, 85), (14, 95), (15, 105), (16, 115), (17, 125), (18, 135), (19, 145);

