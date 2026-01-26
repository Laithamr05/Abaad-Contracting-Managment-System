# Abaad Contracting Management System

A comprehensive management system for Abaad Contracting Company with React frontend and Flask backend.

## 📁 Project Structure

```
Abaad-Contracting-Managment-System-1/
├── backend/                 # Backend Python files
│   ├── hello.py
│   └── insertion.py
│
├── frontend/                # React frontend application
│   ├── public/              # Public assets (served by Vite)
│   │   └── static/
│   │       ├── css/
│   │       └── images/
│   ├── src/                 # React source code
│   │   ├── components/       # Reusable components
│   │   ├── contexts/        # React contexts (Auth, Theme, Language)
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.js
│
├── templates/               # Flask HTML templates (legacy/backend)
│   ├── index.html
│   ├── login.html
│   └── ...
│
├── static/                  # Flask static files (backend)
│   ├── css/
│   └── images/
│
├── assets/                  # Project assets (not part of build)
│   └── images/
│       └── team/           # Team member photos (source files)
│
├── docs/                    # Documentation
│   ├── FRONTEND_QA_SUMMARY.md
│   └── REACT_SETUP.md
│
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md               # This file
```

## 🚀 Getting Started

### Frontend Setup

```bash
cd frontend
npm install
npm run dev      # Development server
npm run build    # Production build
```

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python app.py  # or your main Flask file
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Routing
- **Bootstrap 5** - UI components
- **Axios** - HTTP client

### Backend
- **Python/Flask** - Backend framework
- **SQLite/MySQL** - Database (as configured)

## 📝 Features

- ✅ Multi-language support (English/Arabic)
- ✅ Dark mode theme
- ✅ Responsive design
- ✅ RTL (Right-to-Left) support for Arabic
- ✅ Image optimization with SafeImage component
- ✅ Authentication system
- ✅ Management dashboard

## 📦 Build Output

Frontend builds are output to `static/react-build/` (configured in `vite.config.js`).

## 🔧 Development Notes

- Frontend assets are in `frontend/public/static/`
- Backend static files are in `static/` (root level)
- Team member images source files are in `assets/images/team/`
- Documentation is in `docs/`

## 📄 License

Copyright © 1998–2026 Abaad Contracting. All rights reserved.
