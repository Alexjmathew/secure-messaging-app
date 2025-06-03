from flask import Blueprint, request, session, jsonify, render_template
from app.utils import admin_required
import pyrebase
from datetime import datetime

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

pb = pyrebase.initialize_app(firebase_config)
db = pb.database()

@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('dashboard.html')

@admin_bp.route('/users')
@admin_required
def manage_users():
    try:
        users = db.child("users").get().val()
        return render_template('users.html', users=users)
    except Exception as e:
        return render_template('error.html', error=str(e))

@admin_bp.route('/ban-user', methods=['POST'])
@admin_required
def ban_user():
    user_id = request.json.get('user_id')
    reason = request.json.get('reason', 'No reason provided')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'}), 400
    
    try:
        db.child("users").child(user_id).update({
            'is_banned': True,
            'ban_reason': reason,
            'banned_at': datetime.now().isoformat(),
            'banned_by': session['user']['uid']
        })
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/view-messages')
@admin_required
def view_messages():
    try:
        messages = db.child("messages").order_by_child("timestamp").limit_to_last(100).get().val()
        return render_template('messages.html', messages=messages)
    except Exception as e:
        return render_template('error.html', error=str(e))

@admin_bp.route('/promote-user', methods=['POST'])
@admin_required
def promote_user():
    user_id = request.json.get('user_id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'}), 400
    
    try:
        db.child("users").child(user_id).update({'is_admin': True})
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
