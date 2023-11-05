from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pusher import Pusher
from dotenv import load_dotenv
from datetime import datetime
from db import db, Message, Company, User, ChatRoom
from flask import flash
import hashlib
import random
import string
import uuid
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_required, current_user, login_user




app = Flask(__name__)

load_dotenv(dotenv_path='.env')
app.secret_key = 'some_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Add your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


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
        "pacifictrout": "App123",
        "dingleberry": "App123",
      
    }
    

    @staticmethod
    def login(username, password):
        if TerminalChat.users.get(username) == password:
            session['user'] = username
            return True
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None  # Initialize an error message variable

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:  # Check if either field is empty
            error_message = 'Username and password are required.'
        else:
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                user_primary_key = user.id  # Since you've already queried the user above
                session['user'] = username
                login_user(user) 
                return redirect(url_for('select_chatroom'))
            else:
                error_message = 'Invalid username or password'

    return render_template('login.html', error_message=error_message)
@app.route('/chatroom', methods=['GET', 'POST'])
def select_chatroom():
    
       

    # Retrieve the user from the database to get their company_id
    user = User.query.filter_by(username=session['user']).first()
    print(user)
    
    company_id = user.company_id

    # Now fetch chatrooms that are associated with the user's company_id
    chatrooms = ChatRoom.query.filter_by(company_id=company_id).all()

    if request.method == 'POST':
        chatroom_name = request.form['chatroom']
        print(chatroom_name)
        chatroom = ChatRoom.query.filter_by(name=chatroom_name, company_id=company_id).first()
        print(chatroom)
        if chatroom:
            # If using Pusher, trigger an event for the chatroom that the user has joined
            pusher.trigger('chatroom', 'user_joined', {'message': f"{session['user']} joined the chat"})
            # Here, you should probably store the selected chatroom in the session or handle it somehow
            session['current_chatroom'] = chatroom.name
            session['chatroom'] = chatroom.name
            
            return redirect(url_for('chat'))

    # Pass the chatrooms to the template
    return render_template('chatroom.html', chatrooms=chatrooms)

@app.route('/chat')
def chat():
    print()
    
    new_room = session.get('current_chatroom')
    
    # Fetch the last N messages from the database
    # Adjust the number of messages as needed
    num_messages_to_load = 1000  # For example, load the last 50 messages
    messages = Message.query \
        .filter_by(room=session['current_chatroom']) \
        .order_by(Message.timestamp.asc()) \
        .limit(num_messages_to_load) \
        .all()
    print(messages)
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
    print(username)
    message_content = f"{username}: {request.form.get('message')}"
    timestamp = datetime.utcnow()
    chatroom_id = session.get('chatroom_id')
    new_message = Message(username=username, room=session.get('chatroom', 'general'), message=message_content, timestamp=timestamp, company_id=current_user.company_id, chatroom_id=chatroom_id)
    db.session.add(new_message)  # Add the message to the database session
    db.session.commit()  # Commit the session to store the message in the database

    # Use pusher to broadcast this message to all the clients
    pusher.trigger('chatroom', 'new_message', {
        'user': username,
        'message': message_content,
        'timestamp': timestamp.strftime("%A, %H:%M")
    })

    return jsonify(success=True)


@app.route('/register_organization', methods=['GET', 'POST'])
def register_organization():
    if request.method == 'POST':
        company_name = request.form['company_name']
        # Add your logic to create the organization here
        # For example, save to database
        return redirect(url_for('some_route'))  # Redirect to a confirmation page or dashboard
    return render_template('create-organization.html')

@app.route('/create-organization', methods=['GET', 'POST'])
def create_organization():
    if request.method == 'POST':
        company_name = request.form['company_name']

        if company_name:
            existing_company = Company.query.filter_by(name=company_name).first()
            if existing_company:
                flash('Company already exists.')
                return render_template('create-organization.html')

            # Create a new company if it doesn't exist
            new_company = Company(name=company_name)
            
            # Generate a random password
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Use the set_password method to hash and set the password
            new_company.set_password(random_password)

            try:
                # Add the new company to the session and commit to get its ID
                db.session.add(new_company)
                db.session.commit()
                
                # Store the company's unique_id and random_password for further use
                session['company_unique_id'] = new_company.unique_id
                session['company_password'] = random_password
                
                flash('Company created successfully.')
                # Redirect using the company's unique_id property
                return redirect(url_for('organization_start', company_name=company_name, unique_id=new_company.unique_id, password=random_password))

            except Exception as e:
                db.session.rollback()
                app.logger.error('Error creating company: %s', e)
                flash('An error occurred while creating the company.')
                return render_template('create-organization.html')
        else:
            flash('Company name cannot be empty.')
            return render_template('create-organization.html')

    # GET request
    return render_template('create-organization.html')

@app.route('/organization-start/<company_name>/<unique_id>/<password>')
def organization_start(company_name, unique_id, password):
    # Retrieve the unique ID and password from the session
    unique_id = session.pop('company_unique_id', None)
    password = session.pop('company_password', None)
    session['company_id'] = unique_id
    if unique_id and password:
        # Render a template that shows the unique ID and password securely
        return render_template('organization-start.html', company_name=company_name, unique_id=unique_id, password=password)
    else:
        # If there is no unique ID or password in the session, redirect to home
        flash('No company information found.')
        return redirect(url_for('index'))

@app.route('/join-organization', methods=['GET'])
def redirect_organization():
    # Simply render the join-organization.html template on GET request
    return render_template('join-organization.html')


@app.route('/join-organization', methods=['POST'])
def join_organization():
    # Extract form data
    print(request.form)
    company_id = request.form.get('company_id')
    company_password = request.form.get('company_password')
    username = request.form.get('username')
    user_password = request.form.get('user_password')

    # Verify company
    company = Company.query.filter_by(unique_id=company_id).first()
    if company and check_password_hash(company.password_hash, company_password):
        # Company verified, now handle user

        # Check if username already exists within this company
        existing_user = User.query.filter_by(username=username, company_id=company.id).first()
        
        if existing_user:
            flash('Username already exists within this company.')
            return render_template('join-organization.html')

        # Generate a unique user ID using UUID
        new_user_id = str(uuid.uuid4())

        # Create a new user with the generated ID
        new_user = User(
            id=new_user_id,
            username=username, 
            password_hash=generate_password_hash(user_password), # Hash the user's password
            company_id=company.unique_id # Associate user with the company
        )
        db.session.add(new_user)
        
        try:
            db.session.commit()
            flash('Successfully joined the organization.')
            # Redirect to the user's dashboard or another appropriate page
            return redirect(url_for('dashboard', user_id=new_user.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.')
            return render_template('join-organization.html')

    else:
        flash('Invalid company ID or password.')
        return render_template('join-organization.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    error_message = None  # Initialize the error message to None

    if request.method == 'POST':
        chatroom_name = request.form.get('chatroom_name')
        if chatroom_name:
            # Create a new ChatRoom instance
            new_chatroom = ChatRoom(name=chatroom_name, company_id=current_user.company_id)
            # Add the new chatroom to the session and commit to the database
            db.session.add(new_chatroom)
            try:
                db.session.commit()
                # If commit is successful, you could also pass a success message similarly
            except Exception as e:
                db.session.rollback()
                error_message = f'Error adding chat room: {e}'  # Store the error message
        else:
            error_message = 'Chatroom name is required.'  # Set the error message if chatroom name is not provided

    chatrooms = ChatRoom.query.filter_by(company_id=current_user.company_id).all()
    return render_template('dashboard.html', chatrooms=chatrooms, error_message=error_message)



@app.route('/create-channels')
def create_channels():
    company_id = request.args.get('company_id') or session.get('company_id')
    # This could be a page where the admin can manage or create new channels.
    return redirect(url_for('dashboard', company_id=company_id))


@login_manager.user_loader
def load_user(user_id):
    # Assuming your user model's ID is an integer.
    # Adjust the query if your user identifier is of a different type
    return User.query.get(user_id)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)