import logging
from flask_socketio import emit
from .services.vectorstore import get_vectorstore
from .services.chat import get_answer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def configure_websocket(socketio):
    chat_history = []
    @socketio.on('initialize_chat', namespace='/chat')
    def handle_initialize_chat(data):
        """
        Handle the initialize_chat event
        
        Args:
            data (dict): The data sent with the event
        """
        logger.info("Initializing chat")
        emit('chat_initialized', {'message': 'Welcome to the chat!'}, broadcast=True)
        logger.info("Chat initialized")

    @socketio.on('send_message', namespace='/chat')
    def handle_send_message(data):
        """
        Handle the send_message event
        
        Args:
            data (dict): The data sent with the event
        """
        user_message = data.get('message', '')
        logger.info(f"Received message: {user_message}")
        
        # Check if vectorstore is initialized
        vectorstore = get_vectorstore()
        if vectorstore is None:
            error_msg = "Error: Vectorstore not initialized."
            logger.error(error_msg)
            emit('receive_message', {'error': error_msg}, broadcast=True)
            return
        
        try:
            # Get response using RAG
            logger.info("Getting answer")
            response = get_answer(user_message, chat_history)
            chat_history.append({"role": "user", "content": user_message})
            chat_history.append({"role": "assistant", "content": response["answer"]})
            logger.info(f"Answer received: {response['answer'][:50]}...")
            emit('receive_message', {
                'message': response['answer'],
            }, broadcast=True)
            logger.info("Response sent to client")
        except Exception as e:
            error_msg = f"Error processing your request: {str(e)}"
            logger.error(f"Error in handle_send_message: {str(e)}")
            emit('receive_message', {'error': error_msg}, broadcast=True)
