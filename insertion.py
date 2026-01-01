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
        
        # Drop tables in reverse dependency order (for clean rebuild)
        drop_statements = [
            "DROP TABLE IF EXISTS SupplierMaterial",
            "DROP TABLE IF EXISTS ProjectMaterial",
            "DROP TABLE IF EXISTS WorkAssignment",
            "DROP TABLE IF EXISTS Project",
            "DROP TABLE IF EXISTS Material",
            "DROP TABLE IF EXISTS Supplier",
            "DROP TABLE IF EXISTS Employee",
            "DROP TABLE IF EXISTS Department",
            "DROP TABLE IF EXISTS Client",
            "DROP TABLE IF EXISTS Branch"
        ]
        
        for statement in drop_statements:
            cursor.execute(statement)
        
        # Create Branch table
        cursor.execute("""
            CREATE TABLE Branch (
                BranchID INT AUTO_INCREMENT PRIMARY KEY,
                BranchName VARCHAR(100) NOT NULL,
                City VARCHAR(100) NOT NULL,
                Address VARCHAR(255) NOT NULL,
                PhoneNumber VARCHAR(20) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create Department table
        cursor.execute("""
            CREATE TABLE Department (
                DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
                DepartmentName VARCHAR(100) NOT NULL,
                ManagerID INT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create Employee table (will add FK to Department after Employee creation)
        cursor.execute("""
            CREATE TABLE Employee (
                EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
                EmployeeName VARCHAR(100) NOT NULL,
                Position VARCHAR(100) NOT NULL,
                Salary DECIMAL(12,2) NOT NULL,
                BranchID INT NOT NULL,
                DepartmentID INT NOT NULL,
                ManagerID INT NULL,
                IsManager BOOLEAN DEFAULT FALSE,
                INDEX idx_branch (BranchID),
                INDEX idx_department (DepartmentID),
                INDEX idx_manager (ManagerID),
                FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create Project table
        cursor.execute("""
            CREATE TABLE Project (
                ProjectID INT AUTO_INCREMENT PRIMARY KEY,
                ProjectName VARCHAR(100) NOT NULL,
                Location VARCHAR(255) NOT NULL,
                Cost DECIMAL(12,2) DEFAULT 0.00,
                Revenue DECIMAL(12,2) NOT NULL,
                BranchID INT NOT NULL,
                ClientID INT NOT NULL,
                INDEX idx_branch (BranchID),
                INDEX idx_client (ClientID),
                FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (ClientID) REFERENCES Client(ClientID) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create Material table
        cursor.execute("""
            CREATE TABLE Material (
                MaterialID INT AUTO_INCREMENT PRIMARY KEY,
                MaterialName VARCHAR(100) NOT NULL,
                BaseUnitPrice DECIMAL(12,2) NOT NULL,
                UnitOfMeasure VARCHAR(50) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create Supplier table
        cursor.execute("""
            CREATE TABLE Supplier (
                SupplierID INT AUTO_INCREMENT PRIMARY KEY,
                SupplierName VARCHAR(100) NOT NULL,
                ContactInfo VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
        
        # Insert Branches
        branches = [
            ("Riyadh Main Office", "Riyadh", "King Fahd Road, Building 123", "+966-11-234-5678"),
            ("Jeddah Branch", "Jeddah", "Corniche Road, Tower A", "+966-12-345-6789"),
            ("Dammam Branch", "Dammam", "Prince Sultan Street, Block 5", "+966-13-456-7890")
        ]
        cursor.executemany("""
            INSERT INTO Branch (BranchName, City, Address, PhoneNumber)
            VALUES (%s, %s, %s, %s)
        """, branches)
        
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
            ("Al-Rashid Construction Group", "contact@alrashid.com, +966-11-111-1111"),
            ("Saudi Development Corporation", "info@sdc.com.sa, +966-11-222-2222"),
            ("Kingdom Real Estate", "projects@kingdomre.com, +966-11-333-3333"),
            ("National Infrastructure Authority", "procurement@nia.gov.sa, +966-11-444-4444"),
            ("Gulf Commercial Group", "business@gulfcommercial.com, +966-11-555-5555")
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
        
        # Insert Suppliers
        suppliers = [
            ("Al-Badr Building Materials", "sales@albadr.com, +966-11-777-7777"),
            ("Saudi Steel Corporation", "orders@saudisteel.com, +966-11-888-8888"),
            ("National Cement Company", "contact@ncc.com.sa, +966-11-999-9999"),
            ("Gulf Trading & Supply", "info@gulftrading.com, +966-11-101-1010"),
            ("Arabian Hardware Co.", "sales@arabianhw.com, +966-11-202-2020")
        ]
        cursor.executemany("""
            INSERT INTO Supplier (SupplierName, ContactInfo)
            VALUES (%s, %s)
        """, suppliers)
        
        connection.commit()
        
        # Insert Employees (must be done after branches and departments exist)
        # First, get branch and department IDs
        cursor.execute("SELECT BranchID FROM Branch ORDER BY BranchID")
        branch_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DepartmentID FROM Department ORDER BY DepartmentID")
        dept_ids = [row[0] for row in cursor.fetchall()]
        
        employees = [
            ("Ahmed Al-Mansouri", "CEO", Decimal("350000.00"), branch_ids[0], dept_ids[0], None, True),
            ("Fatima Al-Zahra", "Construction Director", Decimal("280000.00"), branch_ids[0], dept_ids[0], 1, True),
            ("Khalid Al-Saud", "Engineering Manager", Decimal("240000.00"), branch_ids[0], dept_ids[1], 1, True),
            ("Noura Al-Mutairi", "Procurement Manager", Decimal("220000.00"), branch_ids[0], dept_ids[2], 1, True),
            ("Mohammed Al-Harbi", "Project Manager", Decimal("200000.00"), branch_ids[0], dept_ids[0], 2, True),
            ("Sarah Al-Ghamdi", "Senior Engineer", Decimal("180000.00"), branch_ids[0], dept_ids[1], 3, False),
            ("Omar Al-Qahtani", "Site Engineer", Decimal("150000.00"), branch_ids[0], dept_ids[1], 6, False),
            ("Layla Al-Shammari", "Procurement Specialist", Decimal("140000.00"), branch_ids[0], dept_ids[2], 4, False),
            ("Fahad Al-Otaibi", "Quality Inspector", Decimal("130000.00"), branch_ids[0], dept_ids[4], 2, False),
            ("Reem Al-Dosari", "Branch Manager Jeddah", Decimal("260000.00"), branch_ids[1], dept_ids[0], 1, True),
            ("Youssef Al-Mazroei", "Project Manager", Decimal("190000.00"), branch_ids[1], dept_ids[0], 10, True),
            ("Maha Al-Fahad", "Engineer", Decimal("160000.00"), branch_ids[1], dept_ids[1], 3, False),
            ("Sultan Al-Anzi", "Site Supervisor", Decimal("120000.00"), branch_ids[1], dept_ids[0], 11, False),
            ("Hanan Al-Rashid", "Branch Manager Dammam", Decimal("250000.00"), branch_ids[2], dept_ids[0], 1, True),
            ("Tariq Al-Mutlaq", "Project Manager", Decimal("185000.00"), branch_ids[2], dept_ids[0], 14, True),
            ("Dalal Al-Qasimi", "Planning Specialist", Decimal("145000.00"), branch_ids[2], dept_ids[3], 1, False),
            ("Badr Al-Shahrani", "Construction Worker", Decimal("90000.00"), branch_ids[0], dept_ids[0], 5, False),
            ("Salma Al-Harbi", "Construction Worker", Decimal("95000.00"), branch_ids[0], dept_ids[0], 5, False),
            ("Majid Al-Zahrani", "Construction Worker", Decimal("92000.00"), branch_ids[1], dept_ids[0], 11, False),
            ("Amira Al-Suwaidi", "Accountant", Decimal("110000.00"), branch_ids[0], dept_ids[2], 4, False)
        ]
        
        cursor.executemany("""
            INSERT INTO Employee (EmployeeName, Position, Salary, BranchID, DepartmentID, ManagerID, IsManager)
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
        
        projects = [
            ("Riyadh Tower Complex", "King Fahd Road, Riyadh", Decimal("15000000.00"), Decimal("18000000.00"), branch_ids[0], client_ids[0]),
            ("Jeddah Residential District", "Al-Balad Area, Jeddah", Decimal("25000000.00"), Decimal("30000000.00"), branch_ids[1], client_ids[1]),
            ("Dammam Industrial Plant", "Industrial City, Dammam", Decimal("45000000.00"), Decimal("52000000.00"), branch_ids[2], client_ids[2]),
            ("Al-Khobar Office Building", "Corniche Road, Al-Khobar", Decimal("12000000.00"), Decimal("15000000.00"), branch_ids[2], client_ids[3]),
            ("Riyadh Shopping Mall", "Northern Ring Road, Riyadh", Decimal("35000000.00"), Decimal("42000000.00"), branch_ids[0], client_ids[4]),
            ("Jeddah Infrastructure Upgrade", "Various Locations, Jeddah", Decimal("18000000.00"), Decimal("22000000.00"), branch_ids[1], client_ids[3]),
            ("Riyadh Housing Development", "Al-Naseem District, Riyadh", Decimal("28000000.00"), Decimal("34000000.00"), branch_ids[0], client_ids[0])
        ]
        cursor.executemany("""
            INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, projects)
        
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
            (project_ids[6], 8, "Procurement Specialist", Decimal("180.00"), "2024-02-10", None)
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
            (project_ids[6], material_ids[3], Decimal("60000.00"), Decimal("2.58"))
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

