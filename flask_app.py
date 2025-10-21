from flask import Flask, request, jsonify, render_template_string, make_response, session
from flask_cors import CORS
from database import (
    init_db, get_event_by_code, create_event, add_participant,
    get_event_participants, update_event_phase, perform_draw,
    draw_name, get_remaining_participants, is_event_complete,
    verify_pin, get_participant, get_db_connection,
    get_user_by_credentials, create_user, get_user
)
import os
import glob
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gift-exchange-dev-secret-key-change-in-production')

# Environment-based configuration
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'

# CORS configuration - single server approach
# Frontend and backend served from same domain, so relaxed CORS
if DEBUG:
    # Development: Allow same-origin (Flask + Vue on same domain)
    CORS(app, origins=['http://localhost:5000'], supports_credentials=True)
else:
    # Production: Allow same-origin and common frontend patterns
    CORS(app, supports_credentials=True)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Cache static assets for a year
    if request.path.startswith('/static/assets/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'

    return response

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    if not DEBUG:
        raise  # Fail hard in production

def get_current_user():
    """Get current user from session"""
    return session.get('user', {})

def set_current_user(event_code, role, user_id, participant_name=None):
    """Set current user in session - now requires user_id for persistence"""
    session['user'] = {
        'event_code': event_code,
        'role': role,  # 'organizer' or 'participant'
        'user_id': user_id,  # Always required now
        'participant_name': participant_name  # Display name
    }
    session.permanent = True

def clear_current_user():
    """Clear current user session"""
    session.pop('user', None)

# Frontend Routes - Single Server Approach
@app.route('/', methods=['GET'])
def serve_vue_app():
    """Serve the Vue.js Single Page Application"""
    try:
        # Try to serve the built Vue app from static directory
        static_index = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(static_index):
            with open(static_index, 'r') as f:
                html_content = f.read()
            return make_response(html_content, 200)
        else:
            # Fallback for development - API-only response
            return jsonify({
                'message': 'Frontend not built. Run: cd frontend && npm run build',
                'build_command': 'cd frontend && npm run build',
                'access_api': 'Visit /api/* endpoints for API access'
            }), 404
    except Exception as e:
        logger.error(f"Error serving Vue app: {e}")
        return jsonify({'error': 'Failed to load application', 'details': str(e)}), 500

@app.route('/<path:path>', methods=['GET'])
def serve_vue_app_routes(path):
    """Catch-all route for Vue Router - serves the Vue app for all non-API routes"""
    # Don't intercept API routes
    if path.startswith('api/') or path == 'health':
        # This shouldn't happen if API routes are defined first, but safety check
        return jsonify({'error': 'Not found'}), 404

    # Serve the Vue app for any other route (SPA routing)
    return serve_vue_app()

# API Routes - Gift Exchange

@app.route('/api/events', methods=['POST'])
def create_new_event():
    """Create a new event (FR-1)"""
    try:
        data = request.get_json()
        if not data or 'pin' not in data:
            return jsonify({'error': 'PIN is required', 'success': False}), 400

        pin = data['pin']
        if not isinstance(pin, str) or len(pin) < 4:
            return jsonify({'error': 'PIN must be at least 4 characters', 'success': False}), 400

        event_id, event_code = create_event(pin)

        # Automatically authenticate the creator as organizer
        set_current_user(event_code, 'organizer')

        return jsonify({
            'event_code': event_code,
            'message': 'Event created successfully',
            'success': True
        }), 201

    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return jsonify({'error': 'Failed to create event', 'success': False}), 500

@app.route('/api/events/join-or-create', methods=['POST'])
def join_or_create_event():
    """Unified API for joining existing event or creating new event with username + PIN authentication"""
    try:
        data = request.get_json()

        required_fields = ['username', 'pin']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Username and PIN are required', 'success': False}), 400

        username = data['username'].strip()
        pin = data['pin']

        if not username:
            return jsonify({'error': 'Username cannot be empty', 'success': False}), 400

        if not isinstance(pin, str) or len(pin) < 4:
            return jsonify({'error': 'PIN must be at least 4 characters', 'success': False}), 400

        event_code = data.get('event_code', '').strip().upper()

        if not event_code:
            # CREATE NEW EVENT
            event_id, event_code = create_event(pin)

            # Create user account
            user_id = create_user(username, pin, event_id, 'organizer')
            if user_id is None:
                # Username already exists (shouldn't happen for new event, but just in case)
                return jsonify({'error': 'Username already taken', 'success': False}), 409

            # Create participant record for organizer
            participant_id = add_participant(event_id, username)
            if participant_id:
                # Link participant to user account (organizer is always a participant)
                conn = get_db_connection()
                try:
                    conn.execute('UPDATE users SET participant_id = ? WHERE id = ?', (participant_id, user_id))
                    conn.commit()
                finally:
                    conn.close()

            # Set session
            set_current_user(event_code, 'organizer', user_id, username)

            return jsonify({
                'action': 'created',
                'event_code': event_code,
                'role': 'organizer',
                'message': f'Event created! Welcome {username}',
                'success': True
            }), 201

        # JOIN EXISTING EVENT
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Event not found', 'success': False}), 404

        # Check if username + PIN combo exists for this event
        existing_user = get_user_by_credentials(username, pin, event['id'])

        if existing_user:
            # Existing user - authenticate them
            user_id = existing_user['id']
            role = existing_user['role']
            participant_name = existing_user['participant_name']

            # Set session
            set_current_user(event_code, role, user_id, participant_name)

            role_message = 'organizer' if role == 'organizer' else 'participant'
            return jsonify({
                'action': 'authenticated',
                'event_code': event_code,
                'role': role,
                'phase': event['phase'],
                'message': f'Welcome back {username}!',
                'success': True
            })

        # Username + PIN combo not found - create new participant account
        # First verify PIN is correct for the event
        if not verify_pin(pin, event['pin_hash']):
            return jsonify({'error': 'Invalid PIN for this event', 'success': False}), 401

        # PIN correct, but user account doesn't exist - create new participant
        participants = get_event_participants(event['id'])

        if len(participants) == 0:
            # First participant becomes organizer
            role = 'organizer'
            message_part = 'as the organizer'
        else:
            # Additional participants
            role = 'participant'
            message_part = 'as a participant'

        # Create participant record
        participant_id = add_participant(event['id'], username)
        if participant_id is None:
            return jsonify({'error': 'Name already taken', 'success': False}), 409

        # Create user account
        user_id = create_user(username, pin, event['id'], role, participant_id)
        if user_id is None:
            return jsonify({'error': 'Username already taken for this event', 'success': False}), 409

        # Set session
        set_current_user(event_code, role, user_id, username)

        return jsonify({
            'action': 'joined',
            'event_code': event_code,
            'role': role,
            'phase': event['phase'],
            'message': f'Successfully joined {message_part}!',
            'success': True
        })

    except Exception as e:
        logger.error(f"Error in join-or-create: {e}")
        return jsonify({'error': 'Failed to process request', 'success': False}), 500

@app.route('/api/events/<event_code>/status', methods=['GET'])
def get_event_status(event_code):
    """Get event status (FR-7)"""
    try:
        event_code = event_code.upper()

        # Get current user from session
        current_user = get_current_user()
        if not current_user or current_user.get('event_code') != event_code:
            return jsonify({'error': 'Not authenticated for this event', 'success': False}), 401

        # Get event
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Event not found', 'success': False}), 404

        # Get participants
        participants = get_event_participants(event['id'])

        # Process participant data based on role and event phase
        user_role = current_user.get('role')
        is_complete = is_event_complete(event['id'])

        # Filter participant list based on role
        if user_role == 'participant':
            # Participants only see their own status and basic participant counts
            participant_statuses = []
            current_participant_found = False
            drawn_count = sum(1 for p in participants if p['has_drawn'])

            for p in participants:
                if p['id'] == current_user.get('user_id'):
                    participant_statuses.append({
                        'name': p['name'],
                        'status': 'Drawn' if p['has_drawn'] else 'Joined',
                        'giftee_name': p['giftee_name'] if p['has_drawn'] else None
                    })
                    current_participant_found = True
                else:
                    # Anonymous count only
                    participant_statuses.append({
                        'name': f'Participant {len([s for s in participant_statuses if not s.get("is_current_user")])}',
                        'status': 'Drawn' if p['has_drawn'] else 'Joined',
                        'is_anonymous': True
                    })

            participant_list = participant_statuses

        else:  # organizer
            # Organizers see full participant list
            participant_list = [{
                'name': p['name'],
                'status': 'Drawn' if p['has_drawn'] else 'Joined',
                'giftee_name': p['giftee_name'] if p['has_drawn'] else None
            } for p in participants]

        joined_count = len([p for p in participants if not p['has_drawn']])
        drawn_count = len([p for p in participants if p['has_drawn']])

        # Check if organizer is also a participant
        is_participant = False
        if user_role == 'organizer':
            participant_id = current_user.get('participant_id')
            participant_name = current_user.get('participant_name')
            if participant_id or (participant_name and any(p['name'] == participant_name for p in participants)):
                is_participant = True

        # Get participant name for logged-in users
        participant_name = None
        if user_id := current_user.get('user_id'):
            user_info = get_user(user_id)
            if user_info and user_info['participant_name']:
                participant_name = user_info['participant_name']

        return jsonify({
            'event_code': event_code,
            'phase': event['phase'],
            'is_complete': is_complete,
            'joined_count': len(participants),
            'drawn_count': drawn_count,
            'participants': participant_list,
            'user_role': user_role,
            'participant_name': participant_name,
            'is_participant': is_participant,
            'success': True
        })

    except Exception as e:
        logger.error(f"Error getting event status: {e}")
        return jsonify({'error': 'Failed to get event status', 'success': False}), 500

@app.route('/api/events/<event_code>/participants', methods=['POST'])
def register_participant(event_code):
    """Register a participant (FR-3)"""
    try:
        event_code = event_code.upper()
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required', 'success': False}), 400

        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Name cannot be empty', 'success': False}), 400

        # Get event
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Event not found', 'success': False}), 404

        if event['phase'] != 'registration':
            return jsonify({'error': 'Event is no longer accepting registrations', 'success': False}), 400

        # Add participant
        participant_id = add_participant(event['id'], name)
        if participant_id is None:
            return jsonify({'error': 'Name already taken', 'success': False}), 409

        # Update session for all cases - handle both regular participants and organizers joining as participants
        current_user = get_current_user()
        user_role = current_user.get('role', 'participant')

        # For organizers who join as participants, keep their organizer role but track participant ID
        if current_user.get('event_code') == event_code and user_role == 'organizer':
            # Organizer joining as participant - update session with participant info
            # but maintain organizer role
            session['user'].update({
                'participant_id': participant_id,
                'participant_name': name
            })
            session.permanent = True
        elif user_role == 'participant':
            # Regular participant registration
            set_current_user(event_code, 'participant', user_id=participant_id, name=name)

        return jsonify({
            'message': f'Successfully joined as {name}',
            'participant_id': participant_id,
            'success': True
        }), 201

    except Exception as e:
        logger.error(f"Error registering participant: {e}")
        return jsonify({'error': 'Failed to register participant', 'success': False}), 500

@app.route('/api/events/<event_code>/start-drawing', methods=['POST'])
def start_drawing_phase(event_code):
    """Start drawing phase (FR-4)"""
    try:
        event_code = event_code.upper()

        # Check authentication
        current_user = get_current_user()
        if not current_user or current_user.get('event_code') != event_code or current_user.get('role') != 'organizer':
            return jsonify({'error': 'Only event organizers can start the drawing phase', 'success': False}), 403

        # Get event
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Event not found', 'success': False}), 404

        if event['phase'] != 'registration':
            return jsonify({'error': f'Event is already in {event["phase"]} phase', 'success': False}), 400

        # Check minimum participants
        participants = get_event_participants(event['id'])
        if len(participants) < 2:
            return jsonify({'error': 'At least 2 participants required to start drawing', 'success': False}), 400

        # Update phase
        update_event_phase(event['id'], 'drawing')

        return jsonify({
            'message': 'Drawing phase started successfully',
            'phase': 'drawing',
            'participant_count': len(participants),
            'success': True
        })

    except Exception as e:
        logger.error(f"Error starting drawing phase: {e}")
        return jsonify({'error': 'Failed to start drawing phase', 'success': False}), 500

@app.route('/api/events/<event_code>/draw', methods=['POST'])
def perform_user_draw(event_code):
    """Perform a draw for the current participant (FR-5)"""
    try:
        event_code = event_code.upper()

        # Check authentication
        current_user = get_current_user()
        if not current_user or current_user.get('event_code') != event_code or current_user.get('role') != 'participant':
            return jsonify({'error': 'Participant authentication required', 'success': False}), 401

        participant_id = current_user.get('user_id')
        if not participant_id:
            return jsonify({'error': 'Participant not registered', 'success': False}), 400

        # Get event
        event = get_event_by_code(event_code)
        if not event:
            return jsonify({'error': 'Event not found', 'success': False}), 404

        participant_name = current_user.get('name', 'Unknown')

        # Perform the draw
        result = perform_draw(event['id'], participant_id, participant_name)

        if result['success']:
            # Update session to reflect drawn state
            set_current_user(event_code, 'participant', user_id=participant_id, name=participant_name)

            # Check if event is now complete
            is_complete = is_event_complete(event['id'])

            return jsonify({
                'giftee_name': result['giftee_name'],
                'message': result['message'],
                'is_complete': is_complete,
                'success': True
            })
        else:
            return jsonify({
                'error': result['error'],
                'success': False
            }), 400

    except Exception as e:
        logger.error(f"Error performing draw: {e}")
        return jsonify({'error': 'Failed to perform draw', 'success': False}), 500

@app.route('/api/simple-draw', methods=['POST'])
def simple_draw():
    """Simple draw utility (FR-6)"""
    try:
        data = request.get_json()

        if not data or 'names' not in data:
            return jsonify({'error': 'Names list is required', 'success': False}), 400

        names = data['names']
        if not isinstance(names, list) or len(names) < 2:
            return jsonify({'error': 'At least 2 names required', 'success': False}), 400

        # Validate names format
        name_dicts = []
        for i, name_item in enumerate(names):
            if isinstance(name_item, str):
                name_dicts.append({'id': i, 'name': name_item})
            elif isinstance(name_item, dict) and 'name' in name_item:
                name_dicts.append({'id': name_item.get('id', i), 'name': name_item['name']})
            else:
                return jsonify({'error': f'Invalid name format at index {i}', 'success': False}), 400

        exclude_name = data.get('exclude_name')
        remove_drawn = data.get('remove_drawn', True)

        result = draw_name(name_dicts, exclude_name=exclude_name, remove_drawn=remove_drawn)

        if result['success']:
            return jsonify({
                'drawn_name': result['drawn_name'],
                'remaining_names': [n['name'] for n in result['remaining_names']],
                'success': True
            })
        else:
            return jsonify({
                'error': result['error'],
                'success': False
            }), 400

    except Exception as e:
        logger.error(f"Error in simple draw: {e}")
        return jsonify({'error': 'Failed to perform simple draw', 'success': False}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout and clear session (FR-9)"""
    try:
        clear_current_user()
        return jsonify({
            'message': 'Logged out successfully',
            'success': True
        })
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify({'error': 'Failed to logout', 'success': False}), 500

# Health check endpoint for production monitoring
@app.route('/health')
def health_check():
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Error handlers for production
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    if DEBUG:
        return jsonify({'error': str(error), 'success': False}), 500
    return jsonify({'error': 'Internal server error', 'success': False}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found', 'success': False}), 404

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
