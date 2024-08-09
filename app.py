from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
from pymongo import MongoClient
from datetime import datetime
import time

app = Flask(__name__)
# TODO: secret-key
socketio = SocketIO(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_db']
messages_collection = db['messages']


@app.route('/')
def index():
    # Load the last 30 messages from the database
    messages = messages_collection.find().sort('timestamp', -1).limit(30)
    messages = reversed(list(messages))  # Reverse to show the latest at the bottom
    return render_template('index.html', messages=messages)


@socketio.on('message')
def handleMessage(msg):

    # Save the message to MongoDB
    message_data = {
        'username': request.remote_addr,  # I will be using usernames here
        'message': msg,
        'timestamp': datetime.fromtimestamp(time.time())
    }
    messages_collection.insert_one(message_data)

    # Broadcast the message to all clients
    send(msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
