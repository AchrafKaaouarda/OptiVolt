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

CREATE TABLE subscription_plan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prix_mensuel FLOAT NOT NULL,
    duree_jours INT DEFAULT 30,
    max_services INT DEFAULT 5,
    has_scheduling BOOLEAN DEFAULT FALSE,
    has_priority_support BOOLEAN DEFAULT FALSE,
    has_analytics BOOLEAN DEFAULT FALSE,
    description TEXT
);

CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nom_entreprise VARCHAR(100) NOT NULL,
    description TEXT,
    ville VARCHAR(50),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    horaire_debut VARCHAR(5) DEFAULT '08:00',
    horaire_fin VARCHAR(5) DEFAULT '18:00',
    jours_travail VARCHAR(50) DEFAULT 'Lun-Sam',
    is_verified BOOLEAN DEFAULT FALSE,
    subscription_plan_id INT,
    subscription_start DATE,
    subscription_expires_at DATE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_plan_id) REFERENCES subscription_plans (id)
);

CREATE TABLE service_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_service VARCHAR(100) NOT NULL,
    description TEXT,
    category ENUM(
        'Maintenance',
        'Installation',
        'Nettoyage',
        'Diagnostic',
        'Autre'
    ) DEFAULT 'Autre'
);

CREATE TABLE catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    service_type_id INT NOT NULL,
    prix_base FLOAT NOT NULL,
    prix_par_unite FLOAT DEFAULT 0,
    unite_nom VARCHAR(50) DEFAULT 'panneau',
    description_offre TEXT,
    produits_inclus TEXT,
    duree_estimee VARCHAR(50),
    FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
    FOREIGN KEY (service_type_id) REFERENCES service_types (id)
);