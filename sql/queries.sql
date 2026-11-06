-- Auto Repair & Vehicle Maintenance Tracker - Sprint 1 query tests
-- Safe to run multiple times on a populated Sprint 1 database.
-- CREATE, UPDATE and DELETE tests are rolled back; SELECTs are read-only.
-- These statements use the sample three-table schema from schema.sql.
USE auto_repair_db;

-- READ: customers, vehicles and repair records
SELECT * FROM Customer ORDER BY customer_id;
SELECT * FROM Vehicle ORDER BY vehicle_id;
SELECT * FROM Repair ORDER BY repair_id;

-- JOIN: vehicles plus owners
SELECT c.customer_id, c.first_name, c.last_name,
       v.vehicle_id, v.make, v.model, v.year
FROM Customer AS c
JOIN Vehicle AS v ON v.customer_id = c.customer_id
ORDER BY c.customer_id, v.vehicle_id;

-- JOIN: vehicle repair history
SELECT v.vehicle_id, v.make, v.model,
       r.repair_id, r.description, r.repair_date, r.cost, r.status
FROM Vehicle AS v
JOIN Repair AS r ON r.vehicle_id = v.vehicle_id
ORDER BY r.repair_date DESC, r.repair_id DESC;

-- JOIN: owner -> vehicle -> repair
SELECT c.first_name, c.last_name, v.make, v.model,
       r.description, r.cost, r.status
FROM Customer AS c
JOIN Vehicle AS v ON v.customer_id = c.customer_id
JOIN Repair AS r ON r.vehicle_id = v.vehicle_id
ORDER BY c.last_name, r.repair_id;

-- AGGREGATE: vehicles per customer, including customers without vehicles
SELECT c.customer_id, c.first_name, c.last_name,
       COUNT(v.vehicle_id) AS total_vehicles
FROM Customer AS c
LEFT JOIN Vehicle AS v ON v.customer_id = c.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY c.customer_id;

-- AGGREGATE: completed repair costs per customer
SELECT c.customer_id, c.first_name, c.last_name,
       COALESCE(SUM(r.cost), 0) AS completed_repair_total
FROM Customer AS c
LEFT JOIN Vehicle AS v ON v.customer_id = c.customer_id
LEFT JOIN Repair AS r ON r.vehicle_id = v.vehicle_id
                  AND r.status = 'Completed'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY completed_repair_total DESC;

-- AGGREGATE: count repairs by status
SELECT status, COUNT(*) AS total_repairs
FROM Repair
GROUP BY status
ORDER BY status;

-- CRUD smoke test within a transaction so the database remains unchanged.
-- Uses a test email and a unique test VIN; does not assume any particular IDs.
START TRANSACTION;

-- CREATE customer
INSERT INTO Customer (first_name, last_name, email, phone)
VALUES ('Sprint', 'Test', 'sprint1-crud-test@example.invalid', '540-555-0199');
SET @test_customer_id = LAST_INSERT_ID();

-- READ customer
SELECT * FROM Customer WHERE customer_id = @test_customer_id;

-- UPDATE customer
UPDATE Customer
SET phone = '540-555-9999'
WHERE customer_id = @test_customer_id;
SELECT * FROM Customer WHERE customer_id = @test_customer_id;

-- CREATE and READ vehicle
INSERT INTO Vehicle (customer_id, vin, make, model, year, mileage)
VALUES (@test_customer_id, 'TEST0000000000001', 'Test', 'Vehicle', 2022, 1000);
SET @test_vehicle_id = LAST_INSERT_ID();
SELECT * FROM Vehicle WHERE vehicle_id = @test_vehicle_id;

-- UPDATE vehicle
UPDATE Vehicle SET mileage = 1500 WHERE vehicle_id = @test_vehicle_id;
SELECT * FROM Vehicle WHERE vehicle_id = @test_vehicle_id;

-- CREATE and READ repair
INSERT INTO Repair (vehicle_id, description, repair_date, cost, status)
VALUES (@test_vehicle_id, 'Sprint 1 CRUD test', '2026-11-05', 20.00, 'Pending');
SET @test_repair_id = LAST_INSERT_ID();
SELECT * FROM Repair WHERE repair_id = @test_repair_id;

-- UPDATE repair
UPDATE Repair SET status = 'Completed' WHERE repair_id = @test_repair_id;
SELECT * FROM Repair WHERE repair_id = @test_repair_id;

-- DELETE in child-to-parent order (respecting RESTRICT foreign keys)
DELETE FROM Repair WHERE repair_id = @test_repair_id;
DELETE FROM Vehicle WHERE vehicle_id = @test_vehicle_id;
DELETE FROM Customer WHERE customer_id = @test_customer_id;

-- Revert all test writes; AUTO_INCREMENT counters may still advance.
ROLLBACK;
