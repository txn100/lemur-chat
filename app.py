from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pusher import Pusher
from dotenv import load_dotenv
from datetime import datetime
from db import db, Message, Company

app = Flask(__name__)
load_dotenv(dotenv_path='.env')
app.secret_key = 'some_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Add your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the db with the Flask app
with app.app_context():
    db.create_all()