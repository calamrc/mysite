# Gift Exchange - Secret Santa App - CSR Architecture

A Secret Santa (gift exchange) application with a Client-Side Rendering (CSR) architecture using Flask (Python) backend and Vue.js frontend with SQLite database.

## Features

- ✅ **Event Creation & Authentication**: Create events with username/PIN authentication
- ✅ **Participant Management**: Join events, manage participants
- ✅ **Drawing System**: Automated Secret Santa assignment with conflict prevention
- ✅ **Real-time Status**: Live updates on drawing progress
- ✅ **Role-based Access**: Organizer vs Participant views
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Client-side Routing**: Vue Router with proper SPA routing
- ✅ **Cross-Origin Support**: Frontend and backend can be deployed separately

## Architecture Overview

This application uses a **Client-Side Rendering (CSR) architecture** where the frontend and backend are completely separated:

### Backend (API Server)
- **Flask** - RESTful API server
- **SQLite** - Database for data persistence
- **Flask-CORS** - Cross-origin resource sharing
- **Session-based authentication** - Secure cookie-based auth

### Frontend (SPA)
- **Vue.js 3** - Client-side rendered Single Page Application
- **Vue Router** - Client-side routing
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API communication

### Production Deployment
- **Frontend**: Static files served by web server (Nginx/Apache)
- **Backend**: Flask API server
- **Separate Domains**: Frontend and backend can be on different servers

## Project Structure

```
mysite/
├── flask_app.py          # Flask API backend (no HTML serving)
├── flask_app.wsgi        # PythonAnywhere WSGI entry point
├── database.py           # SQLite database operations
├── requirements.txt      # Python dependencies
├── nginx.conf            # Example Nginx configuration
│
├── frontend/             # Vue.js SPA source code
│   ├── src/
│   │   ├── main.js       # Vue app entry point
│   │   ├── App.vue       # Main Vue component
│   │   ├── router.js     # Vue Router configuration
│   │   └── views/        # Vue view components
│   ├── public/           # Static assets
│   ├── dist/             # Build output (generated)
│   ├── package.json      # Node.js dependencies
│   ├── vite.config.js    # Vite configuration
│   ├── .env              # Frontend environment config
│   └── .env.example      # Environment template
│
├── static/               # Legacy SSR build output (can be removed)
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
   The backend API will run on http://localhost:5000

2. **Start the Vue.js frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on http://localhost:5173

3. **Access the application**:
   - **Frontend (Vue SPA)**: http://localhost:5173
   - **Backend API**: http://localhost:5000/api

### Production Testing

1. **Build the frontend for production**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Test the built frontend**:
   ```bash
   cd frontend
   npm run preview
   ```
   The built frontend will run on http://localhost:4173

3. **Keep Flask running separately**:
   ```bash
   # In another terminal
   python flask_app.py
   ```

### Production Deployment

For production deployment, deploy the backend and frontend separately:

#### Option 1: Single Server with Nginx
1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Configure Nginx** (see `nginx.conf` for example):
   - Serve `frontend/dist/` as static files
   - Proxy `/api` routes to Flask backend

3. **Deploy Flask API**:
   ```bash
   python flask_app.py
   ```

#### Option 2: Separate Deployments
- **Frontend**: Deploy `frontend/dist/` to any static hosting (Vercel, Netlify, Cloudflare Pages)
- **Backend**: Deploy Flask API to PythonAnywhere, Heroku, or any server
- **Update CORS**: Add your production domain to `FRONTEND_ORIGINS` in `flask_app.py`

## API Endpoints

The Flask backend provides the following REST API endpoints for gift exchange management:

### Events
- `POST /api/events` - Create a new event
- `POST /api/events/join-or-create` - Join/create event with authentication

### Event Management
- `GET /api/events/<event_code>/status` - Get event status and participants
- `POST /api/events/<event_code>/participants` - Register as participant
- `POST /api/events/<event_code>/start-drawing` - Start drawing phase (organizers only)
- `POST /api/events/<event_code>/draw` - Perform Secret Santa draw

### Utility
- `POST /api/simple-draw` - Simple name drawing utility
- `POST /api/logout` - Logout and clear session
- `GET /health` - Health check endpoint

### Authentication Flow

The app uses session-based authentication with cookies. Frontend sends credentials in request body, Flask maintains sessions via secure cookies.

#### Example Event Creation
```json
POST /api/events/join-or-create
{
  "username": "john_doe",
  "pin": "123456"
}
```

#### Example Response
```json
{
  "action": "created",
  "event_code": "ABC123",
  "role": "organizer",
  "message": "Event created! Welcome john_doe",
  "success": true
}
```

## CSR Deployment Options

This application uses Client-Side Rendering, so the backend and frontend must be deployed separately.

### Backend Deployment (PythonAnywhere)

1. **Upload backend files** to your PythonAnywhere account:
   - `flask_app.py`
   - `flask_app.wsgi`
   - `database.py`
   - `requirements.txt`

2. **Create virtual environment**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 mysite-backend
   workon mysite-backend
   pip install -r requirements.txt
   ```

3. **Configure WSGI**:
   ```python
   import sys
   import os

   project_dir = '/home/yourusername/mysite'
   if project_dir not in sys.path:
       sys.path.insert(0, project_dir)

   os.environ['FLASK_ENV'] = 'production'
   # Add your frontend domains here for CORS
   os.environ['FRONTEND_ORIGINS'] = 'https://your-frontend-domain.com,https://www.your-frontend-domain.com'

   from flask_app import app as application
   ```

4. **Test deployment**:
   - Check `https://your-api-domain.pythonanywhere.com/health`
   - API endpoints available at `https://your-api-domain.pythonanywhere.com/api/*`

### Frontend Deployment Options

#### Option A: Static Hosting (Recommended)
Deploy `frontend/dist/` to Vercel, Netlify, or Cloudflare Pages:

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy the `dist/` folder** to your static hosting provider
3. **Configure environment**:
   - Set `VITE_API_BASE_URL=https://your-api-domain.pythonanywhere.com`

#### Option B: Nginx on Same Server
If deploying both on the same server:

1. **Build frontend**: `cd frontend && npm run build`
2. **Configure Nginx** using the provided `nginx.conf`
3. **Frontend available at**: `https://yourdomain.com/`
4. **API available at**: `https://yourdomain.com/api/*`

### CORS Configuration

For cross-origin requests to work, update the `frontend_origins` list in `flask_app.py` or set the `FRONTEND_ORIGINS` environment variable:

```python
frontend_origins = [
    'http://localhost:4173',  # Vite preview
    'http://localhost:3000',  # Alternative frontend port
    'https://your-frontend-domain.com',
    'https://www.your-frontend-domain.com'
]
```

### Testing CSR Deployment

1. **Test API endpoints** directly: `https://your-api-domain.pythonanywhere.com/api/events/join-or-create`
2. **Test frontend** at its deployed URL
3. **Verify CORS** by checking browser network requests
4. **Check session cookies** are being set properly

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
