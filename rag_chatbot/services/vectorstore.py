import os
import logging
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
            # Log API key status (without revealing the key)
            api_key_status = "available" if (hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY) else "missing"
            logging.info(f"Initializing vector store. OpenAI API key status: {api_key_status}")
            
            # Check if the vectorstore directory exists
            if os.path.exists(Config.VECTORSTORE_PATH):
                logging.info(f"Vector store directory exists at {Config.VECTORSTORE_PATH}")
                # Initialize with embedding function if available
                if hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY:
                    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
                    vectorstore = Chroma(
                        persist_directory=Config.VECTORSTORE_PATH, 
                        embedding_function=embeddings,
                        collection_name=Config.COLLECTION
                    )
                    logging.info("Vector store initialized with embedding function")
                else:
                    # Fallback to environment variable directly if Config doesn't have it
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        logging.info("Using OpenAI API key from environment variable")
                        embeddings = OpenAIEmbeddings(api_key=api_key)
                        vectorstore = Chroma(
                            persist_directory=Config.VECTORSTORE_PATH, 
                            embedding_function=embeddings,
                            collection_name=Config.COLLECTION
                        )
                        logging.info("Vector store initialized with embedding function from environment")
                    else:
                        logging.error("OpenAI API key is missing. Cannot initialize vector store with embedding function.")
                        raise ValueError("OpenAI API key is required for initializing the vector store")
            else:
                # Create directory if it doesn't exist
                logging.info(f"Creating vector store directory at {Config.VECTORSTORE_PATH}")
                os.makedirs(os.path.dirname(Config.VECTORSTORE_PATH), exist_ok=True)
                
                # Initialize with embedding function
                if hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY:
                    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
                    vectorstore = Chroma(
                        persist_directory=Config.VECTORSTORE_PATH, 
                        embedding_function=embeddings,
                        collection_name=Config.COLLECTION
                    )
                    logging.info("New vector store initialized with embedding function")
                else:
                    # Fallback to environment variable directly if Config doesn't have it
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        logging.info("Using OpenAI API key from environment variable")
                        embeddings = OpenAIEmbeddings(api_key=api_key)
                        vectorstore = Chroma(
                            persist_directory=Config.VECTORSTORE_PATH, 
                            embedding_function=embeddings,
                            collection_name=Config.COLLECTION
                        )
                        logging.info("New vector store initialized with embedding function from environment")
                    else:
                        logging.error("OpenAI API key is missing. Cannot initialize vector store with embedding function.")
                        raise ValueError("OpenAI API key is required for initializing the vector store")
        
        return vectorstore
    except Exception as e:
        logging.error(f"Error initializing vector store: {str(e)}")
        # Return None in case of error
        return e

def reset_vectorstore():
    """
    Reset the global vectorstore instance
    """
    global vectorstore
    vectorstore = None
