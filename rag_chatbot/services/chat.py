from ..services.vectorstore import get_vectorstore
from langchain_openai import ChatOpenAI
from ..config import Config
import logging
import os
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


def format_chat_history(messages):
    """
    Convert chat history messages into a formatted string.
    
    Args:
        messages (list): List of HumanMessage and AIMessage objects.
        
    Returns:
        str: Formatted chat history.
    """
    formatted_history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted_history.append(f"AI: {msg.content}")
    return "\n".join(formatted_history)

def get_answer(question, chat_history):
    """
    Get an answer to a query using the RAG system
    
    Args:
        question (str): The user's query
        
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
        llm = ChatOpenAI(model_name="gpt-4o", api_key=api_key)
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )
        
        # Create QA chain with memory
        logger.info("Creating QA chain with memory")        
        
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        response = rag_chain.invoke({"input": question, "chat_history": chat_history})
                
        # Extract answer and sources
        answer = response["answer"]
        
        logger.info(f"Answer: {answer}")
        
        return {
            "answer": answer,
            "query": question,
            "chat_history": chat_history
        }
    except Exception as e:
        logger.error(f"Error getting answer: {str(e)}")
        raise