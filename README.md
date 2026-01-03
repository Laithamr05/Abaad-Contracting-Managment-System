# Abaad Contracting Company - Management System

A Flask-based database management system for a construction/contracting company, designed to manage projects, employees, clients, suppliers, and financial operations.

## Technology Stack

- **Database**: MySQL 8.0+
- **Backend**: Python 3.x + Flask
- **Frontend**: HTML/CSS/JavaScript (Bootstrap 5)
- **Architecture**: Server-side rendered web application

## Quick Start

### 1. Prerequisites

- Python 3.x
- MySQL 8.0+
- pip (Python package manager)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Configure your database credentials in `insertion.py` (or use environment variables):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'abaad_contracting'
}
```

Run the database initialization script:

```bash
python insertion.py
```

This script will:
- Create all database tables
- Insert seed data (branches, employees, clients, suppliers, projects, etc.)

### 4. Run the Application

```bash
python hello.py
```

The application will be available at `http://localhost:5000`

## Project Structure

- `/templates` - HTML templates (Jinja2)
- `/static` - CSS, JavaScript, and images
- `/database` - Database schema reference
- `hello.py` - Main Flask application
- `insertion.py` - Database schema creation and seed data insertion
- `requirements.txt` - Python dependencies

## Features

### Entity Management
- **Branches** - Manage company branches (Ramallah, Nablus, Jerusalem)
- **Departments** - Organize company departments
- **Employees** - Employee management with roles and positions
- **Clients** - Client information and contact details
- **Projects** - Project management (Building & Solar projects)
- **Suppliers** - Supplier management and material pricing
- **Materials** - Material catalog and inventory
- **Contracts** - Contract management
- **Phases** - Project phase tracking
- **Schedules** - Project scheduling
- **Sales** - Sales records
- **Purchases** - Purchase orders
- **Payments** - Payment tracking

### Reports & Analytics
- Project Profitability Analysis
- Supplier Impact Analysis
- Cost Driver Materials Analysis
- Employee Utilization Reports
- Price Anomalies Detection
- Branch Performance Comparison

### Project Types
- **Building Projects** - Construction projects
- **Solar Projects** - Solar energy installations

## Database Schema

The system uses 18 main tables:
- Branch, Department, Role, Employee
- Client, Project, Contract, Phase, Schedule
- Supplier, Material, SupplierMaterial, ProjectMaterial
- WorkAssignment, Sales, Purchase, Payment
- Project_Suppliers (junction table)

## Configuration

### Currency
- Default currency: **ILS** (Israeli Shekel)

### Locations
- Branches located in Palestinian cities (Ramallah, Nablus, Jerusalem)

## Notes

- The application uses simplified SQL queries (no CTEs, window functions, or advanced SQL features)
- All database operations use basic SELECT, JOIN, GROUP BY, and aggregation functions
- The system is designed for easy maintenance and understanding

## License

This project is for educational/portfolio purposes.
