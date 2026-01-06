"""
Flask Application for Abaad Contracting Management System
Main application file with routes and database operations
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', 'l18102005'),
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
               m.EmployeeName as ManagerName, r.Title as Position
        FROM Employee e
        JOIN Branch b ON e.BranchID = b.BranchID
        JOIN Department d ON e.DepartmentID = d.DepartmentID
        JOIN Role r ON e.PositionID = r.RoleID
        LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
        ORDER BY e.EmployeeName
    """
    employees = execute_query(query) or []
    
    # Get branches, departments, roles, and managers for forms
    branches = execute_query("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName") or []
    departments = execute_query("SELECT DepartmentID, DepartmentName FROM Department ORDER BY DepartmentName") or []
    roles = execute_query("SELECT RoleID, Title FROM Role ORDER BY Title") or []
    managers = execute_query("SELECT EmployeeID, EmployeeName FROM Employee WHERE IsManager = TRUE ORDER BY EmployeeName") or []
    
    return render_template('employees.html', employees=employees, branches=branches, 
                         departments=departments, roles=roles, managers=managers)

@app.route('/employees/add', methods=['POST'])
def add_employee():
    """Add a new employee"""
    name = request.form.get('employee_name')
    position_id = request.form.get('position_id')
    salary = request.form.get('salary')
    branch_id = request.form.get('branch_id')
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    is_manager = request.form.get('is_manager') == 'on'
    
    query = """
        INSERT INTO Employee (EmployeeName, PositionID, Salary, BranchID, DepartmentID, ManagerID, IsManager)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    result = execute_query(query, (name, position_id, salary, branch_id, dept_id, manager_id, is_manager), fetch=False)
    
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
    """List all projects, optionally filtered by type"""
    project_type = request.args.get('type', None)
    
    if project_type in ['building', 'solar']:
        query = """
            SELECT p.*, b.BranchName, c.ClientName
            FROM Project p
            JOIN Branch b ON p.BranchID = b.BranchID
            JOIN Client c ON p.ClientID = c.ClientID
            WHERE p.ProjectType = %s
            ORDER BY p.ProjectID DESC
        """
        projects = execute_query(query, (project_type,)) or []
    else:
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
    
    return render_template('projects.html', projects=projects, branches=branches, clients=clients, project_type=project_type)

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
        SELECT wa.*, e.EmployeeName, r.Title as Position
        FROM WorkAssignment wa
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        JOIN Role r ON e.PositionID = r.RoleID
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
    
    total_material_cost = 0.0
    if materials:
        for m in materials:
            quantity = float(m.get('Quantity', 0) or 0)
            unit_price = float(m.get('UnitPrice', 0) or 0)
            total_material_cost += quantity * unit_price
    
    return render_template('manage_project.html', project=project[0], assignments=assignments, materials=materials, total_material_cost=total_material_cost)

@app.route('/projects/add', methods=['POST'])
def add_project():
    """Add a new project"""
    try:
        name = request.form.get('project_name')
        location = request.form.get('location')
        cost = request.form.get('cost') or 0
        revenue = request.form.get('revenue')
        project_type = request.form.get('project_type', 'building')
        branch_id = request.form.get('branch_id')
        client_id = request.form.get('client_id')
        
        # Check if ProjectType column exists, if not use old query
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Try to check if ProjectType column exists
                cursor.execute("SHOW COLUMNS FROM Project LIKE 'ProjectType'")
                has_project_type = cursor.fetchone() is not None
                
                if has_project_type:
                    query = """
                        INSERT INTO Project (ProjectName, Location, Cost, Revenue, ProjectType, BranchID, ClientID)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, location, cost, revenue, project_type, branch_id, client_id))
                else:
                    # Fallback for old schema
                    query = """
                        INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, location, cost, revenue, branch_id, client_id))
                
                connection.commit()
                flash('Project added successfully!', 'success')
            except Error as e:
                connection.rollback()
                flash(f'Error adding project: {str(e)}', 'error')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error: Could not connect to database', 'error')
    except Exception as e:
        flash(f'Error adding project: {str(e)}', 'error')
    
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
        SELECT wa.*, p.ProjectName, e.EmployeeName, r.Title as Position
        FROM WorkAssignment wa
        JOIN Project p ON wa.ProjectID = p.ProjectID
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        JOIN Role r ON e.PositionID = r.RoleID
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

# ==================== CONTRACTS ====================

@app.route('/contracts')
def contracts():
    """List and manage contracts"""
    query = """
        SELECT c.*, p.ProjectName, cl.ClientName
        FROM Contract c
        JOIN Project p ON c.ProjectID = p.ProjectID
        JOIN Client cl ON c.ClientID = cl.ClientID
        ORDER BY c.ContractID DESC
    """
    contracts = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    clients = execute_query("SELECT ClientID, ClientName FROM Client ORDER BY ClientName") or []
    
    return render_template('contracts.html', contracts=contracts, projects=projects, clients=clients)

@app.route('/contracts/add', methods=['POST'])
def add_contract():
    """Add a new contract"""
    project_id = request.form.get('project_id')
    client_id = request.form.get('client_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    total_value = request.form.get('total_value')
    status = request.form.get('status', 'active')
    
    query = """
        INSERT INTO Contract (ProjectID, ClientID, StartDate, EndDate, TotalValue, Status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    result = execute_query(query, (project_id, client_id, start_date, end_date, total_value, status), fetch=False)
    
    if result:
        flash('Contract added successfully!', 'success')
    else:
        flash('Error adding contract', 'error')
    
    return redirect(url_for('contracts'))

# ==================== PHASES ====================

@app.route('/phases')
def phases():
    """List and manage project phases"""
    query = """
        SELECT ph.*, p.ProjectName
        FROM Phase ph
        JOIN Project p ON ph.ProjectID = p.ProjectID
        ORDER BY ph.PhaseID DESC
    """
    phases = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    
    return render_template('phases.html', phases=phases, projects=projects)

@app.route('/phases/add', methods=['POST'])
def add_phase():
    """Add a new phase"""
    project_id = request.form.get('project_id')
    name = request.form.get('name')
    description = request.form.get('description') or None
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    status = request.form.get('status', 'planned')
    
    query = """
        INSERT INTO Phase (ProjectID, Name, Description, StartDate, EndDate, Status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    result = execute_query(query, (project_id, name, description, start_date, end_date, status), fetch=False)
    
    if result:
        flash('Phase added successfully!', 'success')
    else:
        flash('Error adding phase', 'error')
    
    return redirect(url_for('phases'))

# ==================== SCHEDULES ====================

@app.route('/schedules')
def schedules():
    """List and manage schedules"""
    query = """
        SELECT s.*, p.ProjectName, ph.Name as PhaseName
        FROM Schedule s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Phase ph ON s.PhaseID = ph.PhaseID
        ORDER BY s.ScheduleID DESC
    """
    schedules = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    phases = execute_query("SELECT PhaseID, Name, ProjectID FROM Phase ORDER BY PhaseID") or []
    
    return render_template('schedules.html', schedules=schedules, projects=projects, phases=phases)

@app.route('/schedules/add', methods=['POST'])
def add_schedule():
    """Add a new schedule"""
    project_id = request.form.get('project_id')
    phase_id = request.form.get('phase_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    task_details = request.form.get('task_details') or None
    
    query = """
        INSERT INTO Schedule (ProjectID, PhaseID, StartDate, EndDate, TaskDetails)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = execute_query(query, (project_id, phase_id, start_date, end_date, task_details), fetch=False)
    
    if result:
        flash('Schedule added successfully!', 'success')
    else:
        flash('Error adding schedule', 'error')
    
    return redirect(url_for('schedules'))

# ==================== SALES ====================

@app.route('/sales')
def sales():
    """List and manage sales"""
    query = """
        SELECT s.*, p.ProjectName, c.ClientName
        FROM Sales s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Client c ON s.ClientID = c.ClientID
        ORDER BY s.SaleID DESC
    """
    sales = execute_query(query) or []
    
    projects = execute_query("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName") or []
    clients = execute_query("SELECT ClientID, ClientName FROM Client ORDER BY ClientName") or []
    
    return render_template('sales.html', sales=sales, projects=projects, clients=clients)

@app.route('/sales/add', methods=['POST'])
def add_sale():
    """Add a new sale"""
    project_id = request.form.get('project_id')
    client_id = request.form.get('client_id')
    amount = request.form.get('amount')
    issue_date = request.form.get('issue_date')
    due_date = request.form.get('due_date') or None
    
    query = """
        INSERT INTO Sales (ProjectID, ClientID, Amount, IssueDate, DueDate)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = execute_query(query, (project_id, client_id, amount, issue_date, due_date), fetch=False)
    
    if result:
        flash('Sale added successfully!', 'success')
    else:
        flash('Error adding sale', 'error')
    
    return redirect(url_for('sales'))

# ==================== PURCHASES ====================

@app.route('/purchases')
def purchases():
    """List and manage purchases"""
    query = """
        SELECT pu.*, s.SupplierName, m.MaterialName
        FROM Purchase pu
        JOIN Supplier s ON pu.SupplierID = s.SupplierID
        JOIN Material m ON pu.MaterialID = m.MaterialID
        ORDER BY pu.PurchaseID DESC
    """
    purchases = execute_query(query) or []
    
    suppliers = execute_query("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName") or []
    materials = execute_query("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName") or []
    
    return render_template('purchases.html', purchases=purchases, suppliers=suppliers, materials=materials)

@app.route('/purchases/add', methods=['POST'])
def add_purchase():
    """Add a new purchase"""
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    purchase_date = request.form.get('purchase_date')
    total_cost = request.form.get('total_cost')
    
    query = """
        INSERT INTO Purchase (SupplierID, MaterialID, Quantity, PurchaseDate, TotalCost)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = execute_query(query, (supplier_id, material_id, quantity, purchase_date, total_cost), fetch=False)
    
    if result:
        flash('Purchase added successfully!', 'success')
    else:
        flash('Error adding purchase', 'error')
    
    return redirect(url_for('purchases'))

# ==================== PAYMENTS ====================

@app.route('/payments')
def payments():
    """List and manage payments"""
    query = """
        SELECT py.*, c.ClientName, s.SupplierName
        FROM Payment py
        LEFT JOIN Client c ON py.FromClient = c.ClientID
        LEFT JOIN Supplier s ON py.ToSupplier = s.SupplierID
        ORDER BY py.PaymentID DESC
    """
    payments = execute_query(query) or []
    
    clients = execute_query("SELECT ClientID, ClientName FROM Client ORDER BY ClientName") or []
    suppliers = execute_query("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName") or []
    
    return render_template('payments.html', payments=payments, clients=clients, suppliers=suppliers)

@app.route('/payments/add', methods=['POST'])
def add_payment():
    """Add a new payment"""
    from_client = request.form.get('from_client') or None
    to_supplier = request.form.get('to_supplier') or None
    amount = request.form.get('amount')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method')
    
    query = """
        INSERT INTO Payment (FromClient, ToSupplier, Amount, PaymentDate, PaymentMethod)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = execute_query(query, (from_client, to_supplier, amount, payment_date, payment_method), fetch=False)
    
    if result:
        flash('Payment added successfully!', 'success')
    else:
        flash('Error adding payment', 'error')
    
    return redirect(url_for('payments'))

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
        SELECT 
            p.ProjectID,
            p.ProjectName,
            b.BranchName,
            c.ClientName,
            p.Revenue,
            SUM(pm.Quantity * pm.UnitPrice) as MaterialCost,
            SUM(wa.HoursWorked * (e.Salary / 160)) as LaborCost,
            (p.Revenue - SUM(pm.Quantity * pm.UnitPrice) - SUM(wa.HoursWorked * (e.Salary / 160))) as Profit
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        LEFT JOIN ProjectMaterial pm ON p.ProjectID = pm.ProjectID
        LEFT JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
        LEFT JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        GROUP BY p.ProjectID, p.ProjectName, b.BranchName, c.ClientName, p.Revenue
        ORDER BY Profit DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_profitability.html', results=results,
                         description='This query calculates project profitability by computing material costs, labor costs (based on employee salaries), and profit.')

@app.route('/query/supplier_impact')
def query_supplier_impact():
    """Q2: Supplier Impact Analysis"""
    query = """
        SELECT 
            s.SupplierID,
            s.SupplierName,
            COUNT(DISTINCT pm.ProjectID) as ProjectCount,
            SUM(pm.Quantity * sm.Price) as TotalPotentialValue
        FROM Supplier s
        JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
        JOIN ProjectMaterial pm ON sm.MaterialID = pm.MaterialID
        GROUP BY s.SupplierID, s.SupplierName
        ORDER BY ProjectCount DESC, TotalPotentialValue DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_supplier_impact.html', results=results,
                         description='This query analyzes supplier impact by counting distinct projects supplied (via materials) and calculating total potential value.')

@app.route('/query/cost_driver_materials')
def query_cost_driver_materials():
    """Q3: Cost Driver Materials Analysis"""
    query = """
        SELECT 
            m.MaterialID,
            m.MaterialName,
            SUM(pm.Quantity * pm.UnitPrice) as TotalSpend,
            COUNT(DISTINCT pm.ProjectID) as ProjectCount
        FROM Material m
        JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
        GROUP BY m.MaterialID, m.MaterialName
        ORDER BY TotalSpend DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_cost_driver_materials.html', results=results,
                         description='This query identifies cost-driving materials by total spend and shows how many projects use each material.')

@app.route('/query/employee_utilization')
def query_employee_utilization():
    """Q4: Employee Utilization by Manager"""
    query = """
        SELECT 
            m.EmployeeID as ManagerID,
            m.EmployeeName as ManagerName,
            COUNT(DISTINCT e.EmployeeID) as SubordinateCount,
            SUM(wa.HoursWorked) as TotalTeamHours
        FROM Employee m
        LEFT JOIN Employee e ON e.ManagerID = m.EmployeeID
        LEFT JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
        WHERE m.IsManager = TRUE
        GROUP BY m.EmployeeID, m.EmployeeName
        ORDER BY TotalTeamHours DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_employee_utilization.html', results=results,
                         description='This query analyzes employee utilization by manager, showing the number of subordinates and total team hours worked.')

@app.route('/query/price_anomalies')
def query_price_anomalies():
    """Q5: Price Anomalies Detection"""
    query = """
        SELECT 
            pm.ProjectID,
            p.ProjectName,
            pm.MaterialID,
            m.MaterialName,
            pm.UnitPrice as ProjectPrice,
            MIN(sm.Price) as MinSupplierPrice,
            ROUND(((pm.UnitPrice - MIN(sm.Price)) / MIN(sm.Price)) * 100, 2) as PercentDifference
        FROM ProjectMaterial pm
        JOIN Material m ON pm.MaterialID = m.MaterialID
        JOIN SupplierMaterial sm ON pm.MaterialID = sm.MaterialID
        JOIN Project p ON pm.ProjectID = p.ProjectID
        GROUP BY pm.ProjectID, p.ProjectName, pm.MaterialID, m.MaterialName, pm.UnitPrice
        HAVING pm.UnitPrice > (MIN(sm.Price) * 1.20)
        ORDER BY PercentDifference DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_price_anomalies.html', results=results,
                         description='This query identifies price anomalies where project material prices exceed the minimum supplier price by more than 20%.')

@app.route('/query/branch_performance')
def query_branch_performance():
    """Q6: Branch Performance Comparison"""
    query = """
        SELECT 
            b.BranchID,
            b.BranchName,
            b.City,
            COUNT(DISTINCT p.ProjectID) as ProjectCount,
            SUM(p.Revenue) as TotalRevenue,
            AVG(p.Revenue) as AvgRevenuePerProject,
            SUM(pm.Quantity * pm.UnitPrice) as TotalMaterialCost,
            SUM(wa.HoursWorked * (e.Salary / 160)) as TotalLaborCost,
            (SUM(p.Revenue) - SUM(pm.Quantity * pm.UnitPrice) - SUM(wa.HoursWorked * (e.Salary / 160))) as TotalProfit
        FROM Branch b
        LEFT JOIN Project p ON b.BranchID = p.BranchID
        LEFT JOIN ProjectMaterial pm ON p.ProjectID = pm.ProjectID
        LEFT JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
        LEFT JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        GROUP BY b.BranchID, b.BranchName, b.City
        ORDER BY TotalProfit DESC
    """
    
    results = execute_query(query) or []
    return render_template('query_branch_performance.html', results=results,
                         description='This query compares branch performance by analyzing total revenue, project counts, material costs, labor costs, and profitability.')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=True)
