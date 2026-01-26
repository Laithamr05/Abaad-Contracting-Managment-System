# React Frontend Setup Guide

## Prerequisites

1. **Node.js and npm** installed (v16 or higher)
2. **Flask backend** running on port 5001
3. **Python package**: `flask-cors` (install with `pip install flask-cors`)

## Quick Start

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Development Mode (Recommended for development)

**Terminal 1 - Start Flask backend:**
```bash
python hello.py
```

**Terminal 2 - Start React dev server:**
```bash
cd frontend
npm run dev
```

The React app will be available at `http://localhost:3000` with hot reload.

### 3. Production Build

To build the React app for production:

```bash
cd frontend
npm run build
```

This creates a production build in `static/react-build/` that Flask will automatically serve.

Then start Flask:
```bash
python hello.py
```

The app will be available at `http://127.0.0.1:5001`

## What Changed

### Frontend Structure
- **React app** in `/frontend` directory
- **Vite** as build tool (fast and modern)
- **React Router** for client-side routing
- **Context API** for theme, language, and auth state

### Backend Changes
- **API endpoints** added:
  - `GET /api/stats` - Dashboard statistics
  - `POST /api/login` - User authentication
  - `POST /api/logout` - User logout
  - `POST /api/signup` - User registration
- **CORS enabled** for API requests
- **React build serving** - Flask serves React app when built

### Features Preserved
- ✅ Dark/Light theme toggle
- ✅ English/Arabic language toggle
- ✅ User authentication
- ✅ Responsive design
- ✅ All existing functionality

## File Structure

```
frontend/
├── src/
│   ├── components/     # Navbar, Footer
│   ├── pages/          # Home, About, Login, Signup
│   ├── contexts/       # Theme, Language, Auth contexts
│   ├── services/       # API service layer
│   └── utils/          # Translations
├── package.json
└── vite.config.js
```

## Troubleshooting

1. **CORS errors**: Make sure `flask-cors` is installed
2. **API not working**: Ensure Flask backend is running on port 5001
3. **Build errors**: Run `npm install` again in the frontend directory
4. **Static assets not loading**: Check that images are in `/static/images/` directory

## Next Steps

To migrate more pages to React:
1. Create new page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Create API endpoint in `hello.py` if needed
4. Update navigation links
