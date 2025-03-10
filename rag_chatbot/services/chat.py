from langchain.prompts import PromptTemplate
from ..services.vectorstore import get_vectorstore
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from ..config import Config
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template='''\n    You are an AI assistant. Answer based on the context provided.\n    \n    {context}\n    ---\n    User Query: {question}\n    ''')

def get_answer(query):
    """
    Get an answer to a query using the RAG system
    
    Args:
        query (str): The user's query
        
    Returns:
        dict: A dictionary containing the answer and sources
    """
    # Get the vector store
    vectorstore = get_vectorstore()
    if vectorstore is None:
        logger.error("Vector store is not initialized")
        raise ValueError("Vector store is not initialized. Please check the logs for more information.")
    
    try:
        # Check if API key is available
        api_key = Config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key is missing")
            raise ValueError("OpenAI API key is required for answering queries")
        
        # Create retriever
        logger.info("Creating retriever")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Initialize LLM
        logger.info("Initializing LLM")
        llm = ChatOpenAI(model_name="gpt-4", api_key=api_key)
        
        # Create QA chain
        logger.info("Creating QA chain")
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
        
        # Get response
        logger.info(f"Getting answer for query: {query}")
        response = qa_chain.invoke({"query": query})
        
        # Extract answer and sources
        answer = response["result"]
        sources = [doc.metadata["source"] for doc in response["source_documents"]]
        
        logger.info(f"Answer: {answer}")
        logger.info(f"Sources: {sources}")
        
        return {"answer": answer, "sources": sources}
    except Exception as e:
        logger.error(f"Error getting answer: {str(e)}")
        raise