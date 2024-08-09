from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send
from pymongo import MongoClient
from datetime import datetime
import secrets
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_db']
messages_collection = db['messages']


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Load the last 50 messages from the database
    messages = messages_collection.find().sort('timestamp', -1).limit(50)
    messages = reversed(list(messages))  # Reverse to show the latest at the bottom
    return render_template('chat.html', messages=messages, username=session['username'])


@socketio.on('message')
def handleMessage(msg):
    username = session.get('username', 'Anonymous') # defaults to Anonymous if none defined

    # Save the message to MongoDB
    message_data = {
        'username': username,
        'message': msg,
        'timestamp': datetime.utcnow()
    }
    messages_collection.insert_one(message_data)

    # Broadcast the message to all clients
    send(f'{username}: {msg}', broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
