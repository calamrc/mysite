import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(task) for task in tasks]

def get_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    return dict(task) if task else None

def create_task(title, description=''):
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO tasks (title, description) VALUES (?, ?)',
        (title, description)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_task(task_id, title=None, description=None, completed=None):
    conn = get_db_connection()
    updates = []
    params = []

    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if completed is not None:
        updates.append('completed = ?')
        params.append(completed)

    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
        params.append(task_id)
        conn.execute(query, params)
        conn.commit()

    conn.close()
    return True

def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return True
