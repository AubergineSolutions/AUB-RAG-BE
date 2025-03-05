import os
from ..config import Config

def get_uploaded_files():
    upload_folder = Config.UPLOAD_FOLDER
    if not os.path.exists(upload_folder):
        return []

    return os.listdir(upload_folder)
