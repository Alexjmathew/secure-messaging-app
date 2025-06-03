from app import db
from datetime import datetime

# If using SQL database instead of Firebase
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(128), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_banned = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(128), primary_key=True)
    sender_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    encrypted_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_group = db.Column(db.Boolean, default=False)

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
