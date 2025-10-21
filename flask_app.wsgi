#!/usr/bin/env python
"""
WSGI entry point for PythonAnywhere deployment
"""
import sys
import os

# Add the current directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variable to indicate production
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask application
from flask_app import app

# Apply application to the WSGI interface
application = app
