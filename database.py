import sqlite3
from datetime import datetime
import hashlib
import random
import string

def get_db_connection():
    conn = sqlite3.connect('gift_exchange.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    # Create events table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_code TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            phase TEXT NOT NULL CHECK (phase IN ('registration', 'drawing')) DEFAULT 'registration',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create participants table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            has_drawn BOOLEAN DEFAULT FALSE,
            giftee_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
            FOREIGN KEY (giftee_id) REFERENCES participants (id),
            UNIQUE(event_id, name COLLATE NOCASE)
        )
    ''')

    # Create indexes for performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_events_code ON events(event_code)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_event_id ON participants(event_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_name ON participants(event_id, name COLLATE NOCASE)')

    conn.commit()
    conn.close()

def hash_pin(pin):
    """Hash a PIN using SHA-256"""
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin, pin_hash):
    """Verify a PIN against its hash"""
    return hash_pin(pin) == pin_hash

def generate_event_code(length=6):
    """Generate a unique event code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not get_event_by_code(code):
            return code

def get_all_events():
    """Get all events for admin purposes"""
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(event) for event in events]

def get_event(event_id):
    """Get event by ID"""
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    return dict(event) if event else None

def get_event_by_code(event_code):
    """Get event by code"""
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE event_code = ?', (event_code.upper(),)).fetchone()
    conn.close()
    return dict(event) if event else None

def create_event(pin):
    """Create a new event with unique code and hashed PIN"""
    conn = get_db_connection()
    event_code = generate_event_code()
    pin_hash = hash_pin(pin)

    cursor = conn.execute(
        'INSERT INTO events (event_code, pin_hash, phase) VALUES (?, ?, ?)',
        (event_code, pin_hash, 'registration')
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id, event_code

def update_event_phase(event_id, phase):
    """Update event phase"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE events SET phase = ? WHERE id = ?',
        (phase, event_id)
    )
    conn.commit()
    conn.close()
    return True

def get_event_participants(event_id):
    """Get all participants for an event"""
    conn = get_db_connection()
    participants = conn.execute('''
        SELECT
            p.*,
            g.name as giftee_name
        FROM participants p
        LEFT JOIN participants g ON p.giftee_id = g.id
        WHERE p.event_id = ?
        ORDER BY p.joined_at
    ''', (event_id,)).fetchall()
    conn.close()
    return [dict(participant) for participant in participants]

def get_participant(participant_id):
    """Get participant by ID"""
    conn = get_db_connection()
    participant = conn.execute('''
        SELECT
            p.*,
            g.name as giftee_name
        FROM participants p
        LEFT JOIN participants g ON p.giftee_id = g.id
        WHERE p.id = ?
    ''', (participant_id,)).fetchone()
    conn.close()
    return dict(participant) if participant else None

def add_participant(event_id, name):
    """Add a participant to an event"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'INSERT INTO participants (event_id, name) VALUES (?, ?)',
            (event_id, name.strip())
        )
        participant_id = cursor.lastrowid
        conn.commit()
        return participant_id
    except sqlite3.IntegrityError:
        return None  # Name already exists
    finally:
        conn.close()

def get_remaining_participants(event_id):
    """Get participants who haven't drawn yet"""
    conn = get_db_connection()
    participants = conn.execute(
        'SELECT id, name FROM participants WHERE event_id = ? AND has_drawn = FALSE',
        (event_id,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in participants]

def assign_giftee(participant_id, giftee_id):
    """Assign a giftee to a participant"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE participants SET giftee_id = ?, has_drawn = TRUE WHERE id = ?',
        (giftee_id, participant_id)
    )
    conn.commit()
    conn.close()
    return True

def is_event_complete(event_id):
    """Check if all participants have drawn"""
    conn = get_db_connection()
    result = conn.execute(
        'SELECT COUNT(*) as total, SUM(has_drawn) as drawn FROM participants WHERE event_id = ?',
        (event_id,)
    ).fetchone()
    conn.close()

    if result['total'] == 0:
        return False
    return result['drawn'] == result['total']

def draw_name(names, exclude_name=None, remove_drawn=True):
    """
    Draw a random name from a list of names.
    Used by the simple draw API (FR-6) and internal drawing logic.

    Args:
        names: List of name dictionaries with 'id' and 'name' keys
        exclude_name: Name to exclude from drawing (case-insensitive)
        remove_drawn: Whether to remove the drawn name from remaining list

    Returns:
        dict: {
            'success': bool,
            'drawn_name': str or None,
            'drawn_id': int or None,
            'remaining_names': list,
            'error': str or None
        }
    """
    if not names:
        return {
            'success': False,
            'drawn_name': None,
            'drawn_id': None,
            'remaining_names': [],
            'error': 'No names available to draw from'
        }

    # Filter out excluded name (case-insensitive)
    available_names = []
    for name_dict in names:
        if exclude_name and name_dict['name'].lower() == exclude_name.lower():
            continue
        available_names.append(name_dict)

    if not available_names:
        # Only the excluded name was available
        if exclude_name:
            return {
                'success': False,
                'drawn_name': None,
                'drawn_id': None,
                'remaining_names': names,
                'error': f'Only {exclude_name} remains and cannot draw self'
            }
        else:
            return {
                'success': False,
                'drawn_name': None,
                'drawn_id': None,
                'remaining_names': names,
                'error': 'No valid names to draw from'
            }

    # Randomly select from available names
    selected = random.choice(available_names)

    # Remove drawn name if requested
    remaining = [n for n in names if n['id'] != selected['id']] if remove_drawn else names

    return {
        'success': True,
        'drawn_name': selected['name'],
        'drawn_id': selected['id'],
        'remaining_names': remaining,
        'error': None
    }

def perform_draw(event_id, participant_id, participant_name):
    """
    Perform a draw for a participant in an event.
    Handles the full drawing logic including retries for conflicts.

    Returns:
        dict: Result with success status and assignment info
    """
    conn = get_db_connection()

    try:
        # Get event info
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        if not event:
            conn.close()
            return {'success': False, 'error': 'Event not found'}

        if event['phase'] != 'drawing':
            conn.close()
            return {'success': False, 'error': 'Event is not in drawing phase'}

        # Check if participant exists and hasn't drawn yet
        participant = conn.execute(
            'SELECT * FROM participants WHERE id = ? AND event_id = ?',
            (participant_id, event_id)
        ).fetchone()

        if not participant:
            conn.close()
            return {'success': False, 'error': 'Participant not found in this event'}

        if participant['has_drawn']:
            conn.close()
            return {'success': False, 'error': 'Participant has already drawn'}

        # Get all participants (including those who've drawn)
        all_participants = conn.execute(
            'SELECT id, name FROM participants WHERE event_id = ?',
            (event_id,)
        ).fetchall()

        participants_list = [{'id': p['id'], 'name': p['name']} for p in all_participants]

        # Get participants who haven't been assigned yet or are available
        assigned_gifteess = conn.execute(
            'SELECT giftee_id FROM participants WHERE event_id = ? AND giftee_id IS NOT NULL',
            (event_id,)
        ).fetchall()

        assigned_ids = [a['giftee_id'] for a in assigned_gifteess]
        available_gifteess = [p for p in participants_list if p['id'] not in assigned_ids]

        # Try to draw (with max 5 attempts to avoid infinite loops)
        max_attempts = 5
        for attempt in range(max_attempts):
            result = draw_name(available_gifteess, exclude_name=participant_name, remove_drawn=False)

            if result['success']:
                # Check if this assignment would create a cycle
                if not _would_create_invalid_assignment(conn, event_id, participant_id, result['drawn_id']):
                    # Valid assignment - update database
                    conn.execute(
                        'UPDATE participants SET giftee_id = ?, has_drawn = TRUE WHERE id = ?',
                        (result['drawn_id'], participant_id)
                    )
                    conn.commit()

                    # Get the assigned participant's full info
                    giftee = conn.execute(
                        'SELECT * FROM participants WHERE id = ?',
                        (result['drawn_id'],)
                    ).fetchone()

                    conn.close()
                    return {
                        'success': True,
                        'giftee_name': result['drawn_name'],
                        'giftee_id': result['drawn_id'],
                        'message': f'Successfully drew {result["drawn_name"]}'
                    }
                else:
                    # Try again - this assignment would be invalid
                    continue
            else:
                # No valid draw possible
                conn.close()
                return {
                    'success': False,
                    'error': result['error'] or 'Unable to perform draw'
                }

        # After max attempts, give up
        conn.close()
        return {
            'success': False,
            'error': f'Unable to find valid assignment after {max_attempts} attempts. Try again later.'
        }

    except Exception as e:
        conn.close()
        return {'success': False, 'error': f'Database error: {str(e)}'}

def _would_create_invalid_assignment(conn, event_id, drawer_id, giftee_id):
    """
    Check if assigning giftee_id to drawer_id would create an invalid state.
    For now, mainly checks for self-assignment (though this should be prevented elsewhere).
    Can be extended for more complex validation rules.
    """
    # Basic self-assignment check
    if drawer_id == giftee_id:
        return True

    # Could add more complex validation here in the future
    # e.g., prevent cycles, enforce rules, etc.
    return False
