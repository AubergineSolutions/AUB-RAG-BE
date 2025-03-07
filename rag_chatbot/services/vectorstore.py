import os
from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from ..config import Config

# Global vectorstore instance
vectorstore = None

def get_vectorstore():
    """
    Get or initialize the vector store
    
    Returns:
        Chroma: The vector store instance
    """
    global vectorstore
    
    try:
        if vectorstore is None:
            # Check if the vectorstore directory exists
            if os.path.exists(Config.VECTORSTORE_PATH):
                # Initialize with embedding function if available
                if hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY:
                    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
                    vectorstore = Chroma(
                        persist_directory=Config.VECTORSTORE_PATH, 
                        embedding_function=embeddings,
                        collection_name=Config.COLLECTION
                    )
                else:
                    # Initialize without embedding function (for retrieval only)
                    vectorstore = Chroma(
                        persist_directory=Config.VECTORSTORE_PATH,
                        collection_name=Config.COLLECTION
                    )
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(Config.VECTORSTORE_PATH), exist_ok=True)
                
                # Initialize with embedding function
                if hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY:
                    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
                    vectorstore = Chroma(
                        persist_directory=Config.VECTORSTORE_PATH, 
                        embedding_function=embeddings,
                        collection_name=Config.COLLECTION
                    )
                else:
                    raise ValueError("OpenAI API key is required for initializing the vector store")
        
        return vectorstore
    except Exception as e:
        print(f"Error initializing vector store: {str(e)}")
        # Return None in case of error
        return None

def reset_vectorstore():
    """
    Reset the global vectorstore instance
    """
    global vectorstore
    vectorstore = None
