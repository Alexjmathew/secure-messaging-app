from flask import Blueprint, request, redirect, url_for, flash, session, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import firebase
import pyrebase
from functools import wraps

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# Firebase config
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-app.firebaseapp.com",
    "projectId": "your-app",
    "storageBucket": "your-app.appspot.com",
    "messagingSenderId": "123456789",
    "appId": "1:123456789:web:abcdef123456",
    "measurementId": "G-ABCDEF123",
    "databaseURL": "https://your-app.firebaseio.com"
}

pb = pyrebase.initialize_app(firebase_config)
auth = pb.auth()
db = pb.database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = {
                'uid': user['localId'],
                'email': email,
                'idToken': user['idToken']
            }
            
            # Check if user is admin
            user_data = db.child("users").child(user['localId']).get().val()
            if user_data and user_data.get('is_admin'):
                session['is_admin'] = True
            
            next_page = request.args.get('next') or url_for('chat.index')
            return redirect(next_page)
        except Exception as e:
            flash('Invalid credentials or account not found')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.register'))
        
        try:
            user = auth.create_user_with_email_and_password(email, password)
            
            # Create user in database
            db.child("users").child(user['localId']).set({
                'email': email,
                'created_at': pyrebase.SERVER_VALUE.TIMESTAMP,
                'is_banned': False,
                'is_admin': False
            })
            
            session['user'] = {
                'uid': user['localId'],
                'email': email,
                'idToken': user['idToken']
            }
            
            return redirect(url_for('chat.index'))
        except Exception as e:
            flash('Registration failed. Email may already be in use.')
            return redirect(url_for('auth.register'))
    return render_template('register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            flash('Password reset link sent to your email')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Error sending reset link. Please try again.')
            return redirect(url_for('auth.forgot_password'))
    return render_template('forgot_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
