# Import necessary Flask classes and functions for web routing, sessions, flashing messages, etc.
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Import SocketIO and methods to enable real-time messaging
from flask_socketio import SocketIO, send, emit

# Import os for possible file path handling (not strictly needed here but good to have)
import os

# Initialize the Flask application
app = Flask(__name__)

# Set a secret key for session management and security.
# This is used to encrypt session cookies and protect against tampering.
app.config['SECRET_KEY'] = 'testing' # Secret Key should be stronger and secret but this is a personal project so YOLO

# Wrap the Flask app with SocketIO to enable WebSocket support for real-time messaging.
# Now we can handle events like 'connect', 'disconnect', 'message', etc.
socketio = SocketIO(app)

# The path to the file where registered users will be stored.
# Each line in this file will contain: user_id,username,password
USER_INFO = 'users.txt'


# ---------- USER MANAGEMENT FUNCTIONS ----------

# Loads the user data from the text file and converts it into a list of dictionaries.
def load_users():
    try:
        # Open the user file in read mode
        with open(USER_INFO, 'r') as file:
            users = file.readlines()
        # For each line in the file, split it by comma and build a dictionary
        return [
            {
                'id': int(user.split(',')[0]),
                'username': user.split(',')[1].strip(),
                'password': user.split(',')[2].strip()
            } for user in users
        ]
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty list
        return []

# Saves a new user to the file by appending a line in CSV format: id,username,password
def save_user(user_id, username, password):
    with open(USER_INFO, 'a') as file:
        file.write(f"{user_id},{username},{password}\n")


# ---------- ROUTES ----------

# Home page route – if user is logged in, redirect to chat; otherwise, to login
@app.route('/')
def index():
    if 'username' in session:
        # If the user is logged in, show the chat interface
        return render_template('chat.html', username=session['username'])
    # If not logged in, redirect to login page
    return render_template(url_for('login'))


# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract the submitted username and password
        username = request.form['username']
        password = request.form['password']

        # Load the existing users
        users = load_users()

        # Check if the username already exists
        if any(user['username'] == username for user in users):
            flash("Sorry! Chosen username is already in use. Please select a new username")
            return redirect(url_for('register'))

        # Assign a new user ID based on the total number of users
        user_id = len(users) + 1

        # Save the new user to the file
        save_user(user_id, username, password)

        flash("Your account has been created successfully. You can now log in")
        return redirect(url_for('login'))

    # Render the registration form
    return render_template('register.html')


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from submitted form
        username = request.form['username']
        password = request.form['password']

        # Load users from the file
        users = load_users()

        # Check if any user matches the submitted credentials
        user = next((user for user in users if user['username'] == username and user['password'] == password), None)

        if user:
            # Store username in session so we know the user is logged in
            session['username'] = username
            return redirect(url_for('index'))

        # If credentials are incorrect
        flash("Invalid Username or Password")

    # Render the login form
    return render_template('login.html')


# Logout route to remove the user from session
@app.route('/logout')
def logout():
    # Remove the 'username' from session, effectively logging the user out
    session.pop('username', None)
    return redirect(url_for('login'))


# ---------- SOCKETIO EVENT HANDLER ----------

# This function is triggered whenever a client sends a message event
@socketio.on('message')
def handle_message(msg):
    # Get the username from the session to associate it with the message
    username = session.get('username')

    # Only proceed if the user is authenticated (exists in session)
    if username:
        # Print the message to the server console (for debug/logging)
        print(f'{username}: {msg}')

        # Send the message back to all connected clients with the sender’s username
        send({'msg': msg, 'username': username}, broadcast=True)


# ---------- APPLICATION ENTRY POINT ----------

# Run the app using socketio's run method (instead of Flask's app.run)
# Enables WebSocket support and auto-reloading with debug=True
if __name__ == '__main__':
    socketio.run(app, debug=True)
