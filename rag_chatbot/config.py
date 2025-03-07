import os

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # File storage settings
    UPLOAD_FOLDER = os.path.abspath("./uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv'}
    
    # Vector database settings
    VECTORSTORE_PATH = os.path.abspath("./chroma_db")
    COLLECTION = "knowledge_base"
    
    # Chunking settings
    CHUNK_SIZE = 3000
    CHUNK_OVERLAP = 200
    
    # Ensure directories exist
    @classmethod
    def init_app(cls):
        """Initialize application directories"""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.VECTORSTORE_PATH, exist_ok=True)