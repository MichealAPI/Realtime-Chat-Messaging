const socket = io();

socket.on('message', function (msg) {
    document.getElementById('messages').innerHTML += '<li>' + msg + '</li>';
});

// Sends a message to the server (MongoDB)
function sendMessage() {
    const msg = document.getElementById('myMessage').value;
    socket.send(msg);
    document.getElementById('myMessage').value = '';
}