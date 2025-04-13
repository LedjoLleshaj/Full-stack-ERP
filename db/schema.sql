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

CREATE TABLE Clients (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
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
    client_id INT NOT NULL,
    quantity INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (client_id) REFERENCES Clients(id)

);

CREATE TABLE Restock (
    id SERIAL PRIMARY KEY,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    restock_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prod_id) REFERENCES Product(id)
);


-- Inserting data
INSERT INTO Users (username, password, email, firstname, lastname, role) VALUES ('admin', 'pbkdf2_sha256$870000$4Q0rcQv0fwttnrAAWvqpfU$vzu7I2egFdnXYvsfrGna0Ee5PO2u5O+XeQ7z1avuyrI=', 'admin@selita_fish.com', 'Admin', 'Admin', 'admin'),('Ledjo', 'pbkdf2_sha256$870000$4Q0rcQv0fwttnrAAWvqpfU$vzu7I2egFdnXYvsfrGna0Ee5PO2u5O+XeQ7z1avuyrI=', 'ledjo@selita_fish.com', 'Ledjo', 'Lleshaj', 'admin');
INSERT INTO Clients (firstname, lastname, email, phone, address, city) VALUES ('Ledjo', 'Lleshaj', 'ledjo@selita_fish.com', '1234567890', 'Rruga e Dajlani', 'Durres'), ('Kristi', 'Gjinaj', 'kristi@selita_fish.com', '1234567890', 'Rruga e Dajlani', 'Tirane');
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
(1, 100), (2, 100), (3, 100), (4, 100), (5, 100), (6, 100), (7, 100), (8, 100), (9, 100), (10, 100), (11, 100);
INSERT INTO Sales (prod_id, user_id,client_id, quantity) VALUES (1, 1,2, 10), (2, 1,2, 10), (3, 1,1, 10), (4, 1,1, 10), (5, 1,1, 10), (6, 1,1, 10), (7, 1,1, 10), (8, 1,1, 10), (9, 1,1, 10), (10, 1,1, 10), (11, 1,1, 10), (2, 1,1, 10), (3, 1,1, 10), (4, 1,1, 10), (5, 1,1, 10), (6, 1,1, 10), (7, 1,1, 10), (8, 1,1, 10), (9, 1,1, 10);
INSERT INTO Restock (prod_id, quantity) VALUES 
(1, 50), (2, 30), (3, 20), (4, 10), (5, 5), (6, 15), (7, 25), (8, 35), (9, 45), (10, 55), (11, 65);

