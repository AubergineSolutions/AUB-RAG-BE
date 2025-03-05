from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from .websocket import configure_websocket
from .routes import main


def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
    configure_websocket(socketio)
    app.register_blueprint(main)
    return app, socketio