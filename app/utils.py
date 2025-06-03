from functools import wraps
from flask import session, jsonify, redirect, url_for
import pyrebase

pb = pyrebase.initialize_app(firebase_config)
db = pb.database()

def validate_user(user_id, token):
    try:
        user = db.child("users").child(user_id).get().val()
        if not user or user.get('is_banned', False):
            return False
        return True
    except:
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        user_id = session['user']['uid']
        user = db.child("users").child(user_id).get().val()
        
        if not user or not user.get('is_admin', False):
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_email(user_id):
    try:
        user = db.child("users").child(user_id).get().val()
        return user.get('email', 'Unknown')
    except:
        return 'Unknown'
