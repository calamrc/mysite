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
