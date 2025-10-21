#!/usr/bin/env python3
"""
Simple test script to run the Flask app
"""
from flask_app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
