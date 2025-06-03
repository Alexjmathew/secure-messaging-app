from flask import Blueprint, request, session, jsonify, render_template
from app.encryption import encrypt_message, decrypt_message
from app.utils import validate_user
import pyrebase
from datetime import datetime
from functools import wraps

chat_bp = Blueprint('chat', __name__, template_folder='../templates/chat')

pb = pyrebase.initialize_app(firebase_config)
db = pb.database()

def chat_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route('/')
@chat_required
def index():
    return render_template('index.html')

@chat_bp.route('/send', methods=['POST'])
@chat_required
def send_message():
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    message = data.get('message')
    
    if not all([recipient_id, message]):
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    try:
        # Encrypt message for recipient
        encrypted_msg = encrypt_message(message, recipient_id)
        
        message_data = {
            'sender': session['user']['uid'],
            'recipient': recipient_id,
            'message': encrypted_msg,
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'is_group': False
        }
        
        db.child("messages").push(message_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@chat_bp.route('/get/<recipient_id>', methods=['GET'])
@chat_required
def get_messages(recipient_id):
    try:
        # Get messages between current user and recipient
        messages = db.child("messages").order_by_child("recipient").equal_to(recipient_id).get().val()
        decrypted_messages = []
        
        for msg_id, msg in messages.items():
            if msg['sender'] == session['user']['uid'] or msg['recipient'] == session['user']['uid']:
                decrypted_msg = decrypt_message(msg['message'], msg['sender'])
                decrypted_messages.append({
                    'id': msg_id,
                    'sender': msg['sender'],
                    'message': decrypted_msg,
                    'timestamp': msg['timestamp'],
                    'is_me': msg['sender'] == session['user']['uid']
                })
                
                # Mark as read if recipient is current user
                if msg['recipient'] == session['user']['uid'] and not msg['read']:
                    db.child("messages").child(msg_id).update({'read': True})
        
        return jsonify({'status': 'success', 'messages': decrypted_messages})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@chat_bp.route('/create-group', methods=['POST'])
@chat_required
def create_group():
    data = request.get_json()
    group_name = data.get('group_name')
    members = data.get('members', [])
    
    if not group_name or not members:
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    try:
        # Add current user to members
        if session['user']['uid'] not in members:
            members.append(session['user']['uid'])
        
        group_data = {
            'name': group_name,
            'created_by': session['user']['uid'],
            'members': members,
            'created_at': datetime.now().isoformat()
        }
        
        # Create group
        group_ref = db.child("groups").push(group_data)
        return jsonify({'status': 'success', 'group_id': group_ref['name']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
