from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pusher import Pusher
from dotenv import load_dotenv
from datetime import datetime
from db import db, Message

app = Flask(__name__)
load_dotenv(dotenv_path='.env')
app.secret_key = 'some_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Add your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the db with the Flask app
pusher = Pusher(
    app_id='1699312',
    key='4f6a30582d3fee132dc9',
    secret='5a9abd70a7af2505b828',
    cluster='eu',
    ssl=True
)

class TerminalChat():
    users = {
        "xxxxx": "xxxxxx",
        "xxxxxx": "xxxxxx",
      
    }
    chatrooms = ["Dingleberry and PacificTrout", "Sex Dungeon"]

    @staticmethod
    def login(username, password):
        if TerminalChat.users.get(username) == password:
            session['user'] = username
            return True
        return False

    @staticmethod
    def select_chatroom(chatroom):
        if chatroom in TerminalChat.chatrooms:
            session['chatroom'] = chatroom
            return True
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if TerminalChat.login(username, password):
            return redirect(url_for('select_chatroom'))
    return render_template('login.html')

@app.route('/chatroom', methods=['GET', 'POST'])
def select_chatroom():
    if 'user' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        chatroom = request.form['chatroom']
        if TerminalChat.select_chatroom(chatroom):
            pusher.trigger('chatroom', 'user_joined', {'message': f"{session['user']} joined the chat"})
            return redirect(url_for('chat'))
    return render_template('chatroom.html', chatrooms=TerminalChat.chatrooms)

@app.route('/chat')
def chat():
    if 'user' not in session or 'chatroom' not in session:
        return redirect(url_for('index'))
    
    # Fetch the last N messages from the database
    # Adjust the number of messages as needed
    num_messages_to_load = 1000  # For example, load the last 50 messages
    messages = Message.query \
        .filter_by(room=session['chatroom']) \
        .order_by(Message.timestamp.asc()) \
        .limit(num_messages_to_load) \
        .all()
    
    # Format messages for display
    formatted_messages = [
        {
            'user': message.username,
            'message': message.message,
            'timestamp': message.timestamp.strftime("%A, %H:%M")
        }
        for message in messages
    ]
    
    # Pass the messages to the template
    return render_template('chat.html', username=session['user'], messages=formatted_messages)


@app.route('/send_message', methods=['POST'])
def send_message():
    username = session.get('user', 'Anonymous')
    message_content = f"{username}: {request.form.get('message')}"
    timestamp = datetime.utcnow()

    new_message = Message(username=username, room=session.get('chatroom', 'general'), message=message_content, timestamp=timestamp)
    db.session.add(new_message)  # Add the message to the database session
    db.session.commit()  # Commit the session to store the message in the database

    # Use pusher to broadcast this message to all the clients
    pusher.trigger('chatroom', 'new_message', {
        'user': username,
        'message': message_content,
        'timestamp': timestamp.strftime("%A, %H:%M")
    })

    return jsonify(success=True)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
