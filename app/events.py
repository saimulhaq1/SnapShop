from app.extensions import socketio
from flask_socketio import join_room, leave_room
from flask import session

@socketio.on('connect')
def handle_connect(auth):
    """
    Called when a client connects to Socket.IO.
    We read their user_id and role from their session, 
    and put them in appropriate rooms.
    """
    user_id = session.get('user_id')
    role = session.get('role')
    
    if user_id:
        # Join a specific room for direct user notifications
        join_room(f"user_{user_id}")
        print(f"Socket.IO: User {user_id} joined room user_{user_id}")
        
        # If Admin or Staff, join the admin room
        if role in ['ADMIN', 'STAFF']:
            join_room("admin_room")
            print(f"Socket.IO: Admin {user_id} joined admin_room")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        leave_room(f"user_{user_id}")
        if session.get('role') in ['ADMIN', 'STAFF']:
            leave_room("admin_room")
        print(f"Socket.IO: User {user_id} disconnected")
