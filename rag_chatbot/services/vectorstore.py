from langchain_community.vectorstores import Chroma
from ..config import Config

vectorstore = None

def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        vectorstore = Chroma(persist_directory=Config.VECTORSTORE_PATH)
    return vectorstore
