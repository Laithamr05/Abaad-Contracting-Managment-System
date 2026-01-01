"""
Flask Application for Abaad Contracting Management System
Main application file with routes and database operations
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
import os
from decimal import Decimal
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_db_connection():
    """Create and return a MySQL database connection."""
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

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results."""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        else:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        connection.close()
        return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page / Dashboard"""
    stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM Branch) as branch_count,
            (SELECT COUNT(*) FROM Employee) as employee_count,
            (SELECT COUNT(*) FROM Project) as project_count,
            (SELECT COUNT(*) FROM Client) as client_count,
            (SELECT SUM(Revenue) FROM Project) as total_revenue,
            (SELECT COUNT(*) FROM Supplier) as supplier_count
    """
    stats = execute_query(stats_query)
    
    recent_projects_query = """
        SELECT p.ProjectID, p.ProjectName, p.Location, p.Revenue, 
               b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        ORDER BY p.ProjectID DESC
        LIMIT 5
    """
    recent_projects = execute_query(recent_projects_query) or []
    
    return render_template('index.html', stats=stats[0] if stats else {}, recent_projects=recent_projects)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page (optional authentication)"""
    if request.method == 'POST':
        # Simple authentication (can be enhanced)
        username = request.form.get('username')
        password = request.form.get('password')
        
        # For demo purposes, accept any credentials
        if username and password:
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter both username and password', 'error')
    
    return render_template('login.html')

@app.route('/error')
def error_page():
    """Error page"""
    error_msg = request.args.get('msg', 'An error occurred')
    return render_template('error.html', error_msg=error_msg)

# ==================== BRANCHES ====================

@app.route('/branches')
def branches():
    """List and manage branches"""
    query = """
        SELECT b.*, 
               COUNT(DISTINCT e.EmployeeID) as employee_count,
               COUNT(DISTINCT p.ProjectID) as project_count
        FROM Branch b
        LEFT JOIN Employee e ON b.BranchID = e.BranchID
        LEFT JOIN Project p ON b.BranchID = p.BranchID
        GROUP BY b.BranchID
        ORDER BY b.BranchName
    """
    branches = execute_query(query) or []
    return render_template('branches.html', branches=branches)

@app.route('/branches/add', methods=['POST'])
def add_branch():
    """Add a new branch"""
    branch_name = request.form.get('branch_name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    query = "INSERT INTO Branch (BranchName, City, Address, PhoneNumber) VALUES (%s, %s, %s, %s)"
    result = execute_query(query, (branch_name, city, address, phone), fetch=False)
    
    if result:
        flash('Branch added successfully!', 'success')
    else:
        flash('Error adding branch', 'error')
    
    return redirect(url_for('branches'))

# ==================== EMPLOYEES ====================

@app.route('/employees')
def employees():
    """List and manage employees"""
    query = """
        SELECT e.*, b.BranchName, d.DepartmentName,
               m.EmployeeName as ManagerName
        FROM Employee e
        JOIN Branch b ON e.BranchID = b.BranchID
        JOIN Department d ON e.DepartmentID = d.DepartmentID
        LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
        ORDER BY e.EmployeeName
    """
    employees = execute_query(query) or []
    
    # Get branches and departments for forms
    branches = execute_query("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName") or []
    departments = execute_query("SELECT DepartmentID, DepartmentName FROM Department ORDER BY DepartmentName") or []
    managers = execute_query("SELECT EmployeeID, EmployeeName FROM Employee WHERE IsManager = TRUE ORDER BY EmployeeName") or []
    
    return render_template('employees.html', employees=employees, branches=branches, 
                         departments=departments, managers=managers)

@app.route('/employees/add', methods=['POST'])
def add_employee():
    """Add a new employee"""
    name = request.form.get('employee_name')
    position = request.form.get('position')
    salary = request.form.get('salary')
    branch_id = request.form.get('branch_id')
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    is_manager = request.form.get('is_manager') == 'on'
    
    query = """
        INSERT INTO Employee (EmployeeName, Position, Salary, BranchID, DepartmentID, ManagerID, IsManager)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    result = execute_query(query, (name, position, salary, branch_id, dept_id, manager_id, is_manager), fetch=False)
    
    if result:
        flash('Employee added successfully!', 'success')
    else:
        flash('Error adding employee', 'error')
    
    return redirect(url_for('employees'))

# ==================== DEPARTMENTS ====================

@app.route('/departments')
def departments():
    """List and manage departments"""
    query = """
        SELECT d.*, e.EmployeeName as ManagerName,
               COUNT(DISTINCT emp.EmployeeID) as employee_count
        FROM Department d
        LEFT JOIN Employee e ON d.ManagerID = e.EmployeeID
        LEFT JOIN Employee emp ON d.DepartmentID = emp.DepartmentID
        GROUP BY d.DepartmentID
        ORDER BY d.DepartmentName
    """
    departments = execute_query(query) or []
    
    employees = execute_query("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName") or []
    
    return render_template('departments.html', departments=departments, employees=employees)

@app.route('/departments/set_manager', methods=['POST'])
def set_department_manager():
    """Set department manager"""
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    
    query = "UPDATE Department SET ManagerID = %s WHERE DepartmentID = %s"
    result = execute_query(query, (manager_id, dept_id), fetch=False)
    
    if result:
        flash('Department manager updated successfully!', 'success')
    else:
        flash('Error updating department manager', 'error')
    
    return redirect(url_for('departments'))

# ==================== CLIENTS ====================

@app.route('/clients')
def clients():
    """List and manage clients"""
    query = """
        SELECT c.*, COUNT(DISTINCT p.ProjectID) as project_count
        FROM Client c
        LEFT JOIN Project p ON c.ClientID = p.ClientID
        GROUP BY c.ClientID
        ORDER BY c.ClientName
    """
    clients = execute_query(query) or []
    return render_template('clients.html', clients=clients)

@app.route('/clients/add', methods=['POST'])
def add_client():
    """Add a new client"""
    name = request.form.get('client_name')
    contact = request.form.get('contact_info')
    
    query = "INSERT INTO Client (ClientName, ContactInfo) VALUES (%s, %s)"
    result = execute_query(query, (name, contact), fetch=False)
    
    if result:
        flash('Client added successfully!', 'success')
    else:
        flash('Error adding client', 'error')
    
    return redirect(url_for('clients'))

# ==================== PROJECTS ====================

@app.route('/projects')
def projects():
    """List all projects"""
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        ORDER BY p.ProjectID DESC
    """
    projects = execute_query(query) or []
    
    branches = execute_query("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName") or []
    clients = execute_query("SELECT ClientID, ClientName FROM Client ORDER BY ClientName") or []
    
    return render_template('projects.html', projects=projects, branches=branches, clients=clients)

@app.route('/projects/<int:project_id>')
def project_details(project_id):
    """Project details page"""
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        WHERE p.ProjectID = %s
    """
    project = execute_query(query, (project_id,))
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects'))
    
    # Get work assignments
    assignments_query = """
        SELECT wa.*, e.EmployeeName, e.Position
        FROM WorkAssignment wa
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        WHERE wa.ProjectID = %s
    """
    assignments = execute_query(assignments_query, (project_id,)) or []
    
    # Get materials
    materials_query = """
        SELECT pm.*, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Material m ON pm.MaterialID = m.MaterialID
        WHERE pm.ProjectID = %s
    """
    materials = execute_query(materials_query, (project_id,)) or []
    
    return render_template('manage_project.html', project=project[0], assignments=assignments, materials=materials)

@app.route('/projects/add', methods=['POST'])
def add_project():
    """Add a new project"""
    name = request.form.get('project_name')
    location = request.form.get('location')
    cost = request.form.get('cost') or 0
    revenue = request.form.get('revenue')
    branch_id = request.form.get('branch_id')
    client_id = request.form.get('client_id')
    
    query = """
        INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    result = execute_query(query, (name, location, cost, revenue, branch_id, client_id), fetch=False)
    
    if result:
        flash('Project added successfully!', 'success')
    else:
        flash('Error adding project', 'error')
    
    return redirect(url_for('projects'))

# ==================== SUPPLIERS ====================

@app.route('/suppliers')
def suppliers():
    """List and manage suppliers"""
    query = """
        SELECT s.*, COUNT(DISTINCT sm.MaterialID) as material_count
        FROM Supplier s
        LEFT JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
        GROUP BY s.SupplierID
        ORDER BY s.SupplierName
    """
    suppliers = execute_query(query) or []
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    """Add a new supplier"""
    name = request.form.get('supplier_name')
    contact = request.form.get('contact_info')
    
    query = "INSERT INTO Supplier (SupplierName, ContactInfo) VALUES (%s, %s)"
    result = execute_query(query, (name, contact), fetch=False)
    
    if result:
        flash('Supplier added successfully!', 'success')
    else:
        flash('Error adding supplier', 'error')
    
    return redirect(url_for('suppliers'))

# ==================== MATERIALS ====================

@app.route('/materials')
def materials():
    """List and manage materials"""
    query = "SELECT * FROM Material ORDER BY MaterialName"
    materials = execute_query(query) or []
    return render_template('materials.html', materials=materials)

@app.route('/materials/add', methods=['POST'])
def add_material():
    """Add a new material"""
    name = request.form.get('material_name')
    base_price = request.form.get('base_unit_price')
    unit = request.form.get('unit_of_measure')
    
    query = "INSERT INTO Material (MaterialName, BaseUnitPrice, UnitOfMeasure) VALUES (%s, %s, %s)"
    result = execute_query(query, (name, base_price, unit), fetch=False)
    
    if result:
        flash('Material added successfully!', 'success')
    else:
        flash('Error adding material', 'error')
    
    return redirect(url_for('materials'))

# ==================== WORK ASSIGNMENTS ====================

@app.route('/work_assignments')
def work_assignments():
    """Manage work assignments (employees to projects)"""
    query = """
        SELECT wa.*, p.ProjectName, e.EmployeeName, e.Position
        FROM WorkAssignment wa
        JOIN Project p ON wa.ProjectID = p.ProjectID
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        ORDER BY wa.StartDate DESC
    """
    assignments = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    employees = execute_query("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName") or []
    
    return render_template('work_assignments.html', assignments=assignments, projects=projects, employees=employees)

@app.route('/work_assignments/add', methods=['POST'])
def add_work_assignment():
    """Add a new work assignment"""
    project_id = request.form.get('project_id')
    employee_id = request.form.get('employee_id')
    role = request.form.get('role')
    hours = request.form.get('hours_worked') or 0
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    
    query = """
        INSERT INTO WorkAssignment (ProjectID, EmployeeID, Role, HoursWorked, StartDate, EndDate)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Role = VALUES(Role), HoursWorked = VALUES(HoursWorked),
        StartDate = VALUES(StartDate), EndDate = VALUES(EndDate)
    """
    result = execute_query(query, (project_id, employee_id, role, hours, start_date, end_date), fetch=False)
    
    if result:
        flash('Work assignment added/updated successfully!', 'success')
    else:
        flash('Error adding work assignment', 'error')
    
    return redirect(url_for('work_assignments'))

# ==================== PROJECT MATERIALS ====================

@app.route('/project_materials')
def project_materials():
    """Manage project materials"""
    query = """
        SELECT pm.*, p.ProjectName, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Project p ON pm.ProjectID = p.ProjectID
        JOIN Material m ON pm.MaterialID = m.MaterialID
        ORDER BY p.ProjectName, m.MaterialName
    """
    project_materials = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    materials = execute_query("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName") or []
    
    return render_template('project_materials.html', project_materials=project_materials, 
                         projects=projects, materials=materials)

@app.route('/project_materials/add', methods=['POST'])
def add_project_material():
    """Add material to project"""
    project_id = request.form.get('project_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    unit_price = request.form.get('unit_price')
    
    query = """
        INSERT INTO ProjectMaterial (ProjectID, MaterialID, Quantity, UnitPrice)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Quantity = VALUES(Quantity), UnitPrice = VALUES(UnitPrice)
    """
    result = execute_query(query, (project_id, material_id, quantity, unit_price), fetch=False)
    
    if result:
        flash('Project material added/updated successfully!', 'success')
    else:
        flash('Error adding project material', 'error')
    
    return redirect(url_for('project_materials'))

# ==================== SUPPLIER MATERIALS ====================

@app.route('/supplier_materials')
def supplier_materials():
    """Manage supplier-material relationships"""
    query = """
        SELECT sm.*, s.SupplierName, m.MaterialName, m.UnitOfMeasure
        FROM SupplierMaterial sm
        JOIN Supplier s ON sm.SupplierID = s.SupplierID
        JOIN Material m ON sm.MaterialID = m.MaterialID
        ORDER BY s.SupplierName, m.MaterialName
    """
    supplier_materials = execute_query(query) or []
    
    suppliers = execute_query("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName") or []
    materials = execute_query("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName") or []
    
    return render_template('supplier_materials.html', supplier_materials=supplier_materials,
                         suppliers=suppliers, materials=materials)

@app.route('/supplier_materials/add', methods=['POST'])
def add_supplier_material():
    """Add material to supplier"""
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    price = request.form.get('price')
    lead_time = request.form.get('lead_time') or None
    
    query = """
        INSERT INTO SupplierMaterial (SupplierID, MaterialID, Price, LeadTime)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Price = VALUES(Price), LeadTime = VALUES(LeadTime)
    """
    result = execute_query(query, (supplier_id, material_id, price, lead_time), fetch=False)
    
    if result:
        flash('Supplier material added/updated successfully!', 'success')
    else:
        flash('Error adding supplier material', 'error')
    
    return redirect(url_for('supplier_materials'))

# ==================== MY PROJECTS ====================

@app.route('/myProjects')
def my_projects():
    """Show projects by employee (can filter by employee ID)"""
    employee_id = request.args.get('employee_id', type=int)
    
    if employee_id:
        query = """
            SELECT DISTINCT p.*, b.BranchName, c.ClientName, wa.Role, wa.HoursWorked
            FROM Project p
            JOIN Branch b ON p.BranchID = b.BranchID
            JOIN Client c ON p.ClientID = c.ClientID
            JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
            WHERE wa.EmployeeID = %s
            ORDER BY p.ProjectName
        """
        projects = execute_query(query, (employee_id,)) or []
    else:
        query = """
            SELECT DISTINCT p.*, b.BranchName, c.ClientName
            FROM Project p
            JOIN Branch b ON p.BranchID = b.BranchID
            JOIN Client c ON p.ClientID = c.ClientID
            ORDER BY p.ProjectName
        """
        projects = execute_query(query) or []
    
    employees = execute_query("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName") or []
    
    return render_template('myProjects.html', projects=projects, employees=employees, selected_employee=employee_id)

# ==================== QUERIES / REPORTS ====================

@app.route('/all_queries')
def all_queries():
    """List all available query/report pages"""
    queries = [
        {
            'id': 'profitability',
            'name': 'Project Profitability Analysis',
            'description': 'Analyze profitability of all projects including material costs, labor costs, and profit margins',
            'url': url_for('query_profitability')
        },
        {
            'id': 'supplier_impact',
            'name': 'Supplier Impact Analysis',
            'description': 'Evaluate supplier impact by counting projects supplied and total potential value',
            'url': url_for('query_supplier_impact')
        },
        {
            'id': 'cost_driver_materials',
            'name': 'Cost Driver Materials Analysis',
            'description': 'Identify materials driving costs and top projects using each material',
            'url': url_for('query_cost_driver_materials')
        },
        {
            'id': 'employee_utilization',
            'name': 'Employee Utilization by Manager',
            'description': 'Analyze team utilization, hours, and top projects by manager hierarchy',
            'url': url_for('query_employee_utilization')
        },
        {
            'id': 'price_anomalies',
            'name': 'Price Anomalies Detection',
            'description': 'Flag projects where material prices exceed supplier minimum by more than 20%',
            'url': url_for('query_price_anomalies')
        },
        {
            'id': 'branch_performance',
            'name': 'Branch Performance Comparison',
            'description': 'Compare branch performance by total revenue, project count, and average profitability',
            'url': url_for('query_branch_performance')
        }
    ]
    return render_template('all_queries.html', queries=queries)

@app.route('/query/profitability')
def query_profitability():
    """Q1: Project Profitability Analysis"""
    query = """
        WITH MaterialCosts AS (
            SELECT 
                ProjectID,
                SUM(Quantity * UnitPrice) as MaterialCost
            FROM ProjectMaterial
            GROUP BY ProjectID
        ),
        LaborCosts AS (
            SELECT 
                ProjectID,
                SUM(HoursWorked * (e.Salary / 160)) as LaborCost
            FROM WorkAssignment wa
            JOIN Employee e ON wa.EmployeeID = e.EmployeeID
            GROUP BY ProjectID
        )
        SELECT 
            p.ProjectID,
            p.ProjectName,
            b.BranchName,
            c.ClientName,
            p.Revenue,
            COALESCE(mc.MaterialCost, 0) as MaterialCost,
            COALESCE(lc.LaborCost, 0) as LaborCost,
            (p.Revenue - COALESCE(mc.MaterialCost, 0) - COALESCE(lc.LaborCost, 0)) as Profit,
            CASE 
                WHEN p.Revenue > 0 THEN
                    ROUND(((p.Revenue - COALESCE(mc.MaterialCost, 0) - COALESCE(lc.LaborCost, 0)) / p.Revenue) * 100, 2)
                ELSE 0
            END as ProfitMargin
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        LEFT JOIN MaterialCosts mc ON p.ProjectID = mc.ProjectID
        LEFT JOIN LaborCosts lc ON p.ProjectID = lc.ProjectID
        ORDER BY Profit DESC
    """
    
    sql_statement = """
WITH MaterialCosts AS (
    SELECT ProjectID, SUM(Quantity * UnitPrice) as MaterialCost
    FROM ProjectMaterial GROUP BY ProjectID
),
LaborCosts AS (
    SELECT ProjectID, SUM(HoursWorked * (e.Salary / 160)) as LaborCost
    FROM WorkAssignment wa
    JOIN Employee e ON wa.EmployeeID = e.EmployeeID
    GROUP BY ProjectID
)
SELECT 
    p.ProjectID, p.ProjectName, b.BranchName, c.ClientName,
    p.Revenue,
    COALESCE(mc.MaterialCost, 0) as MaterialCost,
    COALESCE(lc.LaborCost, 0) as LaborCost,
    (p.Revenue - COALESCE(mc.MaterialCost, 0) - COALESCE(lc.LaborCost, 0)) as Profit,
    CASE 
        WHEN p.Revenue > 0 THEN
            ROUND(((p.Revenue - COALESCE(mc.MaterialCost, 0) - COALESCE(lc.LaborCost, 0)) / p.Revenue) * 100, 2)
        ELSE 0
    END as ProfitMargin
FROM Project p
JOIN Branch b ON p.BranchID = b.BranchID
JOIN Client c ON p.ClientID = c.ClientID
LEFT JOIN MaterialCosts mc ON p.ProjectID = mc.ProjectID
LEFT JOIN LaborCosts lc ON p.ProjectID = lc.ProjectID
ORDER BY Profit DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_profitability.html', results=results, sql_statement=sql_statement,
                         description='This query calculates project profitability by computing material costs, labor costs (based on employee salaries), and profit margins.')

@app.route('/query/supplier_impact')
def query_supplier_impact():
    """Q2: Supplier Impact Analysis"""
    query = """
        WITH SupplierProjectValue AS (
            SELECT 
                s.SupplierID,
                s.SupplierName,
                COUNT(DISTINCT pm.ProjectID) as ProjectCount,
                SUM(pm.Quantity * sm.Price) as TotalPotentialValue
            FROM Supplier s
            JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
            JOIN ProjectMaterial pm ON sm.MaterialID = pm.MaterialID
            GROUP BY s.SupplierID, s.SupplierName
        )
        SELECT 
            SupplierID,
            SupplierName,
            ProjectCount,
            TotalPotentialValue,
            DENSE_RANK() OVER (ORDER BY ProjectCount DESC, TotalPotentialValue DESC) as RankByProjects,
            DENSE_RANK() OVER (ORDER BY TotalPotentialValue DESC, ProjectCount DESC) as RankByValue
        FROM SupplierProjectValue
        ORDER BY ProjectCount DESC, TotalPotentialValue DESC
    """
    
    sql_statement = """
WITH SupplierProjectValue AS (
    SELECT 
        s.SupplierID, s.SupplierName,
        COUNT(DISTINCT pm.ProjectID) as ProjectCount,
        SUM(pm.Quantity * sm.Price) as TotalPotentialValue
    FROM Supplier s
    JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
    JOIN ProjectMaterial pm ON sm.MaterialID = pm.MaterialID
    GROUP BY s.SupplierID, s.SupplierName
)
SELECT 
    SupplierID, SupplierName, ProjectCount, TotalPotentialValue,
    DENSE_RANK() OVER (ORDER BY ProjectCount DESC, TotalPotentialValue DESC) as RankByProjects,
    DENSE_RANK() OVER (ORDER BY TotalPotentialValue DESC, ProjectCount DESC) as RankByValue
FROM SupplierProjectValue
ORDER BY ProjectCount DESC, TotalPotentialValue DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_supplier_impact.html', results=results, sql_statement=sql_statement,
                         description='This query analyzes supplier impact by counting distinct projects supplied (via materials) and calculating total potential value, with rankings by project count and value.')

@app.route('/query/cost_driver_materials')
def query_cost_driver_materials():
    """Q3: Cost Driver Materials Analysis"""
    query = """
        WITH MaterialSpend AS (
            SELECT 
                m.MaterialID,
                m.MaterialName,
                SUM(pm.Quantity * pm.UnitPrice) as TotalSpend,
                COUNT(DISTINCT pm.ProjectID) as ProjectCount
            FROM Material m
            JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
            GROUP BY m.MaterialID, m.MaterialName
        ),
        TotalSpend AS (
            SELECT SUM(TotalSpend) as GrandTotal FROM MaterialSpend
        ),
        MaterialRanked AS (
            SELECT 
                ms.*,
                ROUND((ms.TotalSpend / ts.GrandTotal) * 100, 2) as SpendPercentage,
                ROW_NUMBER() OVER (ORDER BY ms.TotalSpend DESC) as MaterialRank
            FROM MaterialSpend ms, TotalSpend ts
        ),
        TopProjectsPerMaterial AS (
            SELECT 
                pm.MaterialID,
                pm.ProjectID,
                p.ProjectName,
                (pm.Quantity * pm.UnitPrice) as ProjectMaterialCost,
                ROW_NUMBER() OVER (PARTITION BY pm.MaterialID ORDER BY (pm.Quantity * pm.UnitPrice) DESC) as ProjectRank
            FROM ProjectMaterial pm
            JOIN Project p ON pm.ProjectID = p.ProjectID
        )
        SELECT 
            mr.MaterialID,
            mr.MaterialName,
            mr.TotalSpend,
            mr.SpendPercentage,
            mr.MaterialRank,
            mr.ProjectCount,
            tp.ProjectID as TopProjectID,
            tp.ProjectName as TopProjectName,
            tp.ProjectMaterialCost as TopProjectCost,
            tp.ProjectRank
        FROM MaterialRanked mr
        LEFT JOIN TopProjectsPerMaterial tp ON mr.MaterialID = tp.MaterialID AND tp.ProjectRank <= 3
        ORDER BY mr.MaterialRank, tp.ProjectRank
    """
    
    sql_statement = """
WITH MaterialSpend AS (
    SELECT 
        m.MaterialID, m.MaterialName,
        SUM(pm.Quantity * pm.UnitPrice) as TotalSpend,
        COUNT(DISTINCT pm.ProjectID) as ProjectCount
    FROM Material m
    JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
    GROUP BY m.MaterialID, m.MaterialName
),
TotalSpend AS (SELECT SUM(TotalSpend) as GrandTotal FROM MaterialSpend),
MaterialRanked AS (
    SELECT 
        ms.*,
        ROUND((ms.TotalSpend / ts.GrandTotal) * 100, 2) as SpendPercentage,
        ROW_NUMBER() OVER (ORDER BY ms.TotalSpend DESC) as MaterialRank
    FROM MaterialSpend ms, TotalSpend ts
),
TopProjectsPerMaterial AS (
    SELECT 
        pm.MaterialID, pm.ProjectID, p.ProjectName,
        (pm.Quantity * pm.UnitPrice) as ProjectMaterialCost,
        ROW_NUMBER() OVER (PARTITION BY pm.MaterialID ORDER BY (pm.Quantity * pm.UnitPrice) DESC) as ProjectRank
    FROM ProjectMaterial pm
    JOIN Project p ON pm.ProjectID = p.ProjectID
)
SELECT 
    mr.MaterialID, mr.MaterialName, mr.TotalSpend, mr.SpendPercentage,
    mr.MaterialRank, mr.ProjectCount,
    tp.ProjectID as TopProjectID, tp.ProjectName as TopProjectName,
    tp.ProjectMaterialCost as TopProjectCost, tp.ProjectRank
FROM MaterialRanked mr
LEFT JOIN TopProjectsPerMaterial tp ON mr.MaterialID = tp.MaterialID AND tp.ProjectRank <= 3
ORDER BY mr.MaterialRank, tp.ProjectRank
    """
    
    results = execute_query(query) or []
    return render_template('query_cost_driver_materials.html', results=results, sql_statement=sql_statement,
                         description='This query identifies cost-driving materials by ranking them by total spend, calculates percentage share of overall spend, and shows the top 3 projects for each material using window functions.')

@app.route('/query/employee_utilization')
def query_employee_utilization():
    """Q4: Employee Utilization by Manager"""
    query = """
        WITH ManagerSubordinates AS (
            SELECT 
                m.EmployeeID as ManagerID,
                m.EmployeeName as ManagerName,
                COUNT(DISTINCT e.EmployeeID) as SubordinateCount
            FROM Employee m
            LEFT JOIN Employee e ON e.ManagerID = m.EmployeeID
            WHERE m.IsManager = TRUE
            GROUP BY m.EmployeeID, m.EmployeeName
        ),
        TeamHours AS (
            SELECT 
                e.ManagerID,
                SUM(wa.HoursWorked) as TotalTeamHours
            FROM Employee e
            JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
            WHERE e.ManagerID IS NOT NULL
            GROUP BY e.ManagerID
        ),
        TopProjectByManager AS (
            SELECT 
                e.ManagerID,
                wa.ProjectID,
                p.ProjectName,
                SUM(wa.HoursWorked) as TeamProjectHours,
                ROW_NUMBER() OVER (PARTITION BY e.ManagerID ORDER BY SUM(wa.HoursWorked) DESC) as ProjectRank
            FROM Employee e
            JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
            JOIN Project p ON wa.ProjectID = p.ProjectID
            WHERE e.ManagerID IS NOT NULL
            GROUP BY e.ManagerID, wa.ProjectID, p.ProjectName
        )
        SELECT 
            ms.ManagerID,
            ms.ManagerName,
            ms.SubordinateCount,
            COALESCE(th.TotalTeamHours, 0) as TotalTeamHours,
            tp.ProjectID as TopProjectID,
            tp.ProjectName as TopProjectName,
            tp.TeamProjectHours as TopProjectHours
        FROM ManagerSubordinates ms
        LEFT JOIN TeamHours th ON ms.ManagerID = th.ManagerID
        LEFT JOIN TopProjectByManager tp ON ms.ManagerID = tp.ManagerID AND tp.ProjectRank = 1
        ORDER BY TotalTeamHours DESC
    """
    
    sql_statement = """
WITH ManagerSubordinates AS (
    SELECT 
        m.EmployeeID as ManagerID, m.EmployeeName as ManagerName,
        COUNT(DISTINCT e.EmployeeID) as SubordinateCount
    FROM Employee m
    LEFT JOIN Employee e ON e.ManagerID = m.EmployeeID
    WHERE m.IsManager = TRUE
    GROUP BY m.EmployeeID, m.EmployeeName
),
TeamHours AS (
    SELECT e.ManagerID, SUM(wa.HoursWorked) as TotalTeamHours
    FROM Employee e
    JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
    WHERE e.ManagerID IS NOT NULL
    GROUP BY e.ManagerID
),
TopProjectByManager AS (
    SELECT 
        e.ManagerID, wa.ProjectID, p.ProjectName,
        SUM(wa.HoursWorked) as TeamProjectHours,
        ROW_NUMBER() OVER (PARTITION BY e.ManagerID ORDER BY SUM(wa.HoursWorked) DESC) as ProjectRank
    FROM Employee e
    JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
    JOIN Project p ON wa.ProjectID = p.ProjectID
    WHERE e.ManagerID IS NOT NULL
    GROUP BY e.ManagerID, wa.ProjectID, p.ProjectName
)
SELECT 
    ms.ManagerID, ms.ManagerName, ms.SubordinateCount,
    COALESCE(th.TotalTeamHours, 0) as TotalTeamHours,
    tp.ProjectID as TopProjectID, tp.ProjectName as TopProjectName,
    tp.TeamProjectHours as TopProjectHours
FROM ManagerSubordinates ms
LEFT JOIN TeamHours th ON ms.ManagerID = th.ManagerID
LEFT JOIN TopProjectByManager tp ON ms.ManagerID = tp.ManagerID AND tp.ProjectRank = 1
ORDER BY TotalTeamHours DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_employee_utilization.html', results=results, sql_statement=sql_statement,
                         description='This query analyzes employee utilization by manager, showing the number of subordinates, total team hours worked, and the top project by team hours for each manager.')

@app.route('/query/price_anomalies')
def query_price_anomalies():
    """Q5: Price Anomalies Detection"""
    query = """
        WITH SupplierMinPrices AS (
            SELECT 
                MaterialID,
                MIN(Price) as MinSupplierPrice
            FROM SupplierMaterial
            GROUP BY MaterialID
        ),
        Anomalies AS (
            SELECT 
                pm.ProjectID,
                p.ProjectName,
                pm.MaterialID,
                m.MaterialName,
                pm.UnitPrice as ProjectPrice,
                smp.MinSupplierPrice,
                ROUND(((pm.UnitPrice - smp.MinSupplierPrice) / smp.MinSupplierPrice) * 100, 2) as PercentDifference,
                (SELECT SupplierID FROM SupplierMaterial 
                 WHERE MaterialID = pm.MaterialID AND Price = smp.MinSupplierPrice LIMIT 1) as SuggestedSupplierID,
                (SELECT SupplierName FROM Supplier s
                 JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
                 WHERE sm.MaterialID = pm.MaterialID AND sm.Price = smp.MinSupplierPrice LIMIT 1) as SuggestedSupplier
            FROM ProjectMaterial pm
            JOIN Material m ON pm.MaterialID = m.MaterialID
            JOIN SupplierMinPrices smp ON pm.MaterialID = smp.MaterialID
            WHERE pm.UnitPrice > (smp.MinSupplierPrice * 1.20)
        )
        SELECT * FROM Anomalies
        ORDER BY PercentDifference DESC
    """
    
    sql_statement = """
WITH SupplierMinPrices AS (
    SELECT MaterialID, MIN(Price) as MinSupplierPrice
    FROM SupplierMaterial GROUP BY MaterialID
),
Anomalies AS (
    SELECT 
        pm.ProjectID, p.ProjectName, pm.MaterialID, m.MaterialName,
        pm.UnitPrice as ProjectPrice, smp.MinSupplierPrice,
        ROUND(((pm.UnitPrice - smp.MinSupplierPrice) / smp.MinSupplierPrice) * 100, 2) as PercentDifference,
        (SELECT SupplierID FROM SupplierMaterial 
         WHERE MaterialID = pm.MaterialID AND Price = smp.MinSupplierPrice LIMIT 1) as SuggestedSupplierID,
        (SELECT SupplierName FROM Supplier s
         JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
         WHERE sm.MaterialID = pm.MaterialID AND sm.Price = smp.MinSupplierPrice LIMIT 1) as SuggestedSupplier
    FROM ProjectMaterial pm
    JOIN Material m ON pm.MaterialID = m.MaterialID
    JOIN SupplierMinPrices smp ON pm.MaterialID = smp.MaterialID
    WHERE pm.UnitPrice > (smp.MinSupplierPrice * 1.20)
)
SELECT * FROM Anomalies ORDER BY PercentDifference DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_price_anomalies.html', results=results, sql_statement=sql_statement,
                         description='This query identifies price anomalies where project material prices exceed the minimum supplier price by more than 20%, suggesting potential cost savings opportunities.')

@app.route('/query/branch_performance')
def query_branch_performance():
    """Q6: Branch Performance Comparison"""
    query = """
        WITH BranchProjects AS (
            SELECT 
                b.BranchID,
                b.BranchName,
                b.City,
                COUNT(DISTINCT p.ProjectID) as ProjectCount,
                SUM(p.Revenue) as TotalRevenue,
                AVG(p.Revenue) as AvgRevenuePerProject
            FROM Branch b
            LEFT JOIN Project p ON b.BranchID = p.BranchID
            GROUP BY b.BranchID, b.BranchName, b.City
        ),
        BranchCosts AS (
            SELECT 
                b.BranchID,
                COALESCE(SUM(pm.Quantity * pm.UnitPrice), 0) as TotalMaterialCost,
                COALESCE(SUM(wa.HoursWorked * (e.Salary / 160)), 0) as TotalLaborCost
            FROM Branch b
            LEFT JOIN Project p ON b.BranchID = p.BranchID
            LEFT JOIN ProjectMaterial pm ON p.ProjectID = pm.ProjectID
            LEFT JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
            LEFT JOIN Employee e ON wa.EmployeeID = e.EmployeeID
            GROUP BY b.BranchID
        )
        SELECT 
            bp.BranchID,
            bp.BranchName,
            bp.City,
            bp.ProjectCount,
            bp.TotalRevenue,
            bp.AvgRevenuePerProject,
            bc.TotalMaterialCost,
            bc.TotalLaborCost,
            (bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) as TotalProfit,
            CASE 
                WHEN bp.TotalRevenue > 0 THEN
                    ROUND(((bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) / bp.TotalRevenue) * 100, 2)
                ELSE 0
            END as ProfitMargin,
            RANK() OVER (ORDER BY (bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) DESC) as ProfitRank,
            RANK() OVER (ORDER BY bp.ProjectCount DESC) as ProjectCountRank
        FROM BranchProjects bp
        JOIN BranchCosts bc ON bp.BranchID = bc.BranchID
        ORDER BY TotalProfit DESC
    """
    
    sql_statement = """
WITH BranchProjects AS (
    SELECT 
        b.BranchID, b.BranchName, b.City,
        COUNT(DISTINCT p.ProjectID) as ProjectCount,
        SUM(p.Revenue) as TotalRevenue,
        AVG(p.Revenue) as AvgRevenuePerProject
    FROM Branch b
    LEFT JOIN Project p ON b.BranchID = p.BranchID
    GROUP BY b.BranchID, b.BranchName, b.City
),
BranchCosts AS (
    SELECT 
        b.BranchID,
        COALESCE(SUM(pm.Quantity * pm.UnitPrice), 0) as TotalMaterialCost,
        COALESCE(SUM(wa.HoursWorked * (e.Salary / 160)), 0) as TotalLaborCost
    FROM Branch b
    LEFT JOIN Project p ON b.BranchID = p.BranchID
    LEFT JOIN ProjectMaterial pm ON p.ProjectID = pm.ProjectID
    LEFT JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
    LEFT JOIN Employee e ON wa.EmployeeID = e.EmployeeID
    GROUP BY b.BranchID
)
SELECT 
    bp.BranchID, bp.BranchName, bp.City, bp.ProjectCount,
    bp.TotalRevenue, bp.AvgRevenuePerProject,
    bc.TotalMaterialCost, bc.TotalLaborCost,
    (bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) as TotalProfit,
    CASE 
        WHEN bp.TotalRevenue > 0 THEN
            ROUND(((bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) / bp.TotalRevenue) * 100, 2)
        ELSE 0
    END as ProfitMargin,
    RANK() OVER (ORDER BY (bp.TotalRevenue - bc.TotalMaterialCost - bc.TotalLaborCost) DESC) as ProfitRank,
    RANK() OVER (ORDER BY bp.ProjectCount DESC) as ProjectCountRank
FROM BranchProjects bp
JOIN BranchCosts bc ON bp.BranchID = bc.BranchID
ORDER BY TotalProfit DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_branch_performance.html', results=results, sql_statement=sql_statement,
                         description='This query compares branch performance by analyzing total revenue, project counts, material costs, labor costs, profitability, and profit margins, with rankings.')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

