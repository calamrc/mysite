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

    # Create users table - for authentication
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            avatar_color TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            participant_id INTEGER UNIQUE,
            role TEXT NOT NULL CHECK (role IN ('organizer', 'participant')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
            FOREIGN KEY (participant_id) REFERENCES participants (id) ON DELETE CASCADE,
            UNIQUE(username, event_id COLLATE NOCASE),
            UNIQUE(display_name, event_id COLLATE NOCASE)
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

# ===== USER PERSONALIZATION FUNCTIONS =====

# Pre-defined lists for generating random names and colors
DISPLAY_NAME_WORDS = [
    'Phoenix', 'Blizzard', 'Thunder', 'Whisper', 'Eclipse', 'Mystic', 'Tempest',
    'Sapphire', 'Crimson', 'Aurora', 'Storm', 'Jester', 'Nova', 'Specter', 'Radiant',
    'Vortex', 'Harmony', 'Falcon', 'Trinity', 'Orion', 'Lunar', 'Zenith', 'Cascade',
    'Brave', 'Courage', 'Justice', 'Liberty', 'Spirit', 'Wisdom', 'Passion', 'Dream',
    'Cosmic', 'Galactic', 'Eternal', 'Infinite', 'Majestic', 'Noble', 'Royal', 'Flame',
    'Frost', 'Shadow', 'Light', 'Star', 'Moon', 'Sun', 'Wind', 'Earth', 'Fire', 'Water'
]

AVATAR_COLORS = [
    '#ff6b6b', '#feca57', '#48dbfb', '#0abde3', '#ff9ff3', '#f368e0', '#00d2d3', '#54a0ff',
    '#5f27cd', '#00d2d3', '#ff9f43', '#ee5a24', '#0abde3', '#2e86de', '#341f97', '#5352ed',
    '#ff6b9d', '#e056fd', '#3483fa', '#26de81', '#78e08f', '#fad390', '#6c5ce7', '#a29bfe',
    '#fd79a8', '#fdcb6e', '#e17055', '#d63031', '#00b894', '#00cec9', '#a29bfe', '#6c5ce7'
]

def generate_display_name(event_id):
    """Generate a unique display name for an event"""
    conn = get_db_connection()
    taken_names = set()

    # Get all existing display names for this event
    users = conn.execute(
        'SELECT display_name FROM users WHERE event_id = ?',
        (event_id,)
    ).fetchall()
    conn.close()

    taken_names = {user['display_name'] for user in users}

    # Try to find an unused name
    available_names = [name for name in DISPLAY_NAME_WORDS if name not in taken_names]

    if not available_names:
        # If all names are taken, append a number (fallback)
        base_names = [name for name in DISPLAY_NAME_WORDS if name not in taken_names]
        for name in base_names:
            counter = 1
            while True:
                candidate = f"{name}{counter}"
                if candidate not in taken_names:
                    return candidate
                counter += 1
        # Ultimate fallback
        return f"User{len(taken_names) + 1}"

    return random.choice(available_names)

def generate_avatar_color():
    """Generate a random avatar color"""
    return random.choice(AVATAR_COLORS)

def update_user_profile(user_id, display_name=None, avatar_color=None):
    """Update user display name and/or avatar color"""
    conn = get_db_connection()
    try:
        # Build update query dynamically
        updates = []
        params = []

        if display_name is not None:
            updates.append('display_name = ?')
            params.append(display_name)

        if avatar_color is not None:
            updates.append('avatar_color = ?')
            params.append(avatar_color)

        if not updates:
            return False  # Nothing to update

        params.append(user_id)
        query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'

        conn.execute(query, params)
        conn.commit()
        return True
    finally:
        conn.close()

# ===== USER MANAGEMENT FUNCTIONS =====

def get_user_by_credentials(username, pin, event_id):
    """Get user by username + PIN + event_id (case insensitive username)"""
    conn = get_db_connection()
    user = conn.execute('''
        SELECT u.*, p.name as participant_name
        FROM users u
        LEFT JOIN participants p ON u.participant_id = p.id
        WHERE LOWER(u.username) = LOWER(?) AND u.pin_hash = ? AND u.event_id = ?
    ''', (username, hash_pin(pin), event_id)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, pin, event_id, role, participant_id=None, display_name=None, avatar_color=None):
    """Create a new user account with optional personalized name/avatar"""
    if display_name is None:
        display_name = generate_display_name(event_id)

    if avatar_color is None:
        avatar_color = generate_avatar_color()

    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            INSERT INTO users (username, pin_hash, display_name, avatar_color, event_id, role, participant_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, hash_pin(pin), display_name, avatar_color, event_id, role, participant_id))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id, display_name, avatar_color
    except sqlite3.IntegrityError:
        return None, None, None  # Username or display_name already exists for this event
    finally:
        conn.close()

def get_user(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute('''
        SELECT u.*, p.name as participant_name
        FROM users u
        LEFT JOIN participants p ON u.participant_id = p.id
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_users_for_event(event_id):
    """Get all users for an event"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT u.*, p.name as participant_name
        FROM users u
        LEFT JOIN participants p ON u.participant_id = p.id
        WHERE u.event_id = ?
        ORDER BY u.created_at
    ''', (event_id,)).fetchall()
    conn.close()
    return [dict(user) for user in users]
