-- Auto Repair & Vehicle Maintenance Tracker - Sprint 1
-- MySQL 8.0.16+ (CHECK constraints enforced)
-- IMPORTANT: This is the three-table Sprint 1 example used during implementation.
-- Compare column names and relationships against your finalized relational schema.
-- Safe to re-run on an existing database: does not drop or modify existing tables.
-- Existing tables are NOT verified or migrated by CREATE TABLE IF NOT EXISTS.

CREATE DATABASE IF NOT EXISTS auto_repair_db
    CHARACTER SET utf8mb4;
USE auto_repair_db;

CREATE TABLE IF NOT EXISTS Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vin CHAR(17) NOT NULL UNIQUE,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year SMALLINT NOT NULL,
    mileage INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_vehicle_customer
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_vehicle_year CHECK (year BETWEEN 1886 AND 2100),
    CONSTRAINT chk_vehicle_mileage CHECK (mileage >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Repair (
    repair_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    repair_date DATE NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_repair_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_repair_cost CHECK (cost >= 0),
    CONSTRAINT chk_repair_status
        CHECK (status IN ('Pending', 'In Progress', 'Completed'))
) ENGINE=InnoDB;

-- Inspect the installed schema (run these separately when checking an existing DB):
-- SHOW CREATE TABLE Customer\G
-- SHOW CREATE TABLE Vehicle\G
-- SHOW CREATE TABLE Repair\G
