from flask import Flask, session
from flask_session import Session
from flask_firebase import FirebaseAuth
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

app = Flask(__name__)
app.config.from_pyfile('../config.py')

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)

# Initialize Firebase
firebase = FirebaseAuth(app)

# Military-grade encryption setup
backend = default_backend()
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA512(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=backend
)

# Import blueprints after app creation to avoid circular imports
from app.auth import auth_bp
from app.chat import chat_bp
from app.admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.context_processor
def inject_theme():
    return dict(theme=session.get('theme', 'dark'))

def create_app(config_class=None):
    if config_class:
        app.config.from_object(config_class)
    
    # Initialize extensions
    firebase.init_app(app)
    
    return app
