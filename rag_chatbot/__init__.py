from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from .websocket import configure_websocket
from .routes import main
from .config import Config


def create_app():
    # Load environment variables
    load_dotenv()
    
    # Initialize application directories
    Config.init_app()
    
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
    
    return app, socketio