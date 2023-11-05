# db.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user


db = SQLAlchemy()


class ChatRoom(db.Model):
    __tablename__ = 'chatroom'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    def __repr__(self):
        return f'<ChatRoom {self.name}>'


class User(UserMixin,db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    company_id = db.Column(db.String(36), db.ForeignKey('company.unique_id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Store a hash of the password
    unique_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))  # Generate a unique UUID


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    

    def __repr__(self):
        return f'<Company {self.name}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Add a foreign key to reference the Company model
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    # Set up relationship to the Company model
    company = db.relationship('Company', backref=db.backref('messages', lazy=True))
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'))

    def __repr__(self):
        return f'<Message {self.username}>'
