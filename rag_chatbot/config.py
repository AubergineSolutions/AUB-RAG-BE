import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # File storage settings
    UPLOAD_FOLDER = os.path.abspath("./uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv', 'docx', 'doc', 'zip'}
    
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
        
        # Log configuration
        logger.info(f"OPENAI_API_KEY status: {'available' if cls.OPENAI_API_KEY else 'missing'}")
        logger.info(f"UPLOAD_FOLDER: {cls.UPLOAD_FOLDER}")
        logger.info(f"VECTORSTORE_PATH: {cls.VECTORSTORE_PATH}")
        logger.info(f"COLLECTION: {cls.COLLECTION}")
        
        # If API key is missing, try to get it from environment
        if not cls.OPENAI_API_KEY:
            cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            logger.info(f"Tried to get OPENAI_API_KEY from environment: {'available' if cls.OPENAI_API_KEY else 'missing'}")
            
            # If still missing, log a warning
            if not cls.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY is missing. Some features may not work correctly.")