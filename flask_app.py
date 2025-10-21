from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from database import init_db, get_all_tasks, get_task, create_task, update_task, delete_task
import os
import glob

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database on startup
init_db()

@app.route('/')
def index():
    # Try to serve the built Vue app from static directory
    static_index = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(static_index):
        with open(static_index, 'r') as f:
            html_content = f.read()

        # Replace Vite's default paths with Flask static paths
        html_content = html_content.replace('/assets/', '/static/assets/')
        html_content = html_content.replace('"/vite.svg"', '"/static/vite.svg"')

        return render_template_string(html_content)

    # Fallback to development mode template
    return render_template_string("""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Task Manager - Flask + Vue.js</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="http://localhost:5173/src/main.js"></script>
  </body>
</html>""")

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = get_all_tasks()
        return jsonify({'tasks': tasks, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required', 'success': False}), 400

        title = data['title']
        description = data.get('description', '')

        task_id = create_task(title, description)
        task = get_task(task_id)

        return jsonify({'task': task, 'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_single_task(task_id):
    try:
        task = get_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found', 'success': False}), 404

        return jsonify({'task': task, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_single_task(task_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400

        # Check if task exists
        if get_task(task_id) is None:
            return jsonify({'error': 'Task not found', 'success': False}), 404

        title = data.get('title')
        description = data.get('description')
        completed = data.get('completed')

        update_task(task_id, title=title, description=description, completed=completed)
        task = get_task(task_id)

        return jsonify({'task': task, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_single_task(task_id):
    try:
        # Check if task exists
        if get_task(task_id) is None:
            return jsonify({'error': 'Task not found', 'success': False}), 404

        delete_task(task_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
