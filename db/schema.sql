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
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(255) UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL
    );

CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL, --has table with possible names
    category VARCHAR(255) NOT NULL, --has table with possible categories
    price DECIMAL(10, 2) NOT NULL, -- price per kg
    description TEXT NOT NULL,
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
    prod_id INT NOT NULL,
    prod_price DECIMAL(10, 2) NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE,
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
INSERT INTO Clients (firstname, lastname, email, phone, address, city) VALUES ('Ledjo', 'Lleshaj', 'ledjo@selita_fish.com', '1234567890', 'Rruga e Dajlani', 'Durres'), ('Kristjan', 'Gjinaj', 'Kristjan@selita_fish.com', '1234567890', 'Rruga e Dajlani', 'Tirane');
INSERT INTO Product_Categories (category_name) VALUES ('Peshk'), ('Fruta Deti'), ('Gafforre'), ('Kallamar'), ('Midhje'),('Karkaleca'),('Peshk i eger');
INSERT INTO Product_Names (product_name, category_id) VALUES 
('Salmon',1),('Karkaleca',5),('Koce',1),('Midhje',
5),('Peshk i eger',1),('Peshk',1),('Fruta Deti',2),('Gafforre',3),('Kallamar',4),('Karkaleca',6),('Peshk i eger',7);
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
INSERT INTO Sales (prod_id,prod_price,is_paid, user_id,client_id, quantity) VALUES 
(1, 10.00, TRUE, 1, 1, 2), (2, 15.00, FALSE, 1, 2, 3), (3, 20.00, TRUE, 1, 1, 4), (4, 5.00, TRUE, 1, 2, 5), (5, 30.00, TRUE, 1, 1, 6), (6, 12.00, TRUE, 1, 2, 7), (7, 8.00, FALSE, 1, 1, 8), (8, 25.00, FALSE, 1, 2, 9), (9, 18.00, FALSE, 1, 1 ,10), (10 ,22.00 ,FALSE ,1 ,2 ,11), (11 ,35.00 ,TRUE ,1 ,1 ,12);

--INSERT INTO Restock (prod_id, quantity) VALUES 
--(1, 50), (2, 30), (3, 20), (4, 10), (5, 5), (6, 15), (7, 25), (8, 35), (9, 45), (10, 55), (11, 65);

