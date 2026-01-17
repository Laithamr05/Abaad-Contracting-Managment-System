# Abaad Contracting Company - Management System

A comprehensive Flask-based database management system for a construction/contracting company, designed to manage projects, employees, clients, suppliers, and financial operations.

##  Description

This is a full-stack web application for managing a contracting company's operations. The system handles project management, employee assignments, material procurement, supplier relationships, financial tracking, and provides comprehensive analytics and reporting capabilities.

The application supports both building construction projects and solar energy installations, with branches located in Palestinian cities (Ramallah, Nablus, Jerusalem).

##  Technology Stack

- **Backend**: Python 3.x + Flask
- **Database**: MySQL 8.0+
- **Frontend**: HTML/CSS/JavaScript (Bootstrap 5)
- **Architecture**: Server-side rendered web application

##  Prerequisites

- Python 3.x
- MySQL 8.0+
- pip (Python package manager)

##  Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

The database credentials are configured in `insertion.py` and `hello.py` using environment variables with defaults:
- Host: `localhost`
- User: `root`
- Password: `l18102005` (default, can be changed via `DB_PASS` environment variable)
- Database: `abaad_contracting`

You can override these defaults by setting environment variables:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASS=your_password
export DB_NAME=abaad_contracting
```

### 3. Initialize Database

Run the database initialization script to create tables and insert seed data:

```bash
python3 insertion.py
```

This script will:
- Create the database if it doesn't exist
- Create all required tables (18 tables total)
- Insert seed data (branches, employees, clients, suppliers, projects, etc.)

### 4. Run the Application

```bash
python3 hello.py
```

The application will be available at `http://localhost:5001`

## 📁 Project Structure

```
Abaad-Contracting-Managment-System/
├── hello.py              # Main Flask application
├── insertion.py          # Database schema creation and seed data
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates (Jinja2)
│   ├── index.html
│   ├── branches.html
│   ├── employees.html
│   ├── projects.html
│   └── ... (other templates)
└── static/              # Static assets
    ├── css/
    │   └── style.css
    ├── js/
    │   └── custom.js
    └── images/
        └── logo.png
```

##  Features

### Entity Management
- **Branches** - Manage company branches across different cities
- **Departments** - Organize company departments with managers
- **Employees** - Employee management with roles, positions, and hierarchy
- **Clients** - Client information and contact details
- **Projects** - Project management for Building & Solar projects
- **Suppliers** - Supplier management and material pricing
- **Materials** - Material catalog and inventory tracking
- **Contracts** - Contract management with dates and status
- **Phases** - Project phase tracking and status
- **Schedules** - Detailed project scheduling
- **Sales** - Sales records and invoicing
- **Purchases** - Purchase orders and procurement
- **Payments** - Payment tracking (from clients and to suppliers)
- **Work Assignments** - Employee-project assignments with hours tracking
- **Project Materials** - Material allocation to projects
- **Supplier Materials** - Supplier-material relationships with pricing

###  Reports & Analytics
- **Project Profitability Analysis** - Calculate profit margins including material and labor costs
- **Supplier Impact Analysis** - Evaluate supplier impact by project count and value
- **Cost Driver Materials Analysis** - Identify materials driving costs across projects
- **Employee Utilization Reports** - Analyze team utilization by manager hierarchy
- **Price Anomalies Detection** - Flag projects with material prices exceeding supplier minimums
- **Branch Performance Comparison** - Compare branch performance metrics

###  Project Types
- **Building Projects** - Construction and building projects
- **Solar Projects** - Solar energy installation projects

##  Database Schema

The system uses 18 main tables:

**Core Entities:**
- Branch, Department, Role, Employee

**Project Management:**
- Client, Project, Contract, Phase, Schedule

**Materials & Procurement:**
- Supplier, Material, SupplierMaterial, ProjectMaterial

**Operations:**
- WorkAssignment, Sales, Purchase, Payment, Project_Suppliers

All tables include proper foreign key relationships, indexes for performance, and support for cascading deletes where appropriate.

##  Configuration

### Default Settings
- **Currency**: ILS (Israeli Shekel)
- **Locations**: Palestinian cities (Ramallah, Nablus, Jerusalem)
- **Port**: 5001 (to avoid conflicts with macOS AirPlay Receiver on port 5000)

### Environment Variables
- `DB_HOST` - Database host (default: localhost)
- `DB_USER` - Database user (default: root)
- `DB_PASS` - Database password (default: l18102005)
- `DB_NAME` - Database name (default: abaad_contracting)
- `SECRET_KEY` - Flask secret key for sessions

##  Notes

- The application uses simplified SQL queries (no CTEs, window functions, or advanced SQL features)
- All database operations use basic SELECT, JOIN, GROUP BY, and aggregation functions
- The system is designed for easy maintenance and understanding
- Debug mode is enabled by default for development

##  Troubleshooting

### Port Already in Use
If port 5001 is in use, you can change it in `hello.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=True)
```

### Database Connection Issues
- Ensure MySQL server is running
- Verify database credentials in the code or environment variables
- Check that the database exists or run `insertion.py` to create it

### Module Not Found Errors
Make sure all dependencies are installed:
```bash
pip3 install -r requirements.txt
```

##  License

This project is for educational/portfolio purposes.

##  Author

Abaad Contracting Company Management System

---

**Note**: This is a production-ready management system with comprehensive features for managing a contracting company's operations, from project planning to financial tracking and analytics.
