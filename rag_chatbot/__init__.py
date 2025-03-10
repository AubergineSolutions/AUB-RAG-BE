from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from .websocket import configure_websocket
from .routes import main
from .config import Config
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Log environment variables (without revealing sensitive values)
    logger.info("Environment variables loaded")
    logger.info(f"OPENAI_API_KEY status: {'available' if os.getenv('OPENAI_API_KEY') else 'missing'}")
    logger.info(f"FLASK_APP: {os.getenv('FLASK_APP')}")
    logger.info(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
    
    # Initialize application directories
    Config.init_app()
    logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
    logger.info(f"Vector store path: {Config.VECTORSTORE_PATH}")
    
    # Create Flask application
    app = Flask(__name__)
    
    # Configure app settings
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    
    # Enable CORS
    CORS(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    configure_websocket(socketio)
    
    # Register blueprints
    app.register_blueprint(main)
    
    logger.info("Application initialized successfully")
    
    return app, socketio