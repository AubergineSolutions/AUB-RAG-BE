import os
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTORSTORE_PATH = "./chroma_db"
    UPLOAD_FOLDER = "./uploads"