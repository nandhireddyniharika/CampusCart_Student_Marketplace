CREATE DATABASE campuscart;

USE campuscart;

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE products(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    title VARCHAR(200),
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2),
    image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages(
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_email VARCHAR(100),
    receiver_email VARCHAR(100),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    product_id INT
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    message TEXT,
    status VARCHAR(20) DEFAULT 'UNREAD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);