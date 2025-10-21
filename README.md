# Task Manager - Flask + Vue.js SPA

A simple task management application built with Flask (Python) backend and Vue.js frontend, using SQLite for data persistence.

## Features

- ✅ Create, read, update, and delete tasks
- ✅ Mark tasks as complete or incomplete
- ✅ Client-side routing with Vue Router
- ✅ Responsive design
- ✅ RESTful API with proper error handling
- ✅ SQLite database for data persistence

## Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Database for data persistence
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Official router for Vue.js
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API calls

## Project Structure

```
mysite/
├── flask_app.py          # Flask backend application
├── database.py           # SQLite database operations
├── requirements.txt      # Python dependencies
├── templates/            # Flask HTML templates
├── static/               # Vue.js build output (generated)
├── frontend/             # Vue.js source code
│   ├── src/
│   │   ├── main.js       # Vue app entry point
│   │   ├── App.vue       # Main Vue component
│   │   ├── router.js     # Vue Router configuration
│   │   └── views/        # Vue view components
│   ├── public/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── vite.config.js    # Vite configuration
├── tasks.db              # SQLite database (generated)
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Return to the root directory**:
   ```bash
   cd ..
   ```

## Running the Application

### Development Mode

1. **Start the Flask backend**:
   ```bash
   python flask_app.py
   ```
   The backend will run on http://localhost:5000

2. **Start the Vue.js frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on http://localhost:5173

3. **Access the application**:
   - Frontend dev server: http://localhost:5173
   - Backend API: http://localhost:5000/api/tasks

### Production Mode

1. **Build the Vue.js frontend**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Start the Flask application**:
   ```bash
   python flask_app.py
   ```

3. **Access the application**:
   The full application will be available at http://localhost:5000

## API Endpoints

The Flask backend provides the following REST API endpoints:

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<id>` - Get a specific task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task

### Task Object Structure

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2025-01-22T10:30:00",
  "updated_at": "2025-01-22T10:30:00"
}
```

## Deployment to PythonAnywhere

This application is configured for deployment on PythonAnywhere. Follow these steps:

### Prerequisites
- PythonAnywhere account with "Hacker" plan or higher (required for custom domains/web apps)
- This project uploaded to PythonAnywhere

### Step 1: Upload Files to PythonAnywhere

1. **Upload the entire project** to your PythonAnywhere account:
   - Use SCP, SFTP, or the PythonAnywhere file manager
   - Upload all files including the `static/` directory with built Vue.js files

2. **Ensure the static files are present**:
   ```
   yourusername.pythonanywhere.com/
   ├── flask_app.wsgi
   ├── flask_app.py
   ├── database.py
   ├── requirements.txt
   ├── static/
   │   ├── index.html
   │   └── assets/
   │       ├── main-*.js
   │       └── index-*.css
   └── (other files...)
   ```

### Step 2: Create Virtual Environment

Create a virtual environment on PythonAnywhere:

```bash
mkvirtualenv --python=/usr/bin/python3.10 mysite
workon mysite
pip install -r requirements.txt
```

### Step 3: Configure Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration** (or **Flask** if available)
4. Set **Python version** to 3.10
5. Enter your virtual environment path: `/home/yourusername/.virtualenvs/mysite`

### Step 4: Configure WSGI

In the **WSGI configuration file** field, enter:

```
/var/www/yourusername_pythonanywhere_com_wsgi.py
```

Update the WSGI file content to:

```python
import sys
import os

# Add project directory to path
project_dir = '/home/yourusername/mysite'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment for production
os.environ['FLASK_ENV'] = 'production'

# Import Flask application
from flask_app import app as application
```

### Step 5: Static Files Configuration

In the Web app configuration:

- **Static URL**: `/static/`
- **Static directory path**: `/home/yourusername/mysite/static`

### Step 6: Reload Web App

Click **Reload** in the PythonAnywhere Web tab to apply changes.

### Step 7: Test Deployment

1. **Check health endpoint**: `https://yourusername.pythonanywhere.com/health`
2. **Visit your app**: `https://yourusername.pythonanywhere.com`
3. **Check logs** using PythonAnywhere's "Server error log" if issues occur

### Troubleshooting Common Issues

#### Blank Page Issues:
1. **Static files not served**: Ensure `/static/` URL points to `/home/yourusername/mysite/static`
2. **Build files missing**: Re-run `npm run build` in `frontend/` and re-upload
3. **Path issues**: Check WSGI file paths are absolute

#### Database Issues:
1. **Permission denied**: SQLite creates files in project directory (should work)
2. **Database not initialized**: Check `/health` endpoint for database errors

#### Static File Serving:
1. **Assets not loading**: Ensure static URL mapping is correct
2. **Cache issues**: Hard refresh browser (Ctrl+F5) or clear browser cache

### Production Optimizations

Your app is now production-ready with:

- ✅ **Environment-based configuration**
- ✅ **Security headers** (HSTS, XSS Protection, Content-Type-Options)
- ✅ **Caching** for static assets (1 year)
- ✅ **Logging** for monitoring
- ✅ **Error handling** for graceful failures
- ✅ **Health check endpoint** (`/health`)

## Development

### Adding New Features

1. **Backend changes**: Modify `flask_app.py` and/or `database.py`
2. **Frontend changes**: Modify files in `frontend/src/`
3. **Database changes**: Update the `init_db()` function in `database.py`

### Database Migrations

If you need to modify the database schema:

1. Update the `init_db()` function in `database.py`
2. Delete the existing `tasks.db` file
3. Restart the Flask application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
