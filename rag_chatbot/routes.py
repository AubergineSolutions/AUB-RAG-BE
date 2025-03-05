import os
from flask import Blueprint, request, jsonify, send_from_directory
from .services.file_processing import process_file
from .services.chat import get_answer
from .utils.helpers import get_uploaded_files
from .config import Config

main = Blueprint("main", __name__)


@main.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"./uploads/{file.filename}"
    file.save(file_path)

    try:
        process_file(file_path)
        return jsonify({"message": "File processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = get_answer(user_message)
    return jsonify({"response": response})

@main.route("/files", methods=["GET"])
def list_files():
    """API to list all uploaded files"""
    files = get_uploaded_files()
    return jsonify({"files": files})

@main.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """API to download or open an uploaded file"""
    upload_folder = os.path.abspath(Config.UPLOAD_FOLDER)
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # "conditional" parameter added to bypass cache validation and return file instead for response 200
    return send_from_directory(upload_folder, filename, conditional=False)