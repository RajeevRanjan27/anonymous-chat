from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
import threading
import time
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Production-ready configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# CORS configuration for production
cors_allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '*')
if cors_allowed_origins != '*':
    cors_allowed_origins = cors_allowed_origins.split(',')

socketio = SocketIO(app, 
                   cors_allowed_origins=cors_allowed_origins,
                   logger=True if os.environ.get('FLASK_ENV') == 'development' else False,
                   engineio_logger=True if os.environ.get('FLASK_ENV') == 'development' else False)

# In-memory storage (will be wiped when server restarts)
chat_rooms = {}
user_sessions = {}

# Room expiry time (30 minutes of inactivity)
ROOM_EXPIRY_MINUTES = 30

class ChatRoom:
    def __init__(self, room_code, creator_id):
        self.code = room_code
        self.creator_id = creator_id
        self.participants = set()
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
    
    def add_participant(self, user_id, username):
        self.participants.add(user_id)
        self.last_activity = datetime.now()
        
    def remove_participant(self, user_id):
        self.participants.discard(user_id)
        self.last_activity = datetime.now()
        
    def add_message(self, user_id, username, message):
        self.messages.append({
            'user_id': user_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
        
    def is_expired(self):
        return datetime.now() - self.last_activity > timedelta(minutes=ROOM_EXPIRY_MINUTES)

def generate_room_id():
    """Generate a unique room ID for URL"""
    while True:
        # Generate a URL-safe room ID (longer for security)
        room_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        if room_id not in chat_rooms:
            return room_id

def cleanup_expired_rooms():
    """Remove expired rooms and their data"""
    expired_rooms = []
    for room_code, room in chat_rooms.items():
        if room.is_expired() or len(room.participants) == 0:
            expired_rooms.append(room_code)
    
    for room_code in expired_rooms:
        if room_code in chat_rooms:
            # Notify remaining participants if any
            socketio.emit('room_closed', {'message': 'Room has been closed due to inactivity'}, room=room_code)
            # Delete all room data
            del chat_rooms[room_code]
            print(f"Room {room_code} deleted due to inactivity")

def start_cleanup_thread():
    """Start background thread to clean up expired rooms"""
    def cleanup_loop():
        while True:
            time.sleep(60)  # Check every minute
            cleanup_expired_rooms()
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat/<room_id>')
def join_via_link(room_id):
    """Direct link access to chat room"""
    if room_id not in chat_rooms:
        return render_template('index.html', error='Room not found or has expired')
    
    room = chat_rooms[room_id]
    if room.is_expired():
        del chat_rooms[room_id]
        return render_template('index.html', error='Room has expired')
    
    return render_template('index.html', room_id=room_id)

@app.route('/create-room', methods=['POST'])
def create_room():
    try:
        data = request.get_json()
        creator_name = data.get('username', 'Anonymous')
        
        # Generate unique user ID and room ID
        user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        room_id = generate_room_id()
        
        # Create new room
        room = ChatRoom(room_id, user_id)
        chat_rooms[room_id] = room
        
        # Store user session
        user_sessions[user_id] = {
            'username': creator_name,
            'room_code': room_id,
            'joined_at': datetime.now()
        }
        
        # Generate shareable link
        host = request.headers.get('Host', 'localhost:5000')
        protocol = 'https' if request.headers.get('X-Forwarded-Proto') == 'https' else 'http'
        share_link = f"{protocol}://{host}/chat/{room_id}"
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'share_link': share_link,
            'user_id': user_id,
            'username': creator_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/join-room', methods=['POST'])
def join_room_http():
    try:
        data = request.get_json()
        room_id = data.get('room_id', '')
        username = data.get('username', 'Anonymous')
        
        if room_id not in chat_rooms:
            return jsonify({'success': False, 'error': 'Room not found'}), 404
            
        room = chat_rooms[room_id]
        if room.is_expired():
            del chat_rooms[room_id]
            return jsonify({'success': False, 'error': 'Room has expired'}), 410
        
        # Generate unique user ID
        user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # Store user session
        user_sessions[user_id] = {
            'username': username,
            'room_code': room_id,
            'joined_at': datetime.now()
        }
        
        return jsonify({
            'success': True,
            'room_id': room_id,
            'user_id': user_id,
            'username': username
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@socketio.on('join')
def on_join(data):
    try:
        user_id = data['user_id']
        room_code = data['room_code']
        
        if user_id not in user_sessions:
            emit('error', {'message': 'Invalid session'})
            return
            
        if room_code not in chat_rooms:
            emit('error', {'message': 'Room not found'})
            return
            
        user_session = user_sessions[user_id]
        username = user_session['username']
        room = chat_rooms[room_code]
        
        # Join the room
        join_room(room_code)
        room.add_participant(user_id, username)
        
        # Send chat history to the user
        emit('chat_history', {'messages': room.messages})
        
        # Notify others about the new participant
        emit('user_joined', {
            'username': username,
            'message': f'{username} joined the chat',
            'participant_count': len(room.participants)
        }, room=room_code)
        
        print(f"User {username} joined room {room_code}")
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('leave')
def on_leave(data):
    try:
        user_id = data['user_id']
        room_code = data['room_code']
        
        if user_id in user_sessions and room_code in chat_rooms:
            user_session = user_sessions[user_id]
            username = user_session['username']
            room = chat_rooms[room_code]
            
            leave_room(room_code)
            room.remove_participant(user_id)
            
            # Clean up user session
            del user_sessions[user_id]
            
            # Notify others about the departure
            emit('user_left', {
                'username': username,
                'message': f'{username} left the chat',
                'participant_count': len(room.participants)
            }, room=room_code)
            
            # Delete room if empty
            if len(room.participants) == 0:
                del chat_rooms[room_code]
                print(f"Room {room_code} deleted - no participants")
                
            print(f"User {username} left room {room_code}")
            
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('send_message')
def handle_message(data):
    try:
        user_id = data['user_id']
        room_code = data['room_code']
        message = data['message']
        
        if user_id not in user_sessions:
            emit('error', {'message': 'Invalid session'})
            return
            
        if room_code not in chat_rooms:
            emit('error', {'message': 'Room not found'})
            return
            
        user_session = user_sessions[user_id]
        username = user_session['username']
        room = chat_rooms[room_code]
        
        # Add message to room
        room.add_message(user_id, username, message)
        
        # Broadcast message to all participants
        emit('new_message', {
            'user_id': user_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=room_code)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('disconnect')
def on_disconnect():
    # Clean up user session on disconnect
    user_id = None
    for uid, session in user_sessions.items():
        if request.sid == session.get('socket_id'):
            user_id = uid
            break
    
    if user_id and user_id in user_sessions:
        room_code = user_sessions[user_id]['room_code']
        username = user_sessions[user_id]['username']
        
        if room_code in chat_rooms:
            room = chat_rooms[room_code]
            room.remove_participant(user_id)
            
            # Notify others about the disconnect
            emit('user_left', {
                'username': username,
                'message': f'{username} disconnected',
                'participant_count': len(room.participants)
            }, room=room_code)
            
            # Delete room if empty
            if len(room.participants) == 0:
                del chat_rooms[room_code]
                print(f"Room {room_code} deleted - no participants")
        
        del user_sessions[user_id]

# Start cleanup thread when app starts
start_cleanup_thread()

if __name__ == '__main__':
    # Get port from environment variable for deployment platforms
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🔗 Anonymous Chat Server Starting...")
    print("Features:")
    print("- Temporary chat rooms with shareable links")
    print("- Automatic data deletion after 30 minutes of inactivity")
    print("- No persistent storage - all data wiped on server restart")
    print("- Anonymous participants")
    print(f"- Running on port {port}")
    
    socketio.run(app, 
                debug=debug_mode, 
                host='0.0.0.0', 
                port=port,
                allow_unsafe_werkzeug=True)
