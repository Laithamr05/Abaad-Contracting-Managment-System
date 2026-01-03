"""
Database Schema Creation and Seed Data Insertion
Abaad Contracting Management System
"""

import mysql.connector
from mysql.connector import Error
import os
from decimal import Decimal

def get_db_connection():
    """Create and return a MySQL database connection using environment variables."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'root'),
            database=os.getenv('DB_NAME', 'abaad_contracting')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create the database if it doesn't exist."""
    db_name = os.getenv('DB_NAME', 'abaad_contracting')
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")
        print(f"Database '{db_name}' created/selected successfully.")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def create_tables(connection):
    """Create all database tables."""
    cursor = connection.cursor()
    
    try:
        db_name = os.getenv('DB_NAME', 'abaad_contracting')
        cursor.execute(f"USE {db_name}")
        
        # Temporarily disable foreign key checks to allow dropping tables in any order
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Drop tables in reverse dependency order (for clean rebuild)
        # Must drop tables with foreign keys first, then the referenced tables
        drop_statements = [
            "DROP TABLE IF EXISTS Payment",          # References Client, Supplier
            "DROP TABLE IF EXISTS Purchase",         # References Supplier, Material
            "DROP TABLE IF EXISTS Project_Suppliers", # References Project, Supplier
            "DROP TABLE IF EXISTS SupplierMaterial",  # References Supplier, Material
            "DROP TABLE IF EXISTS ProjectMaterial",  # References Project, Material
            "DROP TABLE IF EXISTS Schedule",         # References Project, Phase
            "DROP TABLE IF EXISTS Phase",            # References Project
            "DROP TABLE IF EXISTS Sales",            # References Project, Client
            "DROP TABLE IF EXISTS Contract",         # References Project, Client
            "DROP TABLE IF EXISTS WorkAssignment",    # References Project, Employee
            "DROP TABLE IF EXISTS Project",          # References Branch, Client
            "DROP TABLE IF EXISTS Department",       # References Employee (MUST be before Employee)
            "DROP TABLE IF EXISTS Employee",         # References Branch, Department, Employee, Role
            "DROP TABLE IF EXISTS Material",
            "DROP TABLE IF EXISTS Supplier",
            "DROP TABLE IF EXISTS Client",
            "DROP TABLE IF EXISTS Role",
            "DROP TABLE IF EXISTS Branch"
        ]
        
        for statement in drop_statements:
            cursor.execute(statement)
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Create Branch table
        cursor.execute("""
            CREATE TABLE Branch (
                BranchID INT AUTO_INCREMENT PRIMARY KEY,
                BranchName VARCHAR(100) NOT NULL,
                City VARCHAR(100) NOT NULL,
                Address VARCHAR(255) NOT NULL,
                PhoneNumber VARCHAR(20) NOT NULL
            )
        """)
        
        # Create Role table
        cursor.execute("""
            CREATE TABLE Role (
                RoleID INT AUTO_INCREMENT PRIMARY KEY,
                Title VARCHAR(100) NOT NULL UNIQUE
            )
        """)
        
        # Create Department table
        cursor.execute("""
            CREATE TABLE Department (
                DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
                DepartmentName VARCHAR(100) NOT NULL,
                ManagerID INT NULL
            )
        """)
        
        # Create Employee table (will add FK to Department after Employee creation)
        cursor.execute("""
            CREATE TABLE Employee (
                EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
                EmployeeName VARCHAR(100) NOT NULL,
                PositionID INT NOT NULL,
                Salary DECIMAL(12,2) NOT NULL,
                BranchID INT NOT NULL,
                DepartmentID INT NOT NULL,
                ManagerID INT NULL,
                IsManager BOOLEAN DEFAULT FALSE,
                INDEX idx_branch (BranchID),
                INDEX idx_department (DepartmentID),
                INDEX idx_manager (ManagerID),
                INDEX idx_position (PositionID),
                FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (PositionID) REFERENCES Role(RoleID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Add FK constraint for Department.ManagerID
        cursor.execute("""
            ALTER TABLE Department
            ADD CONSTRAINT fk_dept_manager
            FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL ON UPDATE CASCADE,
            ADD INDEX idx_dept_manager (ManagerID)
        """)
        
        # Create Client table
        cursor.execute("""
            CREATE TABLE Client (
                ClientID INT AUTO_INCREMENT PRIMARY KEY,
                ClientName VARCHAR(100) NOT NULL,
                ContactInfo VARCHAR(255) NOT NULL
            )
        """)
        
        # Create Project table
        cursor.execute("""
            CREATE TABLE Project (
                ProjectID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectName VARCHAR(100) NOT NULL,
                Location VARCHAR(255) NOT NULL,
                Cost DECIMAL(12,2) DEFAULT 0.00,
                Revenue DECIMAL(12,2) NOT NULL,
                ProjectType VARCHAR(50) DEFAULT 'building',
                BranchID INT NOT NULL,
                ClientID INT NOT NULL,
                INDEX idx_branch (BranchID),
                INDEX idx_client (ClientID),
                INDEX idx_project_type (ProjectType),
                FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ClientID) REFERENCES Client(ClientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Material table
        cursor.execute("""
            CREATE TABLE Material (
                MaterialID INT AUTO_INCREMENT PRIMARY KEY,
                MaterialName VARCHAR(100) NOT NULL,
                BaseUnitPrice DECIMAL(12,2) NOT NULL,
                UnitOfMeasure VARCHAR(50) NOT NULL
            )
        """)
        
        # Create Supplier table
        cursor.execute("""
            CREATE TABLE Supplier (
                SupplierID INT AUTO_INCREMENT PRIMARY KEY,
                SupplierName VARCHAR(100) NOT NULL,
                ContactInfo VARCHAR(255) NOT NULL
            )
        """)
        
        # Create WorkAssignment junction table
        cursor.execute("""
            CREATE TABLE WorkAssignment (
                ProjectID INT NOT NULL,
                EmployeeID INT NOT NULL,
                Role VARCHAR(100) NOT NULL,
                HoursWorked DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                PRIMARY KEY (ProjectID, EmployeeID),
                INDEX idx_project (ProjectID),
                INDEX idx_employee (EmployeeID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create ProjectMaterial junction table
        cursor.execute("""
            CREATE TABLE ProjectMaterial (
                ProjectID INT NOT NULL,
                MaterialID INT NOT NULL,
                Quantity DECIMAL(10,2) NOT NULL,
                UnitPrice DECIMAL(12,2) NOT NULL,
                PRIMARY KEY (ProjectID, MaterialID),
                INDEX idx_project (ProjectID),
                INDEX idx_material (MaterialID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create SupplierMaterial junction table
        cursor.execute("""
            CREATE TABLE SupplierMaterial (
                SupplierID INT NOT NULL,
                MaterialID INT NOT NULL,
                Price DECIMAL(12,2) NOT NULL,
                LeadTime INT NULL,
                PRIMARY KEY (SupplierID, MaterialID),
                INDEX idx_supplier (SupplierID),
                INDEX idx_material (MaterialID),
                FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Contract table
        cursor.execute("""
            CREATE TABLE Contract (
                ContractID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectID INT NOT NULL,
                ClientID INT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                TotalValue DECIMAL(12,2) NOT NULL,
                Status VARCHAR(50) DEFAULT 'active',
                INDEX idx_project (ProjectID),
                INDEX idx_client (ClientID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ClientID) REFERENCES Client(ClientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Phase table
        cursor.execute("""
            CREATE TABLE Phase (
                PhaseID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectID INT NOT NULL,
                Name VARCHAR(100) NOT NULL,
                Description TEXT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                Status VARCHAR(50) DEFAULT 'planned',
                INDEX idx_project (ProjectID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Schedule table
        cursor.execute("""
            CREATE TABLE Schedule (
                ScheduleID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectID INT NOT NULL,
                PhaseID INT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NULL,
                TaskDetails TEXT NULL,
                INDEX idx_project (ProjectID),
                INDEX idx_phase (PhaseID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (PhaseID) REFERENCES Phase(PhaseID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Sales table
        cursor.execute("""
            CREATE TABLE Sales (
                SaleID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectID INT NOT NULL,
                ClientID INT NOT NULL,
                Amount DECIMAL(12,2) NOT NULL,
                IssueDate DATE NOT NULL,
                DueDate DATE NULL,
                INDEX idx_project (ProjectID),
                INDEX idx_client (ClientID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (ClientID) REFERENCES Client(ClientID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Project_Suppliers junction table
        cursor.execute("""
            CREATE TABLE Project_Suppliers (
                ProjectID INT NOT NULL,
                SupplierID INT NOT NULL,
                PRIMARY KEY (ProjectID, SupplierID),
                INDEX idx_project (ProjectID),
                INDEX idx_supplier (SupplierID),
                FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Purchase table
        cursor.execute("""
            CREATE TABLE Purchase (
                PurchaseID INT AUTO_INCREMENT PRIMARY KEY,
                SupplierID INT NOT NULL,
                MaterialID INT NOT NULL,
                Quantity DECIMAL(10,2) NOT NULL,
                PurchaseDate DATE NOT NULL,
                TotalCost DECIMAL(12,2) NOT NULL,
                INDEX idx_supplier (SupplierID),
                INDEX idx_material (MaterialID),
                FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (MaterialID) REFERENCES Material(MaterialID) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)
        
        # Create Payment table
        cursor.execute("""
            CREATE TABLE Payment (
                PaymentID INT AUTO_INCREMENT PRIMARY KEY,
                FromClient INT NULL,
                ToSupplier INT NULL,
                Amount DECIMAL(12,2) NOT NULL,
                PaymentDate DATE NOT NULL,
                PaymentMethod VARCHAR(50) NOT NULL,
                INDEX idx_client (FromClient),
                INDEX idx_supplier (ToSupplier),
                FOREIGN KEY (FromClient) REFERENCES Client(ClientID) ON DELETE SET NULL ON UPDATE CASCADE,
                FOREIGN KEY (ToSupplier) REFERENCES Supplier(SupplierID) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)
        
        connection.commit()
        print("All tables created successfully.")
        
    except Error as e:
        print(f"Error creating tables: {e}")
        connection.rollback()
    finally:
        cursor.close()

def insert_seed_data(connection):
    """Insert realistic seed data into all tables."""
    cursor = connection.cursor()
    
    try:
        db_name = os.getenv('DB_NAME', 'abaad_contracting')
        cursor.execute(f"USE {db_name}")
        
        # Insert Branches (Palestinian cities)
        branches = [
            ("Ramallah Main Office", "Ramallah", "6 Hanna Naqara Street", "+970-2-298-9898"),
            ("Nablus Branch", "Nablus", "Main Street, Building 45", "+970-9-234-5678"),
            ("Jerusalem Branch", "Jerusalem", "Salah Eddin Street", "+970-2-234-5678")
        ]
        cursor.executemany("""
            INSERT INTO Branch (BranchName, City, Address, PhoneNumber)
            VALUES (%s, %s, %s, %s)
        """, branches)
        
        # Insert Roles
        roles = [
            ("CEO",),
            ("Construction Director",),
            ("Engineering Manager",),
            ("Procurement Manager",),
            ("Project Manager",),
            ("Senior Engineer",),
            ("Site Engineer",),
            ("Procurement Specialist",),
            ("Quality Inspector",),
            ("Branch Manager",),
            ("Engineer",),
            ("Site Supervisor",),
            ("Planning Specialist",),
            ("Construction Worker",),
            ("Accountant",)
        ]
        cursor.executemany("""
            INSERT INTO Role (Title)
            VALUES (%s)
        """, roles)
        
        # Insert Departments
        departments = [
            ("Construction Management", None),
            ("Engineering", None),
            ("Procurement", None),
            ("Project Planning", None),
            ("Quality Assurance", None)
        ]
        cursor.executemany("""
            INSERT INTO Department (DepartmentName, ManagerID)
            VALUES (%s, %s)
        """, departments)
        
        # Insert Clients
        clients = [
            ("Palestinian Ministry of Health", "contact@moh.gov.ps, +970-2-296-3636"),
            ("Palestinian Central Elections Commission", "info@elections.ps, +970-2-298-1234"),
            ("Palestine Investment Bank", "contact@pib.ps, +970-2-295-5555"),
            ("A.M. Qattan Foundation", "info@qattanfoundation.org, +970-2-296-0544"),
            ("Palestinian Ministry of Education", "contact@mohe.gov.ps, +970-2-298-1234"),
            ("Palestinian Energy Authority", "info@pea.gov.ps, +970-2-298-5678")
        ]
        cursor.executemany("""
            INSERT INTO Client (ClientName, ContactInfo)
            VALUES (%s, %s)
        """, clients)
        
        # Insert Materials
        materials = [
            ("Concrete Mix C30", Decimal("450.00"), "m³"),
            ("Steel Rebar 12mm", Decimal("2800.00"), "ton"),
            ("Cement Portland", Decimal("280.00"), "bag"),
            ("Bricks Red Clay", Decimal("2.50"), "piece"),
            ("Sand Coarse", Decimal("120.00"), "m³"),
            ("Gravel 20mm", Decimal("150.00"), "m³"),
            ("Gypsum Board", Decimal("45.00"), "sheet"),
            ("Electrical Wire 4mm", Decimal("15.50"), "meter"),
            ("PVC Pipe 4 inch", Decimal("85.00"), "meter"),
            ("Paint Acrylic White", Decimal("180.00"), "gallon")
        ]
        cursor.executemany("""
            INSERT INTO Material (MaterialName, BaseUnitPrice, UnitOfMeasure)
            VALUES (%s, %s, %s)
        """, materials)
        
        # Insert Suppliers (Palestinian companies)
        suppliers = [
            ("Palestine Building Materials Co.", "sales@pbmc.ps, +970-2-298-1111"),
            ("Palestinian Steel Corporation", "orders@psc.ps, +970-2-298-2222"),
            ("National Cement Palestine", "contact@ncp.ps, +970-2-298-3333"),
            ("Palestine Trading & Supply", "info@pts.ps, +970-2-298-4444"),
            ("Palestinian Hardware Co.", "sales@phc.ps, +970-2-298-5555")
        ]
        cursor.executemany("""
            INSERT INTO Supplier (SupplierName, ContactInfo)
            VALUES (%s, %s)
        """, suppliers)
        
        connection.commit()
        
        # Insert Employees (must be done after branches, departments, and roles exist)
        # First, get branch, department, and role IDs
        cursor.execute("SELECT BranchID FROM Branch ORDER BY BranchID")
        branch_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DepartmentID FROM Department ORDER BY DepartmentID")
        dept_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT RoleID, Title FROM Role ORDER BY RoleID")
        roles_dict = {row[1]: row[0] for row in cursor.fetchall()}
        
        employees = [
            ("Ahmed Al-Mansouri", roles_dict["CEO"], Decimal("350000.00"), branch_ids[0], dept_ids[0], None, True),
            ("Fatima Al-Zahra", roles_dict["Construction Director"], Decimal("280000.00"), branch_ids[0], dept_ids[0], 1, True),
            ("Khalid Al-Saud", roles_dict["Engineering Manager"], Decimal("240000.00"), branch_ids[0], dept_ids[1], 1, True),
            ("Noura Al-Mutairi", roles_dict["Procurement Manager"], Decimal("220000.00"), branch_ids[0], dept_ids[2], 1, True),
            ("Mohammed Al-Harbi", roles_dict["Project Manager"], Decimal("200000.00"), branch_ids[0], dept_ids[0], 2, True),
            ("Sarah Al-Ghamdi", roles_dict["Senior Engineer"], Decimal("180000.00"), branch_ids[0], dept_ids[1], 3, False),
            ("Omar Al-Qahtani", roles_dict["Site Engineer"], Decimal("150000.00"), branch_ids[0], dept_ids[1], 6, False),
            ("Layla Al-Shammari", roles_dict["Procurement Specialist"], Decimal("140000.00"), branch_ids[0], dept_ids[2], 4, False),
            ("Fahad Al-Otaibi", roles_dict["Quality Inspector"], Decimal("130000.00"), branch_ids[0], dept_ids[4], 2, False),
            ("Reem Al-Dosari", roles_dict["Branch Manager"], Decimal("260000.00"), branch_ids[1], dept_ids[0], 1, True),
            ("Youssef Al-Mazroei", roles_dict["Project Manager"], Decimal("190000.00"), branch_ids[1], dept_ids[0], 10, True),
            ("Maha Al-Fahad", roles_dict["Engineer"], Decimal("160000.00"), branch_ids[1], dept_ids[1], 3, False),
            ("Sultan Al-Anzi", roles_dict["Site Supervisor"], Decimal("120000.00"), branch_ids[1], dept_ids[0], 11, False),
            ("Hanan Al-Rashid", roles_dict["Branch Manager"], Decimal("250000.00"), branch_ids[2], dept_ids[0], 1, True),
            ("Tariq Al-Mutlaq", roles_dict["Project Manager"], Decimal("185000.00"), branch_ids[2], dept_ids[0], 14, True),
            ("Dalal Al-Qasimi", roles_dict["Planning Specialist"], Decimal("145000.00"), branch_ids[2], dept_ids[3], 1, False),
            ("Badr Al-Shahrani", roles_dict["Construction Worker"], Decimal("90000.00"), branch_ids[0], dept_ids[0], 5, False),
            ("Salma Al-Harbi", roles_dict["Construction Worker"], Decimal("95000.00"), branch_ids[0], dept_ids[0], 5, False),
            ("Majid Al-Zahrani", roles_dict["Construction Worker"], Decimal("92000.00"), branch_ids[1], dept_ids[0], 11, False),
            ("Amira Al-Suwaidi", roles_dict["Accountant"], Decimal("110000.00"), branch_ids[0], dept_ids[2], 4, False)
        ]
        
        cursor.executemany("""
            INSERT INTO Employee (EmployeeName, PositionID, Salary, BranchID, DepartmentID, ManagerID, IsManager)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, employees)
        
        connection.commit()
        
        # Update Department ManagerID (now that employees exist)
        cursor.execute("UPDATE Department SET ManagerID = 2 WHERE DepartmentID = 1")  # Construction Management
        cursor.execute("UPDATE Department SET ManagerID = 3 WHERE DepartmentID = 2")  # Engineering
        cursor.execute("UPDATE Department SET ManagerID = 4 WHERE DepartmentID = 3")  # Procurement
        cursor.execute("UPDATE Department SET ManagerID = 16 WHERE DepartmentID = 4")  # Project Planning
        cursor.execute("UPDATE Department SET ManagerID = 9 WHERE DepartmentID = 5")  # Quality Assurance
        
        connection.commit()
        
        # Insert Projects
        cursor.execute("SELECT ClientID FROM Client ORDER BY ClientID")
        client_ids = [row[0] for row in cursor.fetchall()]
        
        # Building Projects from website
        building_projects = [
            ("Construction of the New Cancer Center", "Ramallah", Decimal("25000000.00"), Decimal("30000000.00"), "building", branch_ids[0], client_ids[0]),
            ("The New Central Elections Commission Building", "Ramallah", Decimal("12000000.00"), Decimal("15000000.00"), "building", branch_ids[0], client_ids[1]),
            ("Al Riyadh Student Residences", "Ramallah", Decimal("18000000.00"), Decimal("22000000.00"), "building", branch_ids[0], client_ids[4]),
            ("A.M Qattan Foundation Project", "Al Tireh, Ramallah", Decimal("15000000.00"), Decimal("18000000.00"), "building", branch_ids[0], client_ids[3]),
            ("Palestine Investment Bank HQ", "El-Ersal Main Street, Ramallah", Decimal("20000000.00"), Decimal("24000000.00"), "building", branch_ids[0], client_ids[2]),
            ("Tulkarem Courthouse", "Tulkarem", Decimal("22000000.00"), Decimal("26000000.00"), "building", branch_ids[1], client_ids[1])
        ]
        
        # Solar Projects from website
        solar_projects = [
            ("Solar Power Plant - Jenin", "Jenin", Decimal("15000000.00"), Decimal("18000000.00"), "solar", branch_ids[1], client_ids[5]),
            ("Jericho 7.5 MWp", "Jericho", Decimal("12000000.00"), Decimal("15000000.00"), "solar", branch_ids[2], client_ids[5]),
            ("Saffarin 5.1 Mega Watt Solar Plant", "Saffarin", Decimal("10000000.00"), Decimal("12000000.00"), "solar", branch_ids[1], client_ids[5])
        ]
        
        all_projects = building_projects + solar_projects
        cursor.executemany("""
            INSERT INTO Project (ProjectName, Location, Cost, Revenue, ProjectType, BranchID, ClientID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, all_projects)
        
        connection.commit()
        
        # Insert WorkAssignments
        cursor.execute("SELECT ProjectID FROM Project ORDER BY ProjectID")
        project_ids = [row[0] for row in cursor.fetchall()]
        
        work_assignments = [
            (project_ids[0], 5, "Project Manager", Decimal("320.00"), "2024-01-15", "2024-12-31"),
            (project_ids[0], 6, "Lead Engineer", Decimal("480.00"), "2024-01-20", "2024-11-30"),
            (project_ids[0], 7, "Site Engineer", Decimal("560.00"), "2024-02-01", None),
            (project_ids[0], 17, "Construction Worker", Decimal("1200.00"), "2024-02-15", None),
            (project_ids[0], 18, "Construction Worker", Decimal("1150.00"), "2024-02-15", None),
            (project_ids[1], 11, "Project Manager", Decimal("400.00"), "2024-03-01", "2025-06-30"),
            (project_ids[1], 12, "Engineer", Decimal("520.00"), "2024-03-10", None),
            (project_ids[1], 13, "Site Supervisor", Decimal("680.00"), "2024-03-15", None),
            (project_ids[1], 19, "Construction Worker", Decimal("1400.00"), "2024-04-01", None),
            (project_ids[2], 15, "Project Manager", Decimal("450.00"), "2024-01-01", "2025-12-31"),
            (project_ids[2], 14, "Branch Manager Oversight", Decimal("200.00"), "2024-01-01", None),
            (project_ids[3], 15, "Project Manager", Decimal("280.00"), "2024-05-01", "2024-12-15"),
            (project_ids[4], 5, "Project Manager", Decimal("380.00"), "2024-04-01", "2025-08-31"),
            (project_ids[4], 6, "Lead Engineer", Decimal("440.00"), "2024-04-10", None),
            (project_ids[5], 11, "Project Manager", Decimal("320.00"), "2024-06-01", "2025-03-31"),
            (project_ids[6], 5, "Project Manager", Decimal("350.00"), "2024-02-01", "2025-04-30"),
            (project_ids[6], 8, "Procurement Specialist", Decimal("180.00"), "2024-02-10", None),
            (project_ids[7], 15, "Project Manager", Decimal("300.00"), "2024-03-10", "2024-10-31"),
            (project_ids[7], 12, "Engineer", Decimal("450.00"), "2024-03-15", None),
            (project_ids[7], 8, "Procurement Specialist", Decimal("150.00"), "2024-03-20", None),
            (project_ids[8], 11, "Project Manager", Decimal("280.00"), "2024-04-15", "2024-12-31"),
            (project_ids[8], 12, "Engineer", Decimal("420.00"), "2024-04-20", None),
            (project_ids[8], 13, "Site Supervisor", Decimal("600.00"), "2024-05-01", None)
        ]
        cursor.executemany("""
            INSERT INTO WorkAssignment (ProjectID, EmployeeID, Role, HoursWorked, StartDate, EndDate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, work_assignments)
        
        connection.commit()
        
        # Insert ProjectMaterials
        cursor.execute("SELECT MaterialID FROM Material ORDER BY MaterialID")
        material_ids = [row[0] for row in cursor.fetchall()]
        
        project_materials = [
            (project_ids[0], material_ids[0], Decimal("1200.00"), Decimal("460.00")),
            (project_ids[0], material_ids[1], Decimal("850.00"), Decimal("2850.00")),
            (project_ids[0], material_ids[2], Decimal("5000.00"), Decimal("290.00")),
            (project_ids[0], material_ids[4], Decimal("800.00"), Decimal("125.00")),
            (project_ids[1], material_ids[0], Decimal("2100.00"), Decimal("455.00")),
            (project_ids[1], material_ids[1], Decimal("1200.00"), Decimal("2820.00")),
            (project_ids[1], material_ids[3], Decimal("50000.00"), Decimal("2.60")),
            (project_ids[1], material_ids[5], Decimal("1500.00"), Decimal("155.00")),
            (project_ids[2], material_ids[0], Decimal("3800.00"), Decimal("445.00")),
            (project_ids[2], material_ids[1], Decimal("2800.00"), Decimal("2780.00")),
            (project_ids[2], material_ids[2], Decimal("15000.00"), Decimal("275.00")),
            (project_ids[2], material_ids[7], Decimal("12000.00"), Decimal("16.00")),
            (project_ids[2], material_ids[8], Decimal("8500.00"), Decimal("88.00")),
            (project_ids[3], material_ids[0], Decimal("900.00"), Decimal("465.00")),
            (project_ids[3], material_ids[6], Decimal("3500.00"), Decimal("47.00")),
            (project_ids[3], material_ids[9], Decimal("450.00"), Decimal("185.00")),
            (project_ids[4], material_ids[0], Decimal("2800.00"), Decimal("450.00")),
            (project_ids[4], material_ids[1], Decimal("1800.00"), Decimal("2830.00")),
            (project_ids[4], material_ids[3], Decimal("80000.00"), Decimal("2.55")),
            (project_ids[4], material_ids[6], Decimal("12000.00"), Decimal("46.00")),
            (project_ids[5], material_ids[0], Decimal("1500.00"), Decimal("460.00")),
            (project_ids[5], material_ids[4], Decimal("2000.00"), Decimal("122.00")),
            (project_ids[5], material_ids[5], Decimal("1800.00"), Decimal("152.00")),
            (project_ids[6], material_ids[0], Decimal("2200.00"), Decimal("455.00")),
            (project_ids[6], material_ids[1], Decimal("1400.00"), Decimal("2820.00")),
            (project_ids[6], material_ids[3], Decimal("60000.00"), Decimal("2.58")),
            (project_ids[7], material_ids[0], Decimal("1800.00"), Decimal("450.00")),
            (project_ids[7], material_ids[1], Decimal("1200.00"), Decimal("2800.00")),
            (project_ids[7], material_ids[7], Decimal("10000.00"), Decimal("15.50")),
            (project_ids[7], material_ids[8], Decimal("6000.00"), Decimal("85.00")),
            (project_ids[8], material_ids[0], Decimal("1500.00"), Decimal("445.00")),
            (project_ids[8], material_ids[1], Decimal("1000.00"), Decimal("2780.00")),
            (project_ids[8], material_ids[7], Decimal("8000.00"), Decimal("15.00")),
            (project_ids[8], material_ids[8], Decimal("5000.00"), Decimal("82.00"))
        ]
        cursor.executemany("""
            INSERT INTO ProjectMaterial (ProjectID, MaterialID, Quantity, UnitPrice)
            VALUES (%s, %s, %s, %s)
        """, project_materials)
        
        connection.commit()
        
        # Insert SupplierMaterials
        supplier_materials = [
            (1, material_ids[0], Decimal("440.00"), 7),
            (1, material_ids[2], Decimal("270.00"), 5),
            (1, material_ids[3], Decimal("2.40"), 3),
            (1, material_ids[4], Decimal("115.00"), 2),
            (2, material_ids[1], Decimal("2750.00"), 14),
            (2, material_ids[7], Decimal("15.00"), 10),
            (3, material_ids[2], Decimal("275.00"), 7),
            (3, material_ids[0], Decimal("445.00"), 10),
            (4, material_ids[5], Decimal("145.00"), 4),
            (4, material_ids[8], Decimal("82.00"), 8),
            (4, material_ids[9], Decimal("175.00"), 5),
            (5, material_ids[6], Decimal("43.00"), 3),
            (5, material_ids[7], Decimal("15.50"), 7),
            (5, material_ids[9], Decimal("180.00"), 4),
            (1, material_ids[5], Decimal("148.00"), 3),
            (3, material_ids[4], Decimal("120.00"), 4),
            (2, material_ids[0], Decimal("448.00"), 12)
        ]
        cursor.executemany("""
            INSERT INTO SupplierMaterial (SupplierID, MaterialID, Price, LeadTime)
            VALUES (%s, %s, %s, %s)
        """, supplier_materials)
        
        connection.commit()
        
        # Insert Contracts
        contracts = [
            (project_ids[0], client_ids[0], "2024-01-01", "2024-12-31", Decimal("30000000.00"), "active"),
            (project_ids[1], client_ids[1], "2024-02-01", "2025-06-30", Decimal("15000000.00"), "active"),
            (project_ids[2], client_ids[4], "2024-01-15", "2025-12-31", Decimal("22000000.00"), "active"),
            (project_ids[3], client_ids[3], "2024-03-01", "2024-12-15", Decimal("18000000.00"), "active"),
            (project_ids[4], client_ids[2], "2024-04-01", "2025-08-31", Decimal("24000000.00"), "active"),
            (project_ids[5], client_ids[1], "2024-05-01", "2025-03-31", Decimal("26000000.00"), "active"),
            (project_ids[6], client_ids[5], "2024-02-15", "2024-11-30", Decimal("18000000.00"), "active"),
            (project_ids[7], client_ids[5], "2024-03-10", "2024-10-31", Decimal("15000000.00"), "active"),
            (project_ids[8], client_ids[5], "2024-04-15", "2024-12-31", Decimal("12000000.00"), "active")
        ]
        cursor.executemany("""
            INSERT INTO Contract (ProjectID, ClientID, StartDate, EndDate, TotalValue, Status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, contracts)
        
        connection.commit()
        
        # Insert Phases
        phases = [
            (project_ids[0], "Foundation", "Foundation and structural work", "2024-01-15", "2024-04-30", "completed"),
            (project_ids[0], "Construction", "Main construction phase", "2024-05-01", "2024-10-31", "in_progress"),
            (project_ids[0], "Finishing", "Final finishing and handover", "2024-11-01", "2024-12-31", "planned"),
            (project_ids[1], "Planning", "Project planning and design", "2024-02-01", "2024-03-31", "completed"),
            (project_ids[1], "Construction", "Main construction", "2024-04-01", "2025-05-31", "in_progress"),
            (project_ids[2], "Site Preparation", "Site clearing and preparation", "2024-01-15", "2024-02-28", "completed"),
            (project_ids[2], "Construction", "Building construction", "2024-03-01", "2025-11-30", "in_progress"),
            (project_ids[6], "Installation", "Solar panel installation", "2024-02-15", "2024-08-31", "in_progress"),
            (project_ids[6], "Testing", "System testing and commissioning", "2024-09-01", "2024-11-30", "planned"),
            (project_ids[7], "Site Preparation", "Site clearing and preparation", "2024-03-10", "2024-04-30", "completed"),
            (project_ids[7], "Installation", "Solar panel installation", "2024-05-01", "2024-09-30", "in_progress"),
            (project_ids[7], "Testing", "System testing and commissioning", "2024-10-01", "2024-10-31", "planned"),
            (project_ids[8], "Site Preparation", "Site clearing and preparation", "2024-04-15", "2024-05-31", "completed"),
            (project_ids[8], "Installation", "Solar panel installation", "2024-06-01", "2024-11-30", "in_progress"),
            (project_ids[8], "Testing", "System testing and commissioning", "2024-12-01", "2024-12-31", "planned")
        ]
        cursor.executemany("""
            INSERT INTO Phase (ProjectID, Name, Description, StartDate, EndDate, Status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, phases)
        
        connection.commit()
        
        # Insert Schedules
        cursor.execute("SELECT PhaseID FROM Phase ORDER BY PhaseID")
        phase_ids = [row[0] for row in cursor.fetchall()]
        
        schedules = [
            (project_ids[0], phase_ids[0], "2024-01-15", "2024-02-15", "Excavation and foundation preparation"),
            (project_ids[0], phase_ids[0], "2024-02-16", "2024-03-31", "Foundation pouring and curing"),
            (project_ids[0], phase_ids[1], "2024-05-01", "2024-07-31", "Structural framework construction"),
            (project_ids[0], phase_ids[1], "2024-08-01", "2024-10-31", "Building envelope and MEP installation"),
            (project_ids[1], phase_ids[3], "2024-02-01", "2024-02-28", "Design finalization"),
            (project_ids[1], phase_ids[3], "2024-03-01", "2024-03-31", "Permit acquisition"),
            (project_ids[2], phase_ids[5], "2024-01-15", "2024-01-31", "Site survey and clearing"),
            (project_ids[2], phase_ids[5], "2024-02-01", "2024-02-28", "Utility connections"),
            (project_ids[6], phase_ids[7], "2024-02-15", "2024-05-31", "Mounting structure installation"),
            (project_ids[6], phase_ids[7], "2024-06-01", "2024-08-31", "Panel installation and wiring")
        ]
        cursor.executemany("""
            INSERT INTO Schedule (ProjectID, PhaseID, StartDate, EndDate, TaskDetails)
            VALUES (%s, %s, %s, %s, %s)
        """, schedules)
        
        connection.commit()
        
        # Insert Sales
        sales = [
            (project_ids[0], client_ids[0], Decimal("30000000.00"), "2024-01-01", "2024-12-31"),
            (project_ids[1], client_ids[1], Decimal("15000000.00"), "2024-02-01", "2025-06-30"),
            (project_ids[2], client_ids[4], Decimal("22000000.00"), "2024-01-15", "2025-12-31"),
            (project_ids[3], client_ids[3], Decimal("18000000.00"), "2024-03-01", "2024-12-15"),
            (project_ids[4], client_ids[2], Decimal("24000000.00"), "2024-04-01", "2025-08-31"),
            (project_ids[5], client_ids[1], Decimal("26000000.00"), "2024-05-01", "2025-03-31"),
            (project_ids[6], client_ids[5], Decimal("18000000.00"), "2024-02-15", "2024-11-30"),
            (project_ids[7], client_ids[5], Decimal("15000000.00"), "2024-03-10", "2024-10-31"),
            (project_ids[8], client_ids[5], Decimal("12000000.00"), "2024-04-15", "2024-12-31")
        ]
        cursor.executemany("""
            INSERT INTO Sales (ProjectID, ClientID, Amount, IssueDate, DueDate)
            VALUES (%s, %s, %s, %s, %s)
        """, sales)
        
        connection.commit()
        
        # Insert Project_Suppliers
        cursor.execute("SELECT SupplierID FROM Supplier ORDER BY SupplierID")
        supplier_ids = [row[0] for row in cursor.fetchall()]
        
        project_suppliers = [
            (project_ids[0], supplier_ids[0]),
            (project_ids[0], supplier_ids[1]),
            (project_ids[0], supplier_ids[2]),
            (project_ids[1], supplier_ids[0]),
            (project_ids[1], supplier_ids[3]),
            (project_ids[2], supplier_ids[1]),
            (project_ids[2], supplier_ids[2]),
            (project_ids[2], supplier_ids[4]),
            (project_ids[3], supplier_ids[0]),
            (project_ids[3], supplier_ids[4]),
            (project_ids[4], supplier_ids[1]),
            (project_ids[4], supplier_ids[2]),
            (project_ids[5], supplier_ids[0]),
            (project_ids[6], supplier_ids[3]),
            (project_ids[6], supplier_ids[4]),
            (project_ids[7], supplier_ids[2]),
            (project_ids[7], supplier_ids[4]),
            (project_ids[8], supplier_ids[1]),
            (project_ids[8], supplier_ids[3])
        ]
        cursor.executemany("""
            INSERT INTO Project_Suppliers (ProjectID, SupplierID)
            VALUES (%s, %s)
        """, project_suppliers)
        
        connection.commit()
        
        # Insert Purchases
        purchases = [
            (supplier_ids[0], material_ids[0], Decimal("500.00"), "2024-01-10", Decimal("225000.00")),
            (supplier_ids[0], material_ids[2], Decimal("3000.00"), "2024-01-12", Decimal("840000.00")),
            (supplier_ids[1], material_ids[1], Decimal("200.00"), "2024-02-01", Decimal("560000.00")),
            (supplier_ids[2], material_ids[2], Decimal("2000.00"), "2024-02-15", Decimal("560000.00")),
            (supplier_ids[3], material_ids[5], Decimal("1000.00"), "2024-03-01", Decimal("150000.00")),
            (supplier_ids[4], material_ids[6], Decimal("5000.00"), "2024-03-10", Decimal("225000.00")),
            (supplier_ids[0], material_ids[3], Decimal("10000.00"), "2024-04-01", Decimal("25000.00")),
            (supplier_ids[1], material_ids[7], Decimal("8000.00"), "2024-04-15", Decimal("124000.00")),
            (supplier_ids[2], material_ids[4], Decimal("1500.00"), "2024-05-01", Decimal("180000.00")),
            (supplier_ids[3], material_ids[8], Decimal("2000.00"), "2024-05-10", Decimal("170000.00"))
        ]
        cursor.executemany("""
            INSERT INTO Purchase (SupplierID, MaterialID, Quantity, PurchaseDate, TotalCost)
            VALUES (%s, %s, %s, %s, %s)
        """, purchases)
        
        connection.commit()
        
        # Insert Payments
        payments = [
            (client_ids[0], None, Decimal("5000000.00"), "2024-01-15", "Bank Transfer"),
            (client_ids[1], None, Decimal("3000000.00"), "2024-02-10", "Check"),
            (client_ids[2], None, Decimal("4000000.00"), "2024-04-15", "Bank Transfer"),
            (None, supplier_ids[0], Decimal("1000000.00"), "2024-01-20", "Bank Transfer"),
            (None, supplier_ids[1], Decimal("800000.00"), "2024-02-05", "Check"),
            (None, supplier_ids[2], Decimal("600000.00"), "2024-02-20", "Bank Transfer"),
            (client_ids[4], None, Decimal("3500000.00"), "2024-01-20", "Bank Transfer"),
            (None, supplier_ids[3], Decimal("400000.00"), "2024-03-15", "Check"),
            (None, supplier_ids[4], Decimal("500000.00"), "2024-03-25", "Bank Transfer")
        ]
        cursor.executemany("""
            INSERT INTO Payment (FromClient, ToSupplier, Amount, PaymentDate, PaymentMethod)
            VALUES (%s, %s, %s, %s, %s)
        """, payments)
        
        connection.commit()
        print("Seed data inserted successfully.")
        
    except Error as e:
        print(f"Error inserting seed data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to create database schema and insert seed data."""
    print("Starting database setup...")
    
    # First, connect without database to create it
    try:
        temp_conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'root')
        )
        create_database(temp_conn)
        temp_conn.close()
    except Error as e:
        print(f"Error in initial connection: {e}")
        return
    
    # Now connect to the database
    connection = get_db_connection()
    if connection:
        try:
            create_tables(connection)
            insert_seed_data(connection)
            print("Database setup completed successfully!")
        except Error as e:
            print(f"Error during setup: {e}")
        finally:
            if connection.is_connected():
                connection.close()
                print("Database connection closed.")
    else:
        print("Failed to establish database connection.")

if __name__ == "__main__":
    main()

