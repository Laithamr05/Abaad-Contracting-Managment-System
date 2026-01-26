# Path Fixes After Reorganization

## Issues Fixed

### 1. Flask App Paths (backend/hello.py)

**Problem**: Flask app was moved to `backend/` but still referenced paths relative to root.

**Fixes Applied**:
- Added `project_root` variable to calculate absolute path to project root
- Updated `static_folder` to use `os.path.join(project_root, 'static', 'react-build')`
- Updated `template_folder` to use `os.path.join(project_root, 'templates')`
- Fixed all `os.path.exists('static/react-build/index.html')` to use absolute paths
- Fixed all `send_from_directory('static/react-build', ...)` to use absolute paths
- Added route `/static/<path:filename>` to serve CSS and images from root static folder

### 2. Media Files Route

**Problem**: `/media/<path:filename>` route used `app.root_path` which was wrong.

**Fix**: Updated to serve from `assets/images/team/` folder using absolute path.

### 3. React Build Output

**Status**: ✅ Already correct - `vite.config.js` outputs to `../static/react-build` which is correct from `frontend/` directory.

### 4. CSS and Static Assets

**Fix**: Added explicit route to serve `/static/*` files from root `static/` folder.

## Current Path Structure

```
Project Root/
├── backend/
│   └── hello.py          # Flask app (uses absolute paths to root)
├── frontend/
│   └── vite.config.js    # Builds to ../static/react-build
├── static/
│   ├── css/              # Served via /static/css/*
│   ├── images/           # Served via /static/images/*
│   └── react-build/      # React build output
├── templates/            # Flask templates (served correctly)
└── assets/               # Source files (not served directly)
```

## Verification

All paths now use absolute paths calculated from `project_root`, ensuring they work regardless of where the Flask app is located.
