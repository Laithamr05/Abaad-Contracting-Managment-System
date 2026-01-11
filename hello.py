from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import pymysql.cursors

myDB = pymysql.connect(host="localhost", user="root", password="l18102005")
myCursor = myDB.cursor(pymysql.cursors.DictCursor)

myCursor.execute("USE abaad_contracting")

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

@app.route('/')
def index():
    stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM Branch) as branch_count,
            (SELECT COUNT(*) FROM Employee) as employee_count,
            (SELECT COUNT(*) FROM Project) as project_count,
            (SELECT COUNT(*) FROM Client) as client_count,
            (SELECT SUM(Revenue) FROM Project) as total_revenue,
            (SELECT COUNT(*) FROM Supplier) as supplier_count
    """
    myCursor.execute(stats_query)
    stats = myCursor.fetchall()
    
    recent_projects_query = """
        SELECT p.ProjectID, p.ProjectName, p.Location, p.Revenue, 
               b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        ORDER BY p.ProjectID DESC
        LIMIT 5
    """
    myCursor.execute(recent_projects_query)
    recent_projects = myCursor.fetchall() or []
    
    return render_template('index.html', stats=stats[0] if stats else {}, recent_projects=recent_projects)

@app.route('/error')
def error_page():
    error_msg = request.args.get('msg', 'An error occurred')
    return render_template('error.html', error_msg=error_msg)

@app.route('/branches')
def branches():
    filter_city = request.args.get('filter_city', '')
    
    query = """
        SELECT b.*, 
               COUNT(DISTINCT e.EmployeeID) as employee_count,
               COUNT(DISTINCT p.ProjectID) as project_count
        FROM Branch b
        LEFT JOIN Employee e ON b.BranchID = e.BranchID
        LEFT JOIN Project p ON b.BranchID = p.BranchID
        WHERE 1=1
    """
    params = []
    
    if filter_city:
        query += " AND b.City = %s"
        params.append(filter_city)
    
    query += " GROUP BY b.BranchID ORDER BY b.BranchName"
    myCursor.execute(query, tuple(params) if params else None)
    branches = myCursor.fetchall() or []
    
    myCursor.execute("SELECT DISTINCT City FROM Branch ORDER BY City")
    cities = myCursor.fetchall() or []
    return render_template('branches.html', branches=branches, cities=cities, filter_city=filter_city)

@app.route('/branches/add', methods=['POST'])
def add_branch():
    branch_name = request.form.get('branch_name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    query = "INSERT INTO Branch (BranchName, City, Address, PhoneNumber) VALUES (%s, %s, %s, %s)"
    myCursor.execute(query, (branch_name, city, address, phone))
    myDB.commit()
    
    flash('Branch added successfully!', 'success')
    return redirect(url_for('branches'))

@app.route('/employees')
def employees():
    filter_branch = request.args.get('filter_branch', '')
    filter_department = request.args.get('filter_department', '')
    filter_role = request.args.get('filter_role', '')
    filter_manager = request.args.get('filter_manager', '')
    filter_is_manager = request.args.get('filter_is_manager', '')
    sort_by = request.args.get('sort_by', 'EmployeeName')
    sort_order = request.args.get('sort_order', 'asc').lower() or 'asc'
    
    query = """
        SELECT e.*, b.BranchName, d.DepartmentName,
               m.EmployeeName as ManagerName, r.Title as Position
        FROM Employee e
        JOIN Branch b ON e.BranchID = b.BranchID
        JOIN Department d ON e.DepartmentID = d.DepartmentID
        JOIN Role r ON e.PositionID = r.RoleID
        LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
        WHERE 1=1
    """
    params = []
    
    if filter_branch:
        query += " AND e.BranchID = %s"
        params.append(filter_branch)
    if filter_department:
        query += " AND e.DepartmentID = %s"
        params.append(filter_department)
    if filter_role:
        query += " AND e.PositionID = %s"
        params.append(filter_role)
    if filter_manager:
        query += " AND e.ManagerID = %s"
        params.append(filter_manager)
    if filter_is_manager:
        query += " AND e.IsManager = %s"
        params.append(filter_is_manager == 'true')
    
    valid_sort_fields = ['EmployeeName', 'Salary', 'BranchName', 'DepartmentName', 'Position']
    if sort_by not in valid_sort_fields:
        sort_by = 'EmployeeName'
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    
    if sort_by == 'Salary':
        query += f" ORDER BY e.Salary {sql_sort_order}"
    elif sort_by == 'BranchName':
        query += f" ORDER BY b.BranchName {sql_sort_order}"
    elif sort_by == 'DepartmentName':
        query += f" ORDER BY d.DepartmentName {sql_sort_order}"
    elif sort_by == 'Position':
        query += f" ORDER BY r.Title {sql_sort_order}"
    else:
        query += f" ORDER BY e.EmployeeName {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    employees = myCursor.fetchall() or []
    
    myCursor.execute("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName")
    branches = myCursor.fetchall() or []
    myCursor.execute("SELECT DepartmentID, DepartmentName FROM Department ORDER BY DepartmentName")
    departments = myCursor.fetchall() or []
    myCursor.execute("SELECT RoleID, Title FROM Role ORDER BY Title")
    roles = myCursor.fetchall() or []
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee WHERE IsManager = TRUE ORDER BY EmployeeName")
    managers = myCursor.fetchall() or []
    
    return render_template('employees.html', employees=employees, branches=branches, 
                         departments=departments, roles=roles, managers=managers,
                         filter_branch=filter_branch, filter_department=filter_department,
                         filter_role=filter_role, filter_manager=filter_manager, filter_is_manager=filter_is_manager,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/employees/add', methods=['POST'])
def add_employee():
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
    myCursor.execute(query, (name, position_id, salary, branch_id, dept_id, manager_id, is_manager))
    myDB.commit()
    
    flash('Employee added successfully!', 'success')
    return redirect(url_for('employees'))

@app.route('/departments')
def departments():
    filter_manager = request.args.get('filter_manager', '')
    
    query = """
        SELECT d.*, e.EmployeeName as ManagerName,
               COUNT(DISTINCT emp.EmployeeID) as employee_count
        FROM Department d
        LEFT JOIN Employee e ON d.ManagerID = e.EmployeeID
        LEFT JOIN Employee emp ON d.DepartmentID = emp.DepartmentID
        WHERE 1=1
    """
    params = []
    
    if filter_manager:
        query += " AND d.ManagerID = %s"
        params.append(filter_manager)
    
    query += " GROUP BY d.DepartmentID ORDER BY d.DepartmentName"
    myCursor.execute(query, tuple(params) if params else None)
    departments = myCursor.fetchall() or []
    
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName")
    employees = myCursor.fetchall() or []
    
    return render_template('departments.html', departments=departments, employees=employees, filter_manager=filter_manager)

@app.route('/departments/set_manager', methods=['POST'])
def set_department_manager():
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    
    query = "UPDATE Department SET ManagerID = %s WHERE DepartmentID = %s"
    myCursor.execute(query, (manager_id, dept_id))
    myDB.commit()
    
    flash('Department manager updated successfully!', 'success')
    return redirect(url_for('departments'))

@app.route('/clients')
def clients():
    filter_has_projects = request.args.get('filter_has_projects', '')
    
    query = """
        SELECT c.*, COUNT(DISTINCT p.ProjectID) as project_count
        FROM Client c
        LEFT JOIN Project p ON c.ClientID = p.ClientID
        WHERE 1=1
    """
    params = []
    
    if filter_has_projects == 'yes':
        query += " HAVING COUNT(DISTINCT p.ProjectID) > 0"
    elif filter_has_projects == 'no':
        query += " HAVING COUNT(DISTINCT p.ProjectID) = 0"
    
    query += " GROUP BY c.ClientID ORDER BY c.ClientName"
    myCursor.execute(query, tuple(params) if params else None)
    clients = myCursor.fetchall() or []
    return render_template('clients.html', clients=clients, filter_has_projects=filter_has_projects)

@app.route('/clients/add', methods=['POST'])
def add_client():
    name = request.form.get('client_name')
    contact = request.form.get('contact_info')
    
    query = "INSERT INTO Client (ClientName, ContactInfo) VALUES (%s, %s)"
    myCursor.execute(query, (name, contact))
    myDB.commit()
    
    flash('Client added successfully!', 'success')
    return redirect(url_for('clients'))

@app.route('/projects')
def projects():
    filter_type = request.args.get('filter_type', '')
    filter_branch = request.args.get('filter_branch', '')
    filter_client = request.args.get('filter_client', '')
    sort_by = request.args.get('sort_by', 'ProjectID')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        WHERE 1=1
    """
    params = []
    
    if filter_type:
        query += " AND p.ProjectType = %s"
        params.append(filter_type)
    if filter_branch:
        query += " AND p.BranchID = %s"
        params.append(filter_branch)
    if filter_client:
        query += " AND p.ClientID = %s"
        params.append(filter_client)
    
    sql_sort_order = 'ASC' if sort_order == 'asc' else 'DESC'
    if sort_by == 'Cost':
        query += f" ORDER BY p.Cost {sql_sort_order}"
    elif sort_by == 'Revenue':
        query += f" ORDER BY p.Revenue {sql_sort_order}"
    else:
        query += f" ORDER BY p.ProjectID {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    projects = myCursor.fetchall() or []
    
    myCursor.execute("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName")
    branches = myCursor.fetchall() or []
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = myCursor.fetchall() or []
    
    return render_template('projects.html', projects=projects, branches=branches, clients=clients, 
                         filter_type=filter_type, filter_branch=filter_branch, filter_client=filter_client,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/projects/<int:project_id>')
def project_details(project_id):
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        WHERE p.ProjectID = %s
    """
    myCursor.execute(query, (project_id,))
    project = myCursor.fetchall()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects'))
    
    assignments_query = """
        SELECT wa.*, e.EmployeeName, r.Title as Position
        FROM WorkAssignment wa
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        JOIN Role r ON e.PositionID = r.RoleID
        WHERE wa.ProjectID = %s
    """
    myCursor.execute(assignments_query, (project_id,))
    assignments = myCursor.fetchall() or []
    
    materials_query = """
        SELECT pm.*, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Material m ON pm.MaterialID = m.MaterialID
        WHERE pm.ProjectID = %s
    """
    myCursor.execute(materials_query, (project_id,))
    materials = myCursor.fetchall() or []
    
    total_material_cost = 0.0
    if materials:
        for m in materials:
            quantity = float(m.get('Quantity', 0) or 0)
            unit_price = float(m.get('UnitPrice', 0) or 0)
            total_material_cost += quantity * unit_price
    
    return render_template('manage_project.html', project=project[0], assignments=assignments, materials=materials, total_material_cost=total_material_cost)

@app.route('/projects/add', methods=['POST'])
def add_project():
    try:
        name = request.form.get('project_name')
        location = request.form.get('location')
        cost = request.form.get('cost') or 0
        revenue = request.form.get('revenue')
        project_type = request.form.get('project_type', 'building')
        branch_id = request.form.get('branch_id')
        client_id = request.form.get('client_id')
        
        myCursor.execute("SHOW COLUMNS FROM Project LIKE 'ProjectType'")
        has_project_type = myCursor.fetchone() is not None
        
        if has_project_type:
            query = """
                INSERT INTO Project (ProjectName, Location, Cost, Revenue, ProjectType, BranchID, ClientID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            myCursor.execute(query, (name, location, cost, revenue, project_type, branch_id, client_id))
        else:
            query = """
                INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            myCursor.execute(query, (name, location, cost, revenue, branch_id, client_id))
        
        myDB.commit()
        flash('Project added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding project: {str(e)}', 'error')
    
    return redirect(url_for('projects'))

@app.route('/suppliers')
def suppliers():
    filter_has_materials = request.args.get('filter_has_materials', '')
    
    query = """
        SELECT s.*, COUNT(DISTINCT sm.MaterialID) as material_count
        FROM Supplier s
        LEFT JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
        WHERE 1=1
    """
    params = []
    
    if filter_has_materials == 'yes':
        query += " HAVING COUNT(DISTINCT sm.MaterialID) > 0"
    elif filter_has_materials == 'no':
        query += " HAVING COUNT(DISTINCT sm.MaterialID) = 0"
    
    query += " GROUP BY s.SupplierID ORDER BY s.SupplierName"
    myCursor.execute(query, tuple(params) if params else None)
    suppliers = myCursor.fetchall() or []
    return render_template('suppliers.html', suppliers=suppliers, filter_has_materials=filter_has_materials)

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    name = request.form.get('supplier_name')
    contact = request.form.get('contact_info')
    
    query = "INSERT INTO Supplier (SupplierName, ContactInfo) VALUES (%s, %s)"
    myCursor.execute(query, (name, contact))
    myDB.commit()
    
    flash('Supplier added successfully!', 'success')
    return redirect(url_for('suppliers'))

@app.route('/materials')
def materials():
    filter_unit = request.args.get('filter_unit', '')
    sort_by = request.args.get('sort_by', 'MaterialName')
    sort_order = request.args.get('sort_order', 'asc').lower() or 'asc'
    
    query = "SELECT * FROM Material WHERE 1=1"
    params = []
    
    if filter_unit:
        query += " AND UnitOfMeasure = %s"
        params.append(filter_unit)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'BaseUnitPrice':
        query += f" ORDER BY BaseUnitPrice {sql_sort_order}"
    else:
        query += f" ORDER BY MaterialName {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    materials = myCursor.fetchall() or []
    
    myCursor.execute("SELECT DISTINCT UnitOfMeasure FROM Material ORDER BY UnitOfMeasure")
    units = myCursor.fetchall() or []
    return render_template('materials.html', materials=materials, units=units, filter_unit=filter_unit,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/materials/add', methods=['POST'])
def add_material():
    name = request.form.get('material_name')
    base_price = request.form.get('base_unit_price')
    unit = request.form.get('unit_of_measure')
    
    query = "INSERT INTO Material (MaterialName, BaseUnitPrice, UnitOfMeasure) VALUES (%s, %s, %s)"
    myCursor.execute(query, (name, base_price, unit))
    myDB.commit()
    
    flash('Material added successfully!', 'success')
    return redirect(url_for('materials'))

@app.route('/work_assignments')
def work_assignments():
    filter_project = request.args.get('filter_project', '')
    filter_employee = request.args.get('filter_employee', '')
    filter_role = request.args.get('filter_role', '')
    
    query = """
        SELECT wa.*, p.ProjectName, e.EmployeeName, r.Title as Position
        FROM WorkAssignment wa
        JOIN Project p ON wa.ProjectID = p.ProjectID
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        JOIN Role r ON e.PositionID = r.RoleID
        WHERE 1=1
    """
    params = []
    
    if filter_project:
        query += " AND wa.ProjectID = %s"
        params.append(filter_project)
    if filter_employee:
        query += " AND wa.EmployeeID = %s"
        params.append(filter_employee)
    if filter_role:
        query += " AND wa.Role = %s"
        params.append(filter_role)
    
    query += " ORDER BY wa.StartDate DESC"
    myCursor.execute(query, tuple(params) if params else None)
    assignments = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName")
    employees = myCursor.fetchall() or []
    myCursor.execute("SELECT DISTINCT Role FROM WorkAssignment ORDER BY Role")
    roles = myCursor.fetchall() or []
    
    return render_template('work_assignments.html', assignments=assignments, projects=projects, 
                         employees=employees, roles=roles,
                         filter_project=filter_project, filter_employee=filter_employee, filter_role=filter_role)

@app.route('/work_assignments/add', methods=['POST'])
def add_work_assignment():
    project_id = request.form.get('project_id')
    employee_id = request.form.get('employee_id')
    role = request.form.get('role')
    hours = request.form.get('hours_worked') or 0
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    
    query = """
        INSERT INTO WorkAssignment (ProjectID, EmployeeID, Role, HoursWorked, StartDate, EndDate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    myCursor.execute(query, (project_id, employee_id, role, hours, start_date, end_date))
    myDB.commit()
    
    flash('Work assignment added successfully!', 'success')
    return redirect(url_for('work_assignments'))

@app.route('/project_materials')
def project_materials():
    filter_project = request.args.get('filter_project', '')
    filter_material = request.args.get('filter_material', '')
    sort_by = request.args.get('sort_by', 'ProjectName')
    sort_order = request.args.get('sort_order', 'asc').lower()
    
    query = """
        SELECT pm.*, p.ProjectName, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Project p ON pm.ProjectID = p.ProjectID
        JOIN Material m ON pm.MaterialID = m.MaterialID
        WHERE 1=1
    """
    params = []
    
    if filter_project:
        query += " AND pm.ProjectID = %s"
        params.append(filter_project)
    if filter_material:
        query += " AND pm.MaterialID = %s"
        params.append(filter_material)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'UnitPrice':
        query += f" ORDER BY pm.UnitPrice {sql_sort_order}"
    elif sort_by == 'TotalCost':
        query += f" ORDER BY (pm.Quantity * pm.UnitPrice) {sql_sort_order}"
    else:
        query += f" ORDER BY p.ProjectName {sql_sort_order}, m.MaterialName"
    
    myCursor.execute(query, tuple(params) if params else None)
    project_materials = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = myCursor.fetchall() or []
    
    return render_template('project_materials.html', project_materials=project_materials, 
                         projects=projects, materials=materials,
                         filter_project=filter_project, filter_material=filter_material,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/project_materials/add', methods=['POST'])
def add_project_material():
    project_id = request.form.get('project_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    unit_price = request.form.get('unit_price')
    
    query = """
        INSERT INTO ProjectMaterial (ProjectID, MaterialID, Quantity, UnitPrice)
        VALUES (%s, %s, %s, %s)
    """
    myCursor.execute(query, (project_id, material_id, quantity, unit_price))
    myDB.commit()
    
    flash('Project material added successfully!', 'success')
    return redirect(url_for('project_materials'))

@app.route('/supplier_materials')
def supplier_materials():
    filter_supplier = request.args.get('filter_supplier', '')
    filter_material = request.args.get('filter_material', '')
    sort_by = request.args.get('sort_by', 'SupplierName')
    sort_order = request.args.get('sort_order', 'asc').lower()
    
    query = """
        SELECT sm.*, s.SupplierName, m.MaterialName, m.UnitOfMeasure
        FROM SupplierMaterial sm
        JOIN Supplier s ON sm.SupplierID = s.SupplierID
        JOIN Material m ON sm.MaterialID = m.MaterialID
        WHERE 1=1
    """
    params = []
    
    if filter_supplier:
        query += " AND sm.SupplierID = %s"
        params.append(filter_supplier)
    if filter_material:
        query += " AND sm.MaterialID = %s"
        params.append(filter_material)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'Price':
        query += f" ORDER BY sm.Price {sql_sort_order}"
    else:
        query += f" ORDER BY s.SupplierName {sql_sort_order}, m.MaterialName"
    
    myCursor.execute(query, tuple(params) if params else None)
    supplier_materials = myCursor.fetchall() or []
    
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = myCursor.fetchall() or []
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = myCursor.fetchall() or []
    
    return render_template('supplier_materials.html', supplier_materials=supplier_materials,
                         suppliers=suppliers, materials=materials,
                         filter_supplier=filter_supplier, filter_material=filter_material,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/supplier_materials/add', methods=['POST'])
def add_supplier_material():
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    price = request.form.get('price')
    lead_time = request.form.get('lead_time') or None
    
    query = """
        INSERT INTO SupplierMaterial (SupplierID, MaterialID, Price, LeadTime)
        VALUES (%s, %s, %s, %s)
    """
    myCursor.execute(query, (supplier_id, material_id, price, lead_time))
    myDB.commit()
    
    flash('Supplier material added successfully!', 'success')
    return redirect(url_for('supplier_materials'))

@app.route('/contracts')
def contracts():
    filter_status = request.args.get('filter_status', '')
    filter_project = request.args.get('filter_project', '')
    filter_client = request.args.get('filter_client', '')
    sort_by = request.args.get('sort_by', 'ContractID')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    query = """
        SELECT c.*, p.ProjectName, cl.ClientName
        FROM Contract c
        JOIN Project p ON c.ProjectID = p.ProjectID
        JOIN Client cl ON c.ClientID = cl.ClientID
        WHERE 1=1
    """
    params = []
    
    if filter_status:
        query += " AND c.Status = %s"
        params.append(filter_status)
    if filter_project:
        query += " AND c.ProjectID = %s"
        params.append(filter_project)
    if filter_client:
        query += " AND c.ClientID = %s"
        params.append(filter_client)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'TotalValue':
        query += f" ORDER BY c.TotalValue {sql_sort_order}"
    else:
        query += f" ORDER BY c.ContractID {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    contracts = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = myCursor.fetchall() or []
    
    return render_template('contracts.html', contracts=contracts, projects=projects, clients=clients,
                         filter_status=filter_status, filter_project=filter_project, filter_client=filter_client,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/contracts/add', methods=['POST'])
def add_contract():
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
    myCursor.execute(query, (project_id, client_id, start_date, end_date, total_value, status))
    myDB.commit()
    
    flash('Contract added successfully!', 'success')
    return redirect(url_for('contracts'))

@app.route('/phases')
def phases():
    filter_project = request.args.get('filter_project', '')
    filter_status = request.args.get('filter_status', '')
    
    query = """
        SELECT ph.*, p.ProjectName
        FROM Phase ph
        JOIN Project p ON ph.ProjectID = p.ProjectID
        WHERE 1=1
    """
    params = []
    
    if filter_project:
        query += " AND ph.ProjectID = %s"
        params.append(filter_project)
    if filter_status:
        query += " AND ph.Status = %s"
        params.append(filter_status)
    
    query += " ORDER BY ph.PhaseID DESC"
    myCursor.execute(query, tuple(params) if params else None)
    phases = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    
    return render_template('phases.html', phases=phases, projects=projects,
                         filter_project=filter_project, filter_status=filter_status)

@app.route('/phases/add', methods=['POST'])
def add_phase():
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
    myCursor.execute(query, (project_id, name, description, start_date, end_date, status))
    myDB.commit()
    
    flash('Phase added successfully!', 'success')
    return redirect(url_for('phases'))

@app.route('/schedules')
def schedules():
    filter_project = request.args.get('filter_project', '')
    filter_phase = request.args.get('filter_phase', '')
    
    query = """
        SELECT s.*, p.ProjectName, ph.Name as PhaseName
        FROM Schedule s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Phase ph ON s.PhaseID = ph.PhaseID
        WHERE 1=1
    """
    params = []
    
    if filter_project:
        query += " AND s.ProjectID = %s"
        params.append(filter_project)
    if filter_phase:
        query += " AND s.PhaseID = %s"
        params.append(filter_phase)
    
    query += " ORDER BY s.ScheduleID DESC"
    myCursor.execute(query, tuple(params) if params else None)
    schedules = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    myCursor.execute("SELECT PhaseID, Name, ProjectID FROM Phase ORDER BY PhaseID")
    phases = myCursor.fetchall() or []
    
    return render_template('schedules.html', schedules=schedules, projects=projects, phases=phases,
                         filter_project=filter_project, filter_phase=filter_phase)

@app.route('/schedules/add', methods=['POST'])
def add_schedule():
    project_id = request.form.get('project_id')
    phase_id = request.form.get('phase_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    task_details = request.form.get('task_details') or None
    
    query = """
        INSERT INTO Schedule (ProjectID, PhaseID, StartDate, EndDate, TaskDetails)
        VALUES (%s, %s, %s, %s, %s)
    """
    myCursor.execute(query, (project_id, phase_id, start_date, end_date, task_details))
    myDB.commit()
    
    flash('Schedule added successfully!', 'success')
    return redirect(url_for('schedules'))

@app.route('/sales')
def sales():
    filter_project = request.args.get('filter_project', '')
    filter_client = request.args.get('filter_client', '')
    sort_by = request.args.get('sort_by', 'SaleID')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    query = """
        SELECT s.*, p.ProjectName, c.ClientName
        FROM Sales s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Client c ON s.ClientID = c.ClientID
        WHERE 1=1
    """
    params = []
    
    if filter_project:
        query += " AND s.ProjectID = %s"
        params.append(filter_project)
    if filter_client:
        query += " AND s.ClientID = %s"
        params.append(filter_client)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'Amount':
        query += f" ORDER BY s.Amount {sql_sort_order}"
    else:
        query += f" ORDER BY s.SaleID {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    sales = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = myCursor.fetchall() or []
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = myCursor.fetchall() or []
    
    return render_template('sales.html', sales=sales, projects=projects, clients=clients,
                         filter_project=filter_project, filter_client=filter_client,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/sales/add', methods=['POST'])
def add_sale():
    project_id = request.form.get('project_id')
    client_id = request.form.get('client_id')
    amount = request.form.get('amount')
    issue_date = request.form.get('issue_date')
    due_date = request.form.get('due_date') or None
    
    query = """
        INSERT INTO Sales (ProjectID, ClientID, Amount, IssueDate, DueDate)
        VALUES (%s, %s, %s, %s, %s)
    """
    myCursor.execute(query, (project_id, client_id, amount, issue_date, due_date))
    myDB.commit()
    
    flash('Sale added successfully!', 'success')
    return redirect(url_for('sales'))

@app.route('/purchases')
def purchases():
    filter_supplier = request.args.get('filter_supplier', '')
    filter_material = request.args.get('filter_material', '')
    sort_by = request.args.get('sort_by', 'PurchaseID')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    query = """
        SELECT pu.*, s.SupplierName, m.MaterialName
        FROM Purchase pu
        JOIN Supplier s ON pu.SupplierID = s.SupplierID
        JOIN Material m ON pu.MaterialID = m.MaterialID
        WHERE 1=1
    """
    params = []
    
    if filter_supplier:
        query += " AND pu.SupplierID = %s"
        params.append(filter_supplier)
    if filter_material:
        query += " AND pu.MaterialID = %s"
        params.append(filter_material)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'TotalCost':
        query += f" ORDER BY pu.TotalCost {sql_sort_order}"
    else:
        query += f" ORDER BY pu.PurchaseID {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    purchases = myCursor.fetchall() or []
    
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = myCursor.fetchall() or []
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = myCursor.fetchall() or []
    
    return render_template('purchases.html', purchases=purchases, suppliers=suppliers, materials=materials,
                         filter_supplier=filter_supplier, filter_material=filter_material,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/purchases/add', methods=['POST'])
def add_purchase():
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    purchase_date = request.form.get('purchase_date')
    total_cost = request.form.get('total_cost')
    
    query = """
        INSERT INTO Purchase (SupplierID, MaterialID, Quantity, PurchaseDate, TotalCost)
        VALUES (%s, %s, %s, %s, %s)
    """
    myCursor.execute(query, (supplier_id, material_id, quantity, purchase_date, total_cost))
    myDB.commit()
    
    flash('Purchase added successfully!', 'success')
    return redirect(url_for('purchases'))

@app.route('/payments')
def payments():
    filter_type = request.args.get('filter_type', '')
    filter_client = request.args.get('filter_client', '')
    filter_supplier = request.args.get('filter_supplier', '')
    sort_by = request.args.get('sort_by', 'PaymentID')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    query = """
        SELECT py.*, c.ClientName, s.SupplierName
        FROM Payment py
        LEFT JOIN Client c ON py.FromClient = c.ClientID
        LEFT JOIN Supplier s ON py.ToSupplier = s.SupplierID
        WHERE 1=1
    """
    params = []
    
    if filter_type == 'client':
        query += " AND py.FromClient IS NOT NULL"
    elif filter_type == 'supplier':
        query += " AND py.ToSupplier IS NOT NULL"
    if filter_client:
        query += " AND py.FromClient = %s"
        params.append(filter_client)
    if filter_supplier:
        query += " AND py.ToSupplier = %s"
        params.append(filter_supplier)
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    if sort_by == 'Amount':
        query += f" ORDER BY py.Amount {sql_sort_order}"
    else:
        query += f" ORDER BY py.PaymentID {sql_sort_order}"
    
    myCursor.execute(query, tuple(params) if params else None)
    payments = myCursor.fetchall() or []
    
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = myCursor.fetchall() or []
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = myCursor.fetchall() or []
    
    return render_template('payments.html', payments=payments, clients=clients, suppliers=suppliers,
                         filter_type=filter_type, filter_client=filter_client, filter_supplier=filter_supplier,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/payments/add', methods=['POST'])
def add_payment():
    from_client = request.form.get('from_client') or None
    to_supplier = request.form.get('to_supplier') or None
    amount = request.form.get('amount')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method')
    
    query = """
        INSERT INTO Payment (FromClient, ToSupplier, Amount, PaymentDate, PaymentMethod)
        VALUES (%s, %s, %s, %s, %s)
    """
    myCursor.execute(query, (from_client, to_supplier, amount, payment_date, payment_method))
    myDB.commit()
    
    flash('Payment added successfully!', 'success')
    return redirect(url_for('payments'))

@app.route('/all_queries')
def all_queries():
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
    sort_by = request.args.get('sort_by', 'Profit')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    valid_sorts = {
        'Revenue': 'p.Revenue',
        'MaterialCost': 'SUM(pm.Quantity * pm.UnitPrice)',
        'LaborCost': 'SUM(wa.HoursWorked * (e.Salary / 160))',
        'Profit': '(p.Revenue - SUM(pm.Quantity * pm.UnitPrice) - SUM(wa.HoursWorked * (e.Salary / 160)))'
    }
    order_clause = valid_sorts.get(sort_by, valid_sorts['Profit'])
    
    query = f"""
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
        ORDER BY {order_clause} {sql_sort_order}
    """
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_profitability.html', results=results,
                         description='This query calculates project profitability by computing material costs, labor costs (based on employee salaries), and profit.',
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/query/supplier_impact')
def query_supplier_impact():
    sort_by = request.args.get('sort_by', 'TotalPotentialValue')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    valid_sorts = {
        'ProjectCount': 'COUNT(DISTINCT pm.ProjectID)',
        'TotalPotentialValue': 'SUM(pm.Quantity * sm.Price)'
    }
    order_clause = valid_sorts.get(sort_by, valid_sorts['TotalPotentialValue'])
    
    query = f"""
        SELECT 
            s.SupplierID,
            s.SupplierName,
            COUNT(DISTINCT pm.ProjectID) as ProjectCount,
            SUM(pm.Quantity * sm.Price) as TotalPotentialValue
        FROM Supplier s
        JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
        JOIN ProjectMaterial pm ON sm.MaterialID = pm.MaterialID
        GROUP BY s.SupplierID, s.SupplierName
        ORDER BY {order_clause} {sql_sort_order}
    """
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_supplier_impact.html', results=results,
                         description='This query analyzes supplier impact by counting distinct projects supplied (via materials) and calculating total potential value.',
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/query/cost_driver_materials')
def query_cost_driver_materials():
    sort_by = request.args.get('sort_by', 'TotalSpend')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    valid_sorts = {
        'TotalSpend': 'SUM(pm.Quantity * pm.UnitPrice)',
        'ProjectCount': 'COUNT(DISTINCT pm.ProjectID)'
    }
    order_clause = valid_sorts.get(sort_by, valid_sorts['TotalSpend'])
    
    query = f"""
        SELECT 
            m.MaterialID,
            m.MaterialName,
            SUM(pm.Quantity * pm.UnitPrice) as TotalSpend,
            COUNT(DISTINCT pm.ProjectID) as ProjectCount
        FROM Material m
        JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
        GROUP BY m.MaterialID, m.MaterialName
        ORDER BY {order_clause} {sql_sort_order}
    """
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_cost_driver_materials.html', results=results,
                         description='This query identifies cost-driving materials by total spend and shows how many projects use each material.',
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/query/employee_utilization')
def query_employee_utilization():
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
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_employee_utilization.html', results=results,
                         description='This query analyzes employee utilization by manager, showing the number of subordinates and total team hours worked.')

@app.route('/query/price_anomalies')
def query_price_anomalies():
    sort_by = request.args.get('sort_by', 'PercentDifference')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    valid_sorts = {
        'ProjectPrice': 'pm.UnitPrice',
        'MinSupplierPrice': 'MIN(sm.Price)',
        'PercentDifference': 'ROUND(((pm.UnitPrice - MIN(sm.Price)) / MIN(sm.Price)) * 100, 2)'
    }
    order_clause = valid_sorts.get(sort_by, valid_sorts['PercentDifference'])
    
    query = f"""
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
        ORDER BY {order_clause} {sql_sort_order}
    """
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_price_anomalies.html', results=results,
                         description='This query identifies price anomalies where project material prices exceed the minimum supplier price by more than 20%.',
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/query/branch_performance')
def query_branch_performance():
    sort_by = request.args.get('sort_by', 'TotalProfit')
    sort_order = request.args.get('sort_order', 'desc').lower()
    
    sql_sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
    valid_sorts = {
        'ProjectCount': 'COUNT(DISTINCT p.ProjectID)',
        'TotalRevenue': 'SUM(p.Revenue)',
        'AvgRevenuePerProject': 'AVG(p.Revenue)',
        'TotalMaterialCost': 'SUM(pm.Quantity * pm.UnitPrice)',
        'TotalLaborCost': 'SUM(wa.HoursWorked * (e.Salary / 160))',
        'TotalProfit': '(SUM(p.Revenue) - SUM(pm.Quantity * pm.UnitPrice) - SUM(wa.HoursWorked * (e.Salary / 160)))'
    }
    order_clause = valid_sorts.get(sort_by, valid_sorts['TotalProfit'])
    
    query = f"""
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
        ORDER BY {order_clause} {sql_sort_order}
    """
    
    myCursor.execute(query)
    results = myCursor.fetchall() or []
    return render_template('query_branch_performance.html', results=results,
                         description='This query compares branch performance by analyzing total revenue, project counts, material costs, labor costs, and profitability.',
                         sort_by=sort_by, sort_order=sort_order)

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=True)
