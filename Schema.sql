CREATE DATABASE IF NOT EXISTS optivolt DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE optivolt;
-- TABLES --
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM(
        'CLIENT',
        'ENTREPRISE',
        'ADMIN'
    ) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    ville VARCHAR(50),
    adresse TEXT,
    is_banned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);