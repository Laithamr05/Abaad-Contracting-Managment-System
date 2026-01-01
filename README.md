# Abaad Contracting Company - Management System

A full-stack database management system for a construction/contracting company, following the same flow as the reference airline booking system but with completely different UI, structure, and functionality.

## Technology Stack

- **Database**: MySQL 8.0+
- **Backend**: Node.js + Express
- **Frontend**: React
- **Architecture**: RESTful API with React SPA

## Quick Start

### 1. Database Setup
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 2. Backend Setup
```bash
cd backend
npm install
# Create .env file with DB credentials
npm start
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Project Structure

- `/database` - Schema, seed data, and complex queries
- `/backend` - Express.js REST API
- `/frontend` - React application
- `/backend/routes/reports.js` - Complex SQL query endpoints

## Features

- Full CRUD for all entities (Branches, Departments, Employees, Clients, Projects, Suppliers, Materials)
- Dashboards with key metrics
- 6+ Complex SQL Reports (CTEs, window functions, aggregations)
- Project profitability analysis
- Branch performance tracking
- Employee utilization reports

