-- Abaad Contracting Company - Seed Data
USE abaad_contracting;

INSERT INTO Role (Title, Description) VALUES
('CEO', 'Chief Executive Officer'),
('Project Manager', 'Manages construction projects'),
('Site Engineer', 'Oversees construction site operations'),
('Civil Engineer', 'Designs and supervises construction'),
('Architect', 'Designs building structures'),
('Quantity Surveyor', 'Estimates costs and quantities'),
('Site Supervisor', 'Supervises daily site activities'),
('Equipment Operator', 'Operates heavy machinery'),
('Laborer', 'General construction worker'),
('HR Manager', 'Human Resources management'),
('Accountant', 'Financial management and reporting'),
('Procurement Officer', 'Handles material purchases');

INSERT INTO Branch (BranchName, City, Address, PhoneNumber) VALUES
('Head Office', 'Ramallah', 'Al-Bireh Main Street, Building 45', '+970-2-2951234'),
('Nablus Branch', 'Nablus', 'Rafidia Street, Building 12', '+970-9-2345678'),
('Gaza Branch', 'Gaza City', 'Omar Al-Mukhtar Street, Tower 3', '+970-8-1234567'),
('Hebron Branch', 'Hebron', 'King Faisal Street, Complex A', '+970-2-2234567');

INSERT INTO Department (DepartmentName, ManagerID) VALUES
('Engineering', NULL),
('Construction', NULL),
('Procurement', NULL),
('Finance', NULL),
('Human Resources', NULL);

INSERT INTO Employee (EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID, HireDate, Email, PhoneNumber) VALUES
('Ahmad Al-Khatib', 1, 15000.00, 1, 1, NULL, '2010-01-15', 'ahmad.khatib@abaad.ps', '+970-59-1234567'),
('Mohammad Abdo', 2, 8500.00, 1, 2, NULL, '2015-03-20', 'mohammad.abdo@abaad.ps', '+970-59-2345678'),
('Sara Nasser', 3, 6500.00, 1, 1, NULL, '2017-06-10', 'sara.nasser@abaad.ps', '+970-59-3456789'),
('Khalid Mansour', 4, 7200.00, 1, 1, NULL, '2016-08-05', 'khalid.mansour@abaad.ps', '+970-59-4567890'),
('Layla Hamdan', 11, 6000.00, 1, 4, NULL, '2018-02-14', 'layla.hamdan@abaad.ps', '+970-59-5678901'),
('Yusuf Salim', 10, 7000.00, 1, 5, NULL, '2017-11-30', 'yusuf.salim@abaad.ps', '+970-59-6789012'),
('Noor Ibrahim', 12, 5500.00, 1, 3, NULL, '2019-04-22', 'noor.ibrahim@abaad.ps', '+970-59-7890123'),
('Omar Faraj', 2, 8000.00, 2, 2, NULL, '2014-09-15', 'omar.faraj@abaad.ps', '+970-59-8901234'),
('Rania Zaid', 3, 6200.00, 2, 1, NULL, '2018-07-20', 'rania.zaid@abaad.ps', '+970-59-9012345'),
('Bassem Atta', 4, 7000.00, 2, 1, NULL, '2016-12-01', 'bassem.atta@abaad.ps', '+970-59-0123456'),
('Mona Shaker', 7, 4800.00, 2, 2, NULL, '2020-03-10', 'mona.shaker@abaad.ps', '+970-59-1234509'),
('Tariq Jaber', 8, 4200.00, 2, 2, NULL, '2020-05-18', 'tariq.jaber@abaad.ps', '+970-59-2345601'),
('Hassan Salama', 2, 7800.00, 3, 2, NULL, '2015-10-25', 'hassan.salama@abaad.ps', '+970-59-3456702'),
('Nadia Mahmoud', 3, 6000.00, 3, 1, NULL, '2019-01-12', 'nadia.mahmoud@abaad.ps', '+970-59-4567803'),
('Samir Qadri', 6, 5800.00, 3, 2, NULL, '2018-08-08', 'samir.qadri@abaad.ps', '+970-59-5678904'),
('Fatima Khalil', 2, 8200.00, 4, 2, NULL, '2016-04-03', 'fatima.khalil@abaad.ps', '+970-59-6789015'),
('Ibrahim Asad', 3, 6400.00, 4, 1, NULL, '2019-09-17', 'ibrahim.asad@abaad.ps', '+970-59-7890126'),
('Lina Younis', 7, 4900.00, 4, 2, NULL, '2021-02-28', 'lina.younis@abaad.ps', '+970-59-8901237');

UPDATE Department SET ManagerID = 1 WHERE DepartmentID = 1;
UPDATE Department SET ManagerID = 2 WHERE DepartmentID = 2;
UPDATE Department SET ManagerID = 7 WHERE DepartmentID = 3;
UPDATE Department SET ManagerID = 5 WHERE DepartmentID = 4;
UPDATE Department SET ManagerID = 6 WHERE DepartmentID = 5;

UPDATE Employee SET ManagerID = 1 WHERE EmployeeID IN (3, 4, 10, 11, 16);
UPDATE Employee SET ManagerID = 2 WHERE EmployeeID IN (9, 12, 14, 17, 19);
UPDATE Employee SET ManagerID = 8 WHERE EmployeeID IN (12, 14, 18);
UPDATE Employee SET ManagerID = 13 WHERE EmployeeID IN (15, 16);
UPDATE Employee SET ManagerID = 18 WHERE EmployeeID IN (20, 21);

INSERT INTO BranchManager (BranchID, EmployeeID, AssignedDate) VALUES
(1, 1, '2010-01-15'),
(2, 8, '2014-09-15'),
(3, 13, '2015-10-25'),
(4, 18, '2016-04-03');

INSERT INTO Client (ClientName, ContactInfo, Email, PhoneNumber) VALUES
('Ministry of Public Works', 'Government Building, Ramallah', 'info@mopw.ps', '+970-2-2980000'),
('Palestine Investment Fund', 'Al-Masyoun, Ramallah', 'contact@pif.ps', '+970-2-2981000'),
('Red Crescent Society', 'Nablus Main Office', 'info@rcs.ps', '+970-9-2334567'),
('Qatar Red Crescent', 'Gaza City Office', 'qrc@gaza.ps', '+970-8-2840000'),
('UNRWA', 'Regional Office, Jerusalem', 'info@unrwa.org', '+972-2-5890400'),
('World Bank Project', 'Ramallah Office', 'wb-palestine@worldbank.org', '+970-2-2955000'),
('Private Developer - Al-Hamra', 'Al-Bireh', 'info@alhamra.ps', '+970-59-9876543'),
('Municipality of Hebron', 'Hebron City Hall', 'info@hebron.ps', '+970-2-2222000');

INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID, StartDate, EndDate, Status) VALUES
('Public School Complex - Ramallah', 'Al-Bireh, Ramallah', 2500000.00, 2800000.00, 1, 1, '2023-01-15', '2024-06-30', 'Completed'),
('Residential Tower - Nablus', 'Downtown Nablus', 1800000.00, 2100000.00, 2, 7, '2023-03-01', NULL, 'Active'),
('Hospital Extension - Gaza', 'Gaza City', 3200000.00, 3500000.00, 3, 4, '2023-05-10', NULL, 'Active'),
('Road Infrastructure - Hebron', 'Hebron Governorate', 1500000.00, 1700000.00, 4, 8, '2023-07-20', '2024-12-31', 'Active'),
('Warehouse Facility - Nablus', 'Industrial Zone, Nablus', 900000.00, 1050000.00, 2, 2, '2024-01-10', NULL, 'Active'),
('Office Building - Ramallah', 'Al-Masyoun, Ramallah', 2200000.00, 2500000.00, 1, 2, '2024-02-01', NULL, 'Planning'),
('Health Center - Hebron', 'Hebron City', 1200000.00, 1350000.00, 4, 5, '2024-03-15', NULL, 'Active'),
('Water Treatment Plant - Gaza', 'Northern Gaza', 4500000.00, 5000000.00, 3, 6, '2023-09-01', NULL, 'Active'),
('Sports Complex - Ramallah', 'Birzeit Road, Ramallah', 2800000.00, 3200000.00, 1, 1, '2023-11-01', '2025-05-30', 'Active'),
('Shopping Mall - Nablus', 'Rafidia, Nablus', 3500000.00, 4000000.00, 2, 7, '2024-04-01', NULL, 'Planning');

INSERT INTO Material (MaterialName, BaseUnitPrice, UnitOfMeasure) VALUES
('Cement (Portland)', 85.50, 'Bag (50kg)'),
('Reinforcement Steel (Rebar)', 1200.00, 'Ton'),
('Concrete Ready-Mix (C30)', 450.00, 'Cubic Meter'),
('Bricks (Standard)', 0.45, 'Piece'),
('Sand (Fine)', 35.00, 'Cubic Meter'),
('Gravel (Coarse)', 40.00, 'Cubic Meter'),
('Electrical Wire (Copper 2.5mm)', 450.00, 'Roll (100m)'),
('PVC Pipes (4 inch)', 25.00, 'Meter'),
('Aluminum Windows', 320.00, 'Square Meter'),
('Ceramic Tiles', 18.50, 'Square Meter'),
('Paint (Interior)', 65.00, 'Gallon'),
('Gypsum Board', 8.50, 'Square Meter'),
('Steel Beams (I-Beam)', 850.00, 'Ton'),
('Insulation Material', 22.00, 'Square Meter'),
('Roofing Sheets (Metal)', 28.00, 'Square Meter');

INSERT INTO Supplier (SupplierName, ContactInfo, Email, PhoneNumber) VALUES
('Palestine Cement Company', 'Hebron Industrial Zone', 'sales@pcc.ps', '+970-2-2223000'),
('Al-Quds Steel Works', 'Nablus Industrial Area', 'info@aqsw.ps', '+970-9-2340000'),
('Ready-Mix Concrete Co.', 'Multiple Locations', 'orders@rmc.ps', '+970-59-1111111'),
('Building Materials Trading', 'Ramallah', 'sales@bmt.ps', '+970-2-2951111'),
('Electrical Supplies Ltd.', 'Gaza City', 'info@electrical.ps', '+970-8-1234000');

INSERT INTO SupplierMaterial (SupplierID, MaterialID, Price, LeadTime) VALUES
(1, 1, 82.00, 3), (1, 5, 33.00, 2), (1, 6, 38.00, 2),
(2, 2, 1180.00, 5), (2, 13, 830.00, 7),
(3, 3, 445.00, 1), (3, 5, 34.00, 1), (3, 6, 39.00, 1),
(4, 1, 86.00, 2), (4, 4, 0.43, 1), (4, 5, 35.00, 2),
(5, 7, 440.00, 4), (5, 8, 24.00, 3);

INSERT INTO WorkAssignment (ProjectID, EmployeeID, Role, HoursWorked, StartDate, EndDate) VALUES
(1, 2, 'Project Manager', 320.00, '2023-01-15', '2024-06-30'),
(1, 3, 'Site Engineer', 450.00, '2023-01-15', '2024-06-30'),
(2, 9, 'Project Manager', 280.00, '2023-03-01', NULL),
(2, 11, 'Site Engineer', 520.00, '2023-03-01', NULL),
(3, 14, 'Project Manager', 350.00, '2023-05-10', NULL),
(3, 16, 'Site Engineer', 480.00, '2023-05-10', NULL);

INSERT INTO ProjectMaterial (ProjectID, MaterialID, Quantity, UnitPrice) VALUES
(1, 1, 2500.00, 84.00), (1, 2, 45.00, 1190.00), (1, 3, 380.00, 448.00),
(2, 1, 1800.00, 83.50), (2, 2, 32.00, 1185.00), (2, 3, 290.00, 446.00),
(3, 1, 3200.00, 85.00), (3, 2, 55.00, 1200.00), (3, 3, 480.00, 450.00);

INSERT INTO Purchase (SupplierID, ProjectID, PurchaseDate, Status, TotalAmount) VALUES
(1, 1, '2023-01-20', 'Delivered', 285000.00),
(2, 1, '2023-02-05', 'Delivered', 57800.00),
(3, 2, '2023-03-15', 'Delivered', 150300.00),
(4, 2, '2023-04-01', 'Delivered', 37920.00);

INSERT INTO PurchaseItem (PurchaseID, MaterialID, Quantity, UnitPrice) VALUES
(1, 1, 2500.00, 82.00), (1, 5, 2000.00, 33.00),
(2, 2, 45.00, 1180.00), (3, 1, 1800.00, 83.50),
(4, 2, 32.00, 1185.00);

INSERT INTO Payment (ProjectID, PayerType, PayeeSupplierID, Amount, PayDate, Method) VALUES
(1, 'CLIENT', NULL, 700000.00, '2023-02-01', 'Bank Transfer'),
(1, 'COMPANY', 1, 271000.00, '2023-01-25', 'Check'),
(2, 'CLIENT', NULL, 525000.00, '2023-04-01', 'Bank Transfer'),
(2, 'COMPANY', 4, 150300.00, '2023-03-20', 'Check');

