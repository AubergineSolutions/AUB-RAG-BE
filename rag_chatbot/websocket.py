from flask_socketio import emit
from .services.vectorstore import get_vectorstore
from .services.chat import get_answer

def configure_websocket(socketio):
    @socketio.on('initialize_chat', namespace='/chat')
    def handle_initialize_chat(data):
        emit('chat_initialized', {'message': 'Welcome to the chat!'}, broadcast=True)

    @socketio.on('send_message', namespace='/chat')
    def handle_send_message(data):
        user_message = data.get('message', '')
        
        # Check if vectorstore is initialized
        vectorstore = get_vectorstore()
        if vectorstore is None:
            emit('receive_message', {'message': 'Error: Vectorstore not initialized.'}, broadcast=True)
            return
        
        try:
            # Get response using RAG
            response = get_answer(user_message)
            emit('receive_message', {
                'message': response['answer'],
                'sources': response['sources']
            }, broadcast=True)
        except Exception as e:
            emit('receive_message', {'message': f'Error processing your request: {str(e)}'}, broadcast=True)
