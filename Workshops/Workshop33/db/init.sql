CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

INSERT INTO products (name, price) VALUES
('Laptop', 3500000),
('Mouse', 80000),
('Keyboard', 150000),
('Monitor', 900000),
('Headphones', 120000);
