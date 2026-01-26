# Abaad Contracting - React Frontend

This is the React frontend for the Abaad Contracting Management System.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Development mode:**
   ```bash
   npm run dev
   ```
   This will start the Vite dev server on `http://localhost:3000` with hot reload.

3. **Build for production:**
   ```bash
   npm run build
   ```
   This will create a production build in `../static/react-build/` that Flask can serve.

## Project Structure

- `src/` - React source code
  - `components/` - Reusable React components (Navbar, Footer)
  - `pages/` - Page components (Home, About, Login, Signup)
  - `contexts/` - React contexts (Theme, Language, Auth)
  - `services/` - API service layer
  - `utils/` - Utility functions and translations

## Features

- ✅ React Router for navigation
- ✅ Theme toggle (light/dark mode)
- ✅ Language toggle (English/Arabic)
- ✅ Authentication context
- ✅ API integration with Flask backend
- ✅ Responsive design with Bootstrap

## API Endpoints

The frontend communicates with Flask backend via:
- `GET /api/stats` - Get dashboard statistics
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/signup` - User registration

## Notes

- The Flask backend must be running on `http://127.0.0.1:5001`
- CORS is enabled on the Flask backend for API requests
- Static assets (images, CSS) are served from `/static/` directory
