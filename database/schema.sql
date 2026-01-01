-- Abaad Contracting Company Database Schema
-- MySQL 8.0+

DROP DATABASE IF EXISTS abaad_contracting;
CREATE DATABASE abaad_contracting;
USE abaad_contracting;

SET SQL_SAFE_UPDATES = 0;

CREATE TABLE Role (
    RoleID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(50) UNIQUE NOT NULL,
    Description TEXT,
    INDEX idx_title (Title)
);

CREATE TABLE Branch (
    BranchID INT PRIMARY KEY AUTO_INCREMENT,
    BranchName VARCHAR(100) NOT NULL,
    City VARCHAR(50) NOT NULL,
    Address VARCHAR(200),
    PhoneNumber VARCHAR(20),
    INDEX idx_city (City)
);

CREATE TABLE Department (
    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentName VARCHAR(100) NOT NULL,
    ManagerID INT NULL,
    INDEX idx_name (DepartmentName)
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeName VARCHAR(100) NOT NULL,
    RoleID INT NOT NULL,
    Salary DECIMAL(12,2) NOT NULL CHECK (Salary >= 0),
    BranchID INT NOT NULL,
    DepartmentID INT NOT NULL,
    ManagerID INT NULL,
    HireDate DATE NOT NULL,
    Email VARCHAR(100),
    PhoneNumber VARCHAR(20),
    FOREIGN KEY (RoleID) REFERENCES Role(RoleID) ON DELETE RESTRICT,
    FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT,
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE RESTRICT,
    FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL,
    INDEX idx_branch (BranchID),
    INDEX idx_department (DepartmentID),
    INDEX idx_manager (ManagerID),
    INDEX idx_role (RoleID)
);

ALTER TABLE Department
ADD CONSTRAINT fk_department_manager
FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL;

CREATE TABLE BranchManager (
    BranchID INT PRIMARY KEY,
    EmployeeID INT NOT NULL UNIQUE,
    AssignedDate DATE NOT NULL,
    FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE
);

CREATE TABLE Client (
    ClientID INT PRIMARY KEY AUTO_INCREMENT,
    ClientName VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(200),
    Email VARCHAR(100),
    PhoneNumber VARCHAR(20),
    INDEX idx_name (ClientName)
);

CREATE TABLE Project (
    ProjectID INT PRIMARY KEY AUTO_INCREMENT,
    ProjectName VARCHAR(100) NOT NULL,
    Location VARCHAR(200),
    Cost DECIMAL(12,2) DEFAULT 0 CHECK (Cost >= 0),
    Revenue DECIMAL(12,2) DEFAULT 0 CHECK (Revenue >= 0),
    BranchID INT NOT NULL,
    ClientID INT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    Status ENUM('Planning', 'Active', 'On Hold', 'Completed', 'Cancelled') DEFAULT 'Planning',
    FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT,
    FOREIGN KEY (ClientID) REFERENCES Client(ClientID) ON DELETE RESTRICT,
    CONSTRAINT chk_end_after_start CHECK (EndDate IS NULL OR EndDate >= StartDate),
    INDEX idx_branch (BranchID),
    INDEX idx_client (ClientID),
    INDEX idx_status (Status),
    INDEX idx_dates (StartDate, EndDate)
);

CREATE TABLE WorkAssignment (
    ProjectID INT NOT NULL,
    EmployeeID INT NOT NULL,
    Role VARCHAR(50) NOT NULL,
    HoursWorked DECIMAL(8,2) NOT NULL DEFAULT 0 CHECK (HoursWorked >= 0),
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    PRIMARY KEY (ProjectID, EmployeeID),
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    CONSTRAINT chk_work_end_after_start CHECK (EndDate IS NULL OR EndDate >= StartDate),
    INDEX idx_project (ProjectID),
    INDEX idx_employee (EmployeeID)
);

CREATE TABLE Material (
    MaterialID INT PRIMARY KEY AUTO_INCREMENT,
    MaterialName VARCHAR(100) NOT NULL,
    BaseUnitPrice DECIMAL(12,2) NOT NULL CHECK (BaseUnitPrice >= 0),
    UnitOfMeasure VARCHAR(20) NOT NULL,
    INDEX idx_name (MaterialName)
);

CREATE TABLE ProjectMaterial (
    ProjectID INT NOT NULL,
    MaterialID INT NOT NULL,
    Quantity DECIMAL(10,2) NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(12,2) NOT NULL CHECK (UnitPrice >= 0),
    PRIMARY KEY (ProjectID, MaterialID),
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE,
    INDEX idx_project (ProjectID),
    INDEX idx_material (MaterialID)
);

CREATE TABLE Supplier (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(200),
    Email VARCHAR(100),
    PhoneNumber VARCHAR(20),
    INDEX idx_name (SupplierName)
);

CREATE TABLE SupplierMaterial (
    SupplierID INT NOT NULL,
    MaterialID INT NOT NULL,
    Price DECIMAL(12,2) NOT NULL CHECK (Price >= 0),
    LeadTime INT NULL CHECK (LeadTime >= 0),
    PRIMARY KEY (SupplierID, MaterialID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE,
    INDEX idx_supplier (SupplierID),
    INDEX idx_material (MaterialID)
);

CREATE TABLE Purchase (
    PurchaseID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierID INT NOT NULL,
    ProjectID INT NULL,
    PurchaseDate DATE NOT NULL,
    Status ENUM('Pending', 'Confirmed', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    TotalAmount DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (TotalAmount >= 0),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE RESTRICT,
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE SET NULL,
    INDEX idx_supplier (SupplierID),
    INDEX idx_project (ProjectID),
    INDEX idx_date (PurchaseDate),
    INDEX idx_status (Status)
);

CREATE TABLE PurchaseItem (
    PurchaseID INT NOT NULL,
    MaterialID INT NOT NULL,
    Quantity DECIMAL(10,2) NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(12,2) NOT NULL CHECK (UnitPrice >= 0),
    PRIMARY KEY (PurchaseID, MaterialID),
    FOREIGN KEY (PurchaseID) REFERENCES Purchase(PurchaseID) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE,
    INDEX idx_purchase (PurchaseID),
    INDEX idx_material (MaterialID)
);

CREATE TABLE Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    ProjectID INT NULL,
    PayerType ENUM('CLIENT', 'COMPANY') NOT NULL,
    PayeeSupplierID INT NULL,
    Amount DECIMAL(12,2) NOT NULL CHECK (Amount > 0),
    PayDate DATE NOT NULL,
    Method VARCHAR(50),
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE SET NULL,
    FOREIGN KEY (PayeeSupplierID) REFERENCES Supplier(SupplierID) ON DELETE SET NULL,
    INDEX idx_project (ProjectID),
    INDEX idx_supplier (PayeeSupplierID),
    INDEX idx_payer_type (PayerType),
    INDEX idx_date (PayDate)
);

SET SQL_SAFE_UPDATES = 1;

