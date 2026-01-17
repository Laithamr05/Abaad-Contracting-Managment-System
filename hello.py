from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

myDB = pymysql.connect(host="localhost", user="root", password="l18102005")
myCursor = myDB.cursor()

myCursor.execute("USE abaad_contracting")

app = Flask(__name__)
app.secret_key = 'my_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    myCursor.execute("SELECT UserID, Username, Email FROM User WHERE UserID = %s", (user_id,))
    user_data = myCursor.fetchone()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

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
    columns = [col[0] for col in myCursor.description]
    stats = [dict(zip(columns, row)) for row in myCursor.fetchall()]
    return render_template('index.html', stats=stats[0] if stats else {})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        myCursor.execute("SELECT UserID, Username, Email, Password FROM User WHERE Username = %s", (username,))
        user_data = myCursor.fetchone()
        
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('signup.html')
        
        myCursor.execute("SELECT UserID FROM User WHERE Username = %s OR Email = %s", (username, email))
        if myCursor.fetchone():
            flash('Username or email already exists', 'error')
            return render_template('signup.html')
        
        hashed_password = generate_password_hash(password)
        myCursor.execute("INSERT INTO User (Username, Email, Password) VALUES (%s, %s, %s)", 
                        (username, email, hashed_password))
        myDB.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/branches')
@login_required
def branches():
    filter_city = request.args.get('filter_city', '').strip() or None
    
    query = """
        SELECT b.*, 
               COUNT(DISTINCT e.EmployeeID) as employee_count,
               COUNT(DISTINCT p.ProjectID) as project_count
        FROM Branch b
        LEFT JOIN Employee e ON b.BranchID = e.BranchID
        LEFT JOIN Project p ON b.BranchID = p.BranchID
    """
    
    if filter_city:
        query += " WHERE b.City = %s"
        query += " GROUP BY b.BranchID ORDER BY b.BranchName"
        myCursor.execute(query, (filter_city,))
    else:
        query += " GROUP BY b.BranchID ORDER BY b.BranchName"
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    branches = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT DISTINCT City FROM Branch ORDER BY City")
    cities = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/branches/update/<int:branch_id>', methods=['POST'])
def update_branch(branch_id):
    branch_name = request.form.get('branch_name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    query = "UPDATE Branch SET BranchName = %s, City = %s, Address = %s, PhoneNumber = %s WHERE BranchID = %s"
    myCursor.execute(query, (branch_name, city, address, phone, branch_id))
    myDB.commit()
    
    flash('Branch updated successfully!', 'success')
    return redirect(url_for('branches'))

@app.route('/branches/delete/<int:branch_id>', methods=['POST'])
def delete_branch(branch_id):
    try:
        query = "DELETE FROM Branch WHERE BranchID = %s"
        myCursor.execute(query, (branch_id,))
        myDB.commit()
        flash('Branch deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting branch: {str(e)}', 'error')
    return redirect(url_for('branches'))

@app.route('/employees')
@login_required
def employees():
    filter_branch = request.args.get('filter_branch', '').strip() or None
    filter_department = request.args.get('filter_department', '').strip() or None
    filter_role = request.args.get('filter_role', '').strip() or None
    filter_manager = request.args.get('filter_manager', '').strip() or None
    filter_is_manager = request.args.get('filter_is_manager', '').strip() or None
    sort_by = request.args.get('sort_by', 'EmployeeName')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = """
        SELECT e.*, b.BranchName, d.DepartmentName,
               m.EmployeeName as ManagerName, r.Title as Position
        FROM Employee e
        JOIN Branch b ON e.BranchID = b.BranchID
        JOIN Department d ON e.DepartmentID = d.DepartmentID
        JOIN Role r ON e.PositionID = r.RoleID
        LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
    """
    
    conditions = []
    params = []
    
    if filter_branch:
        conditions.append("e.BranchID = %s")
        params.append(filter_branch)
    if filter_department:
        conditions.append("e.DepartmentID = %s")
        params.append(filter_department)
    if filter_role:
        conditions.append("e.PositionID = %s")
        params.append(filter_role)
    if filter_manager:
        conditions.append("e.ManagerID = %s")
        params.append(filter_manager)
    if filter_is_manager:
        conditions.append("e.IsManager = %s")
        params.append(filter_is_manager == 'true')
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    valid_sort_columns = ['EmployeeName', 'Salary']
    if sort_by not in valid_sort_columns:
        sort_by = 'EmployeeName'
    
    query += f" ORDER BY e.{sort_by} {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    employees = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName")
    branches = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT DepartmentID, DepartmentName FROM Department ORDER BY DepartmentName")
    departments = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT RoleID, Title FROM Role ORDER BY Title")
    roles = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee WHERE IsManager = TRUE ORDER BY EmployeeName")
    managers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    return render_template('employees.html', employees=employees, branches=branches, 
                         departments=departments, roles=roles, managers=managers,
                         filter_branch=filter_branch, filter_department=filter_department,
                         filter_role=filter_role, filter_manager=filter_manager,
                         filter_is_manager=filter_is_manager, sort_by=sort_by, sort_order=sort_order)

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

@app.route('/employees/update/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    name = request.form.get('employee_name')
    position_id = request.form.get('position_id')
    salary = request.form.get('salary')
    branch_id = request.form.get('branch_id')
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    is_manager = request.form.get('is_manager') == 'on'
    
    query = """
        UPDATE Employee SET EmployeeName = %s, PositionID = %s, Salary = %s, 
        BranchID = %s, DepartmentID = %s, ManagerID = %s, IsManager = %s 
        WHERE EmployeeID = %s
    """
    myCursor.execute(query, (name, position_id, salary, branch_id, dept_id, manager_id, is_manager, employee_id))
    myDB.commit()
    
    flash('Employee updated successfully!', 'success')
    return redirect(url_for('employees'))

@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        query = "DELETE FROM Employee WHERE EmployeeID = %s"
        myCursor.execute(query, (employee_id,))
        myDB.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    return redirect(url_for('employees'))

@app.route('/departments')
@login_required
def departments():
    filter_manager = request.args.get('filter_manager', '').strip() or None
    
    query = """
        SELECT d.*, e.EmployeeName as ManagerName,
               COUNT(DISTINCT emp.EmployeeID) as employee_count
        FROM Department d
        LEFT JOIN Employee e ON d.ManagerID = e.EmployeeID
        LEFT JOIN Employee emp ON d.DepartmentID = emp.DepartmentID
    """
    
    if filter_manager:
        query += " WHERE d.ManagerID = %s"
        query += " GROUP BY d.DepartmentID ORDER BY d.DepartmentName"
        myCursor.execute(query, (filter_manager,))
    else:
        query += " GROUP BY d.DepartmentID ORDER BY d.DepartmentName"
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    departments = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee WHERE IsManager = TRUE ORDER BY EmployeeName")
    managers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    employees = managers
    
    return render_template('departments.html', departments=departments, managers=managers, employees=employees, filter_manager=filter_manager)

@app.route('/departments/add', methods=['POST'])
def add_department():
    dept_name = request.form.get('department_name')
    manager_id = request.form.get('manager_id') or None
    
    query = "INSERT INTO Department (DepartmentName, ManagerID) VALUES (%s, %s)"
    myCursor.execute(query, (dept_name, manager_id))
    myDB.commit()
    
    flash('Department added successfully!', 'success')
    return redirect(url_for('departments'))

@app.route('/departments/set_manager', methods=['POST'])
def set_department_manager():
    dept_id = request.form.get('department_id')
    manager_id = request.form.get('manager_id') or None
    
    query = "UPDATE Department SET ManagerID = %s WHERE DepartmentID = %s"
    myCursor.execute(query, (manager_id, dept_id))
    myDB.commit()
    
    flash('Department manager updated successfully!', 'success')
    return redirect(url_for('departments'))

@app.route('/departments/update/<int:dept_id>', methods=['POST'])
def update_department(dept_id):
    dept_name = request.form.get('department_name')
    manager_id = request.form.get('manager_id') or None
    
    query = "UPDATE Department SET DepartmentName = %s, ManagerID = %s WHERE DepartmentID = %s"
    myCursor.execute(query, (dept_name, manager_id, dept_id))
    myDB.commit()
    
    flash('Department updated successfully!', 'success')
    return redirect(url_for('departments'))

@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    try:
        query = "DELETE FROM Department WHERE DepartmentID = %s"
        myCursor.execute(query, (dept_id,))
        myDB.commit()
        flash('Department deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting department: {str(e)}', 'error')
    return redirect(url_for('departments'))

@app.route('/clients')
@login_required
def clients():
    filter_has_projects = request.args.get('filter_has_projects', '').strip() or None
    
    query = """
        SELECT c.*, COUNT(DISTINCT p.ProjectID) as project_count
        FROM Client c
        LEFT JOIN Project p ON c.ClientID = p.ClientID
    """
    
    if filter_has_projects == 'yes':
        query += " GROUP BY c.ClientID HAVING COUNT(DISTINCT p.ProjectID) > 0"
    elif filter_has_projects == 'no':
        query += " GROUP BY c.ClientID HAVING COUNT(DISTINCT p.ProjectID) = 0"
    else:
        query += " GROUP BY c.ClientID"
    
    query += " ORDER BY c.ClientName"
    
    myCursor.execute(query)
    clients = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
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

@app.route('/clients/update/<int:client_id>', methods=['POST'])
def update_client(client_id):
    name = request.form.get('client_name')
    contact = request.form.get('contact_info')
    
    query = "UPDATE Client SET ClientName = %s, ContactInfo = %s WHERE ClientID = %s"
    myCursor.execute(query, (name, contact, client_id))
    myDB.commit()
    
    flash('Client updated successfully!', 'success')
    return redirect(url_for('clients'))

@app.route('/clients/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    try:
        query = "DELETE FROM Client WHERE ClientID = %s"
        myCursor.execute(query, (client_id,))
        myDB.commit()
        flash('Client deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting client: {str(e)}', 'error')
    return redirect(url_for('clients'))

@app.route('/projects')
@login_required
def projects():
    filter_type = request.args.get('filter_type', '').strip() or None
    filter_branch = request.args.get('filter_branch', '').strip() or None
    filter_client = request.args.get('filter_client', '').strip() or None
    sort_by = request.args.get('sort_by', 'ProjectID')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
    """
    
    conditions = []
    params = []
    
    if filter_type:
        conditions.append("p.ProjectType = %s")
        params.append(filter_type)
    if filter_branch:
        conditions.append("p.BranchID = %s")
        params.append(filter_branch)
    if filter_client:
        conditions.append("p.ClientID = %s")
        params.append(filter_client)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    valid_sort_columns = ['ProjectID', 'Cost', 'Revenue']
    if sort_by not in valid_sort_columns:
        sort_by = 'ProjectID'
    
    query += f" ORDER BY p.{sort_by} {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    projects = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT BranchID, BranchName FROM Branch ORDER BY BranchName")
    branches = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    return render_template('projects.html', projects=projects, branches=branches, clients=clients,
                         filter_type=filter_type, filter_branch=filter_branch, filter_client=filter_client,
                         sort_by=sort_by, sort_order=sort_order)

@app.route('/projects/<int:project_id>')
@login_required
def project_details(project_id):
    query = """
        SELECT p.*, b.BranchName, c.ClientName
        FROM Project p
        JOIN Branch b ON p.BranchID = b.BranchID
        JOIN Client c ON p.ClientID = c.ClientID
        WHERE p.ProjectID = %s
    """
    myCursor.execute(query, (project_id,))
    cols = [c[0] for c in myCursor.description]
    project = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
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
    assignments = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    materials_query = """
        SELECT pm.*, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Material m ON pm.MaterialID = m.MaterialID
        WHERE pm.ProjectID = %s
    """
    myCursor.execute(materials_query, (project_id,))
    materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/projects/update/<int:project_id>', methods=['POST'])
def update_project(project_id):
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
                UPDATE Project SET ProjectName = %s, Location = %s, Cost = %s, 
                Revenue = %s, ProjectType = %s, BranchID = %s, ClientID = %s 
                WHERE ProjectID = %s
            """
            myCursor.execute(query, (name, location, cost, revenue, project_type, branch_id, client_id, project_id))
        else:
            query = """
                UPDATE Project SET ProjectName = %s, Location = %s, Cost = %s, 
                Revenue = %s, BranchID = %s, ClientID = %s 
                WHERE ProjectID = %s
            """
            myCursor.execute(query, (name, location, cost, revenue, branch_id, client_id, project_id))
        
        myDB.commit()
        flash('Project updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating project: {str(e)}', 'error')
    
    return redirect(url_for('projects'))

@app.route('/projects/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    try:
        query = "DELETE FROM Project WHERE ProjectID = %s"
        myCursor.execute(query, (project_id,))
        myDB.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting project: {str(e)}', 'error')
    return redirect(url_for('projects'))

@app.route('/suppliers')
@login_required
def suppliers():
    filter_has_materials = request.args.get('filter_has_materials', '').strip() or None
    
    query = """
        SELECT s.*, COUNT(DISTINCT sm.MaterialID) as material_count
        FROM Supplier s
        LEFT JOIN SupplierMaterial sm ON s.SupplierID = sm.SupplierID
    """
    
    if filter_has_materials == 'yes':
        query += " GROUP BY s.SupplierID HAVING COUNT(DISTINCT sm.MaterialID) > 0"
    elif filter_has_materials == 'no':
        query += " GROUP BY s.SupplierID HAVING COUNT(DISTINCT sm.MaterialID) = 0"
    else:
        query += " GROUP BY s.SupplierID"
    
    query += " ORDER BY s.SupplierName"
    
    myCursor.execute(query)
    suppliers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
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

@app.route('/suppliers/update/<int:supplier_id>', methods=['POST'])
def update_supplier(supplier_id):
    name = request.form.get('supplier_name')
    contact = request.form.get('contact_info')
    
    query = "UPDATE Supplier SET SupplierName = %s, ContactInfo = %s WHERE SupplierID = %s"
    myCursor.execute(query, (name, contact, supplier_id))
    myDB.commit()
    
    flash('Supplier updated successfully!', 'success')
    return redirect(url_for('suppliers'))

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    try:
        query = "DELETE FROM Supplier WHERE SupplierID = %s"
        myCursor.execute(query, (supplier_id,))
        myDB.commit()
        flash('Supplier deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting supplier: {str(e)}', 'error')
    return redirect(url_for('suppliers'))

@app.route('/materials')
@login_required
def materials():
    filter_unit = request.args.get('filter_unit', '').strip() or None
    sort_by = request.args.get('sort_by', 'MaterialName')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = "SELECT * FROM Material"
    conditions = []
    params = []
    
    if filter_unit:
        conditions.append("UnitOfMeasure = %s")
        params.append(filter_unit)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    valid_sort_columns = ['MaterialName', 'BaseUnitPrice']
    if sort_by not in valid_sort_columns:
        sort_by = 'MaterialName'
    
    query += f" ORDER BY {sort_by} {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT DISTINCT UnitOfMeasure FROM Material WHERE UnitOfMeasure IS NOT NULL ORDER BY UnitOfMeasure")
    units = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    return render_template('materials.html', materials=materials, units=units, filter_unit=filter_unit, sort_by=sort_by, sort_order=sort_order)

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

@app.route('/materials/update/<int:material_id>', methods=['POST'])
def update_material(material_id):
    name = request.form.get('material_name')
    base_price = request.form.get('base_unit_price')
    unit = request.form.get('unit_of_measure')
    
    query = "UPDATE Material SET MaterialName = %s, BaseUnitPrice = %s, UnitOfMeasure = %s WHERE MaterialID = %s"
    myCursor.execute(query, (name, base_price, unit, material_id))
    myDB.commit()
    
    flash('Material updated successfully!', 'success')
    return redirect(url_for('materials'))

@app.route('/materials/delete/<int:material_id>', methods=['POST'])
def delete_material(material_id):
    try:
        query = "DELETE FROM Material WHERE MaterialID = %s"
        myCursor.execute(query, (material_id,))
        myDB.commit()
        flash('Material deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting material: {str(e)}', 'error')
    return redirect(url_for('materials'))

@app.route('/work_assignments')
@login_required
def work_assignments():
    query = """
        SELECT wa.*, p.ProjectName, e.EmployeeName, r.Title as Position
        FROM WorkAssignment wa
        JOIN Project p ON wa.ProjectID = p.ProjectID
        JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        JOIN Role r ON e.PositionID = r.RoleID
        ORDER BY wa.StartDate DESC
    """
    myCursor.execute(query)
    cols = [c[0] for c in myCursor.description]
    assignments = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT EmployeeID, EmployeeName FROM Employee ORDER BY EmployeeName")
    employees = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT DISTINCT Role FROM WorkAssignment ORDER BY Role")
    roles = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    return render_template('work_assignments.html', assignments=assignments, projects=projects, 
                         employees=employees, roles=roles)

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

@app.route('/work_assignments/update/<int:assignment_id>', methods=['POST'])
def update_work_assignment(assignment_id):
    project_id = request.form.get('project_id')
    employee_id = request.form.get('employee_id')
    role = request.form.get('role')
    hours = request.form.get('hours_worked') or 0
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    
    query = """
        UPDATE WorkAssignment SET ProjectID = %s, EmployeeID = %s, Role = %s, 
        HoursWorked = %s, StartDate = %s, EndDate = %s 
        WHERE AssignmentID = %s
    """
    myCursor.execute(query, (project_id, employee_id, role, hours, start_date, end_date, assignment_id))
    myDB.commit()
    
    flash('Work assignment updated successfully!', 'success')
    return redirect(url_for('work_assignments'))

@app.route('/work_assignments/delete/<int:assignment_id>', methods=['POST'])
def delete_work_assignment(assignment_id):
    try:
        query = "DELETE FROM WorkAssignment WHERE AssignmentID = %s"
        myCursor.execute(query, (assignment_id,))
        myDB.commit()
        flash('Work assignment deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting work assignment: {str(e)}', 'error')
    return redirect(url_for('work_assignments'))

@app.route('/project_materials')
@login_required
def project_materials():
    filter_project = request.args.get('filter_project', '').strip() or None
    filter_material = request.args.get('filter_material', '').strip() or None
    sort_by = request.args.get('sort_by', 'UnitPrice')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = """
        SELECT pm.*, p.ProjectName, m.MaterialName, m.UnitOfMeasure
        FROM ProjectMaterial pm
        JOIN Project p ON pm.ProjectID = p.ProjectID
        JOIN Material m ON pm.MaterialID = m.MaterialID
    """
    
    conditions = []
    params = []
    
    if filter_project:
        conditions.append("pm.ProjectID = %s")
        params.append(filter_project)
    if filter_material:
        conditions.append("pm.MaterialID = %s")
        params.append(filter_material)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    valid_sort_columns = ['UnitPrice', 'TotalCost']
    if sort_by not in valid_sort_columns:
        sort_by = 'UnitPrice'
    
    if sort_by == 'TotalCost':
        query += f" ORDER BY (pm.Quantity * pm.UnitPrice) {sort_order.upper()}"
    else:
        query += f" ORDER BY pm.{sort_by} {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    project_materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/project_materials/update/<int:project_material_id>', methods=['POST'])
def update_project_material(project_material_id):
    project_id = request.form.get('project_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    unit_price = request.form.get('unit_price')
    
    query = """
        UPDATE ProjectMaterial SET ProjectID = %s, MaterialID = %s, 
        Quantity = %s, UnitPrice = %s 
        WHERE ProjectMaterialID = %s
    """
    myCursor.execute(query, (project_id, material_id, quantity, unit_price, project_material_id))
    myDB.commit()
    
    flash('Project material updated successfully!', 'success')
    return redirect(url_for('project_materials'))

@app.route('/project_materials/delete/<int:project_material_id>', methods=['POST'])
def delete_project_material(project_material_id):
    try:
        query = "DELETE FROM ProjectMaterial WHERE ProjectMaterialID = %s"
        myCursor.execute(query, (project_material_id,))
        myDB.commit()
        flash('Project material deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting project material: {str(e)}', 'error')
    return redirect(url_for('project_materials'))

@app.route('/supplier_materials')
@login_required
def supplier_materials():
    filter_supplier = request.args.get('filter_supplier', '').strip() or None
    filter_material = request.args.get('filter_material', '').strip() or None
    sort_by = request.args.get('sort_by', 'Price')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = """
        SELECT sm.*, s.SupplierName, m.MaterialName, m.UnitOfMeasure
        FROM SupplierMaterial sm
        JOIN Supplier s ON sm.SupplierID = s.SupplierID
        JOIN Material m ON sm.MaterialID = m.MaterialID
    """
    
    conditions = []
    params = []
    
    if filter_supplier:
        conditions.append("sm.SupplierID = %s")
        params.append(filter_supplier)
    if filter_material:
        conditions.append("sm.MaterialID = %s")
        params.append(filter_material)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY sm.Price {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    supplier_materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/supplier_materials/update/<int:supplier_material_id>', methods=['POST'])
def update_supplier_material(supplier_material_id):
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    price = request.form.get('price')
    lead_time = request.form.get('lead_time') or None
    
    query = """
        UPDATE SupplierMaterial SET SupplierID = %s, MaterialID = %s, 
        Price = %s, LeadTime = %s 
        WHERE SupplierMaterialID = %s
    """
    myCursor.execute(query, (supplier_id, material_id, price, lead_time, supplier_material_id))
    myDB.commit()
    
    flash('Supplier material updated successfully!', 'success')
    return redirect(url_for('supplier_materials'))

@app.route('/supplier_materials/delete/<int:supplier_material_id>', methods=['POST'])
def delete_supplier_material(supplier_material_id):
    try:
        query = "DELETE FROM SupplierMaterial WHERE SupplierMaterialID = %s"
        myCursor.execute(query, (supplier_material_id,))
        myDB.commit()
        flash('Supplier material deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting supplier material: {str(e)}', 'error')
    return redirect(url_for('supplier_materials'))

@app.route('/contracts')
@login_required
def contracts():
    filter_status = request.args.get('filter_status', '').strip() or None
    filter_project = request.args.get('filter_project', '').strip() or None
    filter_client = request.args.get('filter_client', '').strip() or None
    sort_by = request.args.get('sort_by', 'TotalValue')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = """
        SELECT c.*, p.ProjectName, cl.ClientName
        FROM Contract c
        JOIN Project p ON c.ProjectID = p.ProjectID
        JOIN Client cl ON c.ClientID = cl.ClientID
    """
    
    conditions = []
    params = []
    
    if filter_status:
        conditions.append("c.Status = %s")
        params.append(filter_status)
    if filter_project:
        conditions.append("c.ProjectID = %s")
        params.append(filter_project)
    if filter_client:
        conditions.append("c.ClientID = %s")
        params.append(filter_client)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY c.TotalValue {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    contracts = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/contracts/update/<int:contract_id>', methods=['POST'])
def update_contract(contract_id):
    project_id = request.form.get('project_id')
    client_id = request.form.get('client_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    total_value = request.form.get('total_value')
    status = request.form.get('status', 'active')
    
    query = """
        UPDATE Contract SET ProjectID = %s, ClientID = %s, StartDate = %s, 
        EndDate = %s, TotalValue = %s, Status = %s 
        WHERE ContractID = %s
    """
    myCursor.execute(query, (project_id, client_id, start_date, end_date, total_value, status, contract_id))
    myDB.commit()
    
    flash('Contract updated successfully!', 'success')
    return redirect(url_for('contracts'))

@app.route('/contracts/delete/<int:contract_id>', methods=['POST'])
def delete_contract(contract_id):
    try:
        query = "DELETE FROM Contract WHERE ContractID = %s"
        myCursor.execute(query, (contract_id,))
        myDB.commit()
        flash('Contract deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting contract: {str(e)}', 'error')
    return redirect(url_for('contracts'))

@app.route('/phases')
@login_required
def phases():
    filter_project = request.args.get('filter_project', '').strip() or None
    filter_status = request.args.get('filter_status', '').strip() or None
    
    query = """
        SELECT ph.*, p.ProjectName
        FROM Phase ph
        JOIN Project p ON ph.ProjectID = p.ProjectID
    """
    
    conditions = []
    params = []
    
    if filter_project:
        conditions.append("ph.ProjectID = %s")
        params.append(filter_project)
    if filter_status:
        conditions.append("ph.Status = %s")
        params.append(filter_status)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY ph.PhaseID DESC"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    phases = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/phases/update/<int:phase_id>', methods=['POST'])
def update_phase(phase_id):
    project_id = request.form.get('project_id')
    name = request.form.get('name')
    description = request.form.get('description') or None
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    status = request.form.get('status', 'planned')
    
    query = """
        UPDATE Phase SET ProjectID = %s, Name = %s, Description = %s, 
        StartDate = %s, EndDate = %s, Status = %s 
        WHERE PhaseID = %s
    """
    myCursor.execute(query, (project_id, name, description, start_date, end_date, status, phase_id))
    myDB.commit()
    
    flash('Phase updated successfully!', 'success')
    return redirect(url_for('phases'))

@app.route('/phases/delete/<int:phase_id>', methods=['POST'])
def delete_phase(phase_id):
    try:
        query = "DELETE FROM Phase WHERE PhaseID = %s"
        myCursor.execute(query, (phase_id,))
        myDB.commit()
        flash('Phase deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting phase: {str(e)}', 'error')
    return redirect(url_for('phases'))

@app.route('/schedules')
@login_required
def schedules():
    filter_project = request.args.get('filter_project', '').strip() or None
    filter_phase = request.args.get('filter_phase', '').strip() or None
    
    query = """
        SELECT s.*, p.ProjectName, ph.Name as PhaseName
        FROM Schedule s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Phase ph ON s.PhaseID = ph.PhaseID
    """
    
    conditions = []
    params = []
    
    if filter_project:
        conditions.append("s.ProjectID = %s")
        params.append(filter_project)
    if filter_phase:
        conditions.append("s.PhaseID = %s")
        params.append(filter_phase)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY s.ScheduleID DESC"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    schedules = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT PhaseID, Name, ProjectID FROM Phase ORDER BY PhaseID")
    phases = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/schedules/update/<int:schedule_id>', methods=['POST'])
def update_schedule(schedule_id):
    project_id = request.form.get('project_id')
    phase_id = request.form.get('phase_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') or None
    task_details = request.form.get('task_details') or None
    
    query = """
        UPDATE Schedule SET ProjectID = %s, PhaseID = %s, StartDate = %s, 
        EndDate = %s, TaskDetails = %s 
        WHERE ScheduleID = %s
    """
    myCursor.execute(query, (project_id, phase_id, start_date, end_date, task_details, schedule_id))
    myDB.commit()
    
    flash('Schedule updated successfully!', 'success')
    return redirect(url_for('schedules'))

@app.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    try:
        query = "DELETE FROM Schedule WHERE ScheduleID = %s"
        myCursor.execute(query, (schedule_id,))
        myDB.commit()
        flash('Schedule deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting schedule: {str(e)}', 'error')
    return redirect(url_for('schedules'))

@app.route('/sales')
@login_required
def sales():
    filter_project = request.args.get('filter_project', '').strip() or None
    filter_client = request.args.get('filter_client', '').strip() or None
    sort_by = request.args.get('sort_by', 'SaleID')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = """
        SELECT s.*, p.ProjectName, c.ClientName
        FROM Sales s
        JOIN Project p ON s.ProjectID = p.ProjectID
        JOIN Client c ON s.ClientID = c.ClientID
    """
    
    conditions = []
    params = []
    
    if filter_project:
        conditions.append("s.ProjectID = %s")
        params.append(filter_project)
    if filter_client:
        conditions.append("s.ClientID = %s")
        params.append(filter_client)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    valid_sort_columns = ['SaleID', 'Amount']
    if sort_by not in valid_sort_columns:
        sort_by = 'SaleID'
    
    query += f" ORDER BY s.{sort_by} {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    cols = [c[0] for c in myCursor.description]
    sales = [dict(zip(cols, r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ProjectID, ProjectName FROM Project ORDER BY ProjectName")
    projects = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/sales/update/<int:sale_id>', methods=['POST'])
def update_sale(sale_id):
    project_id = request.form.get('project_id')
    client_id = request.form.get('client_id')
    amount = request.form.get('amount')
    issue_date = request.form.get('issue_date')
    due_date = request.form.get('due_date') or None
    
    query = """
        UPDATE Sales SET ProjectID = %s, ClientID = %s, Amount = %s, 
        IssueDate = %s, DueDate = %s 
        WHERE SaleID = %s
    """
    myCursor.execute(query, (project_id, client_id, amount, issue_date, due_date, sale_id))
    myDB.commit()
    
    flash('Sale updated successfully!', 'success')
    return redirect(url_for('sales'))

@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    try:
        query = "DELETE FROM Sales WHERE SaleID = %s"
        myCursor.execute(query, (sale_id,))
        myDB.commit()
        flash('Sale deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting sale: {str(e)}', 'error')
    return redirect(url_for('sales'))

@app.route('/purchases')
@login_required
def purchases():
    filter_supplier = request.args.get('filter_supplier', '').strip() or None
    filter_material = request.args.get('filter_material', '').strip() or None
    sort_by = request.args.get('sort_by', 'TotalCost')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = """
        SELECT pu.*, s.SupplierName, m.MaterialName
        FROM Purchase pu
        JOIN Supplier s ON pu.SupplierID = s.SupplierID
        JOIN Material m ON pu.MaterialID = m.MaterialID
    """
    
    conditions = []
    params = []
    
    if filter_supplier:
        conditions.append("pu.SupplierID = %s")
        params.append(filter_supplier)
    if filter_material:
        conditions.append("pu.MaterialID = %s")
        params.append(filter_material)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY pu.TotalCost {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    purchases = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT MaterialID, MaterialName FROM Material ORDER BY MaterialName")
    materials = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/purchases/update/<int:purchase_id>', methods=['POST'])
def update_purchase(purchase_id):
    supplier_id = request.form.get('supplier_id')
    material_id = request.form.get('material_id')
    quantity = request.form.get('quantity')
    purchase_date = request.form.get('purchase_date')
    total_cost = request.form.get('total_cost')
    
    query = """
        UPDATE Purchase SET SupplierID = %s, MaterialID = %s, Quantity = %s, 
        PurchaseDate = %s, TotalCost = %s 
        WHERE PurchaseID = %s
    """
    myCursor.execute(query, (supplier_id, material_id, quantity, purchase_date, total_cost, purchase_id))
    myDB.commit()
    
    flash('Purchase updated successfully!', 'success')
    return redirect(url_for('purchases'))

@app.route('/purchases/delete/<int:purchase_id>', methods=['POST'])
def delete_purchase(purchase_id):
    try:
        query = "DELETE FROM Purchase WHERE PurchaseID = %s"
        myCursor.execute(query, (purchase_id,))
        myDB.commit()
        flash('Purchase deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting purchase: {str(e)}', 'error')
    return redirect(url_for('purchases'))

@app.route('/payments')
@login_required
def payments():
    filter_type = request.args.get('filter_type', '').strip() or None
    filter_client = request.args.get('filter_client', '').strip() or None
    filter_supplier = request.args.get('filter_supplier', '').strip() or None
    sort_by = request.args.get('sort_by', 'Amount')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = """
        SELECT py.*, c.ClientName, s.SupplierName
        FROM Payment py
        LEFT JOIN Client c ON py.FromClient = c.ClientID
        LEFT JOIN Supplier s ON py.ToSupplier = s.SupplierID
    """
    
    conditions = []
    params = []
    
    if filter_type == 'client':
        conditions.append("py.FromClient IS NOT NULL")
    elif filter_type == 'supplier':
        conditions.append("py.ToSupplier IS NOT NULL")
    
    if filter_client:
        conditions.append("py.FromClient = %s")
        params.append(filter_client)
    if filter_supplier:
        conditions.append("py.ToSupplier = %s")
        params.append(filter_supplier)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY py.Amount {sort_order.upper()}"
    
    if params:
        myCursor.execute(query, tuple(params))
    else:
        myCursor.execute(query)
    
    payments = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
    myCursor.execute("SELECT ClientID, ClientName FROM Client ORDER BY ClientName")
    clients = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    myCursor.execute("SELECT SupplierID, SupplierName FROM Supplier ORDER BY SupplierName")
    suppliers = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    
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

@app.route('/payments/update/<int:payment_id>', methods=['POST'])
def update_payment(payment_id):
    from_client = request.form.get('from_client') or None
    to_supplier = request.form.get('to_supplier') or None
    amount = request.form.get('amount')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method')
    
    query = """
        UPDATE Payment SET FromClient = %s, ToSupplier = %s, Amount = %s, 
        PaymentDate = %s, PaymentMethod = %s 
        WHERE PaymentID = %s
    """
    myCursor.execute(query, (from_client, to_supplier, amount, payment_date, payment_method, payment_id))
    myDB.commit()
    
    flash('Payment updated successfully!', 'success')
    return redirect(url_for('payments'))

@app.route('/payments/delete/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    try:
        query = "DELETE FROM Payment WHERE PaymentID = %s"
        myCursor.execute(query, (payment_id,))
        myDB.commit()
        flash('Payment deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting payment: {str(e)}', 'error')
    return redirect(url_for('payments'))

@app.route('/all_queries')
@login_required
def all_queries():
    queries = [
        {
            'id': 'profitability',
            'name': 'Project Profit',
            'description': 'Project revenue, cost, and profit',
            'url': url_for('query_project_profit')
        },
        {
            'id': 'supplier_impact',
            'name': 'Supplier Impact',
            'description': 'Number of projects per supplier',
            'url': url_for('query_supplier_projects')
        },
        {
            'id': 'cost_driver_materials',
            'name': 'Material Costs',
            'description': 'Total spending per material',
            'url': url_for('query_material_spending')
        },
        {
            'id': 'employee_utilization',
            'name': 'Team Hours',
            'description': 'Total hours worked per employee',
            'url': url_for('query_employee_hours')
        },
        {
            'id': 'price_anomalies',
            'name': 'Price Issues',
            'description': 'Materials priced above supplier minimum',
            'url': url_for('query_high_prices')
        },
        {
            'id': 'branch_performance',
            'name': 'Branch Performance',
            'description': 'Projects and revenue per branch',
            'url': url_for('query_branch_revenue')
        }
    ]
    return render_template('all_queries.html', queries=queries)

@app.route('/query/project_profit')
@login_required
def query_project_profit():
    query = """
        SELECT p.ProjectID, p.ProjectName, p.Revenue, p.Cost, 
               (p.Revenue - p.Cost) as Profit
        FROM Project p
        ORDER BY Profit DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_profitability.html', results=results)

@app.route('/query/supplier_projects')
@login_required
def query_supplier_projects():
    query = """
        SELECT s.SupplierID, s.SupplierName, COUNT(ps.ProjectID) as ProjectCount
        FROM Supplier s
        LEFT JOIN Project_Suppliers ps ON s.SupplierID = ps.SupplierID
        GROUP BY s.SupplierID, s.SupplierName
        ORDER BY ProjectCount DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_supplier_impact.html', results=results)

@app.route('/query/material_spending')
@login_required
def query_material_spending():
    query = """
        SELECT m.MaterialID, m.MaterialName, SUM(pm.Quantity * pm.UnitPrice) as TotalSpend
        FROM Material m
        JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
        GROUP BY m.MaterialID, m.MaterialName
        ORDER BY TotalSpend DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_cost_driver_materials.html', results=results)

@app.route('/query/employee_hours')
@login_required
def query_employee_hours():
    query = """
        SELECT e.EmployeeID, e.EmployeeName, SUM(wa.HoursWorked) as TotalHours
        FROM Employee e
        LEFT JOIN WorkAssignment wa ON e.EmployeeID = wa.EmployeeID
        GROUP BY e.EmployeeID, e.EmployeeName
        ORDER BY TotalHours DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_employee_utilization.html', results=results)

@app.route('/query/high_prices')
@login_required
def query_high_prices():
    query = """
        SELECT pm.ProjectID, p.ProjectName, m.MaterialName, pm.UnitPrice, MIN(sm.Price) as MinPrice
        FROM ProjectMaterial pm
        JOIN Material m ON pm.MaterialID = m.MaterialID
        JOIN SupplierMaterial sm ON pm.MaterialID = sm.MaterialID
        JOIN Project p ON pm.ProjectID = p.ProjectID
        GROUP BY pm.ProjectID, p.ProjectName, m.MaterialName, pm.UnitPrice
        HAVING pm.UnitPrice > MIN(sm.Price) * 1.2
        ORDER BY pm.UnitPrice DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_price_anomalies.html', results=results)

@app.route('/query/branch_revenue')
@login_required
def query_branch_revenue():
    query = """
        SELECT b.BranchID, b.BranchName, b.City, COUNT(p.ProjectID) as ProjectCount, SUM(p.Revenue) as TotalRevenue
        FROM Branch b
        LEFT JOIN Project p ON b.BranchID = p.BranchID
        GROUP BY b.BranchID, b.BranchName, b.City
        ORDER BY TotalRevenue DESC
    """
    myCursor.execute(query)
    results = [dict(zip([c[0] for c in myCursor.description], r)) for r in myCursor.fetchall()]
    return render_template('query_branch_performance.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
