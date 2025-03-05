from flask_socketio import emit

def configure_websocket(socketio):
    @socketio.on('initialize_chat', namespace='/chat')
    def handle_initialize_chat(data):
        emit('chat_initialized', {'message': 'Welcome to the chat!'}, broadcast=True)

    @socketio.on('send_message', namespace='/chat')
    def handle_send_message(data):
        user_message = data.get('message', '')
        response = f"Message received: {user_message}"
        emit('receive_message', {'message': response}, broadcast=True)
