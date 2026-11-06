-- Auto Repair & Vehicle Maintenance Tracker - Sprint 1 sample data
-- Run only on a NEW, EMPTY database after schema.sql.
-- Do NOT run on your existing populated local database: IDs and emails/VINs
-- are deliberately fixed so relationships are deterministic.
-- All names, emails, phone numbers and VINs are synthetic examples.
USE auto_repair_db;

START TRANSACTION;

INSERT INTO Customer
(customer_id, first_name, last_name, email, phone) VALUES
(1, 'John', 'Smith', 'john.smith@example.com', '540-555-0101'),
(2, 'Sarah', 'Johnson', 'sarah.johnson@example.com', '540-555-0102'),
(3, 'Michael', 'Brown', 'michael.brown@example.com', '540-555-0103'),
(4, 'Emily', 'Davis', 'emily.davis@example.com', '540-555-0104'),
(5, 'Robert', 'Wilson', 'robert.wilson@example.com', '540-555-0105');

INSERT INTO Vehicle
(vehicle_id, customer_id, vin, make, model, year, mileage) VALUES
(1, 1, '1HGCM82633A004352', 'Toyota', 'Camry', 2023, 42000),
(2, 1, '1HGCM82633A004353', 'Honda', 'Civic', 2020, 68000),
(3, 2, '1HGCM82633A004354', 'Ford', 'F-150', 2019, 89000),
(4, 3, '1HGCM82633A004355', 'Chevrolet', 'Malibu', 2021, 51000),
(5, 4, '1HGCM82633A004356', 'Nissan', 'Altima', 2018, 105000),
(6, 5, '1HGCM82633A004357', 'Hyundai', 'Elantra', 2022, 31000),
(7, 5, '1HGCM82633A004358', 'Toyota', 'RAV4', 2024, 18000);

INSERT INTO Repair
(repair_id, vehicle_id, description, repair_date, cost, status) VALUES
(1, 1, 'Oil and filter change', '2026-09-10', 65.00, 'Completed'),
(2, 1, 'Brake pad replacement', '2026-10-15', 320.00, 'Completed'),
(3, 2, 'Tire rotation', '2026-10-20', 45.00, 'Completed'),
(4, 3, 'Transmission inspection', '2026-10-21', 150.00, 'In Progress'),
(5, 4, 'Battery replacement', '2026-10-22', 210.00, 'Completed'),
(6, 5, 'Engine diagnostic', '2026-10-25', 120.00, 'Pending'),
(7, 5, 'Air filter replacement', '2026-09-15', 35.00, 'Completed'),
(8, 6, 'Brake fluid replacement', '2026-10-28', 110.00, 'Completed'),
(9, 7, 'Oil and filter change', '2026-10-30', 75.00, 'Completed'),
(10, 3, 'Tire replacement', '2026-11-02', 680.00, 'Pending');

COMMIT;
