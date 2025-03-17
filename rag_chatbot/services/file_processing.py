import os.path
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma.vectorstores import Chroma
from ..config import Config

def get_document_loader(file_path):
    if file_path.endswith('.pdf'):
        return PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        return TextLoader(file_path)
    elif file_path.endswith('.docx' or '.doc'):
        return UnstructuredWordDocumentLoader(file_path)
    elif file_path.endswith('.csv'):
        return CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type for file: {file_path}")

def process_file(file_paths, file_metadata=None):
    """
    Process files and store them in the vector database
    
    Args:
        file_paths (list): List of file paths to process
        file_metadata (list, optional): List of metadata dictionaries for each file
    
    Returns:
        list: List of document IDs added to the vector store
    """
    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
    text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    added_doc_ids = []

    # Initialize or load existing vector store
    if os.path.exists(Config.VECTORSTORE_PATH):
        vector_store = Chroma(
            persist_directory=Config.VECTORSTORE_PATH,
            embedding_function=embeddings,
            collection_name=Config.COLLECTION
        )
    else:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(Config.VECTORSTORE_PATH), exist_ok=True)
        vector_store = Chroma(
            persist_directory=Config.VECTORSTORE_PATH,
            embedding_function=embeddings,
            collection_name=Config.COLLECTION
        )

    # Create a metadata lookup dictionary if metadata is provided
    metadata_lookup = {}
    if file_metadata:
        for meta in file_metadata:
            if "file_path" in meta:
                metadata_lookup[meta["file_path"]] = meta

    # Process each file
    for i, file_path in enumerate(file_paths):
        try:
            # Load the document
            loader = get_document_loader(file_path)
            documents = loader.load()
            
            # Split documents into chunks using the text splitter
            split_docs = text_splitter.split_documents(documents)
            
            # Generate unique ID for this file
            doc_id = str(uuid.uuid4())
            
            # Get file metadata if available
            file_meta = metadata_lookup.get(file_path, {})
            if not file_meta and file_metadata and i < len(file_metadata):
                file_meta = file_metadata[i]
            
            # Add doc_id to metadata
            file_meta["doc_id"] = doc_id
            
            # Extract texts and prepare metadata for each chunk
            texts = []
            metadatas = []
            ids = []
            
            for j, doc in enumerate(split_docs):
                # Add the text content
                texts.append(doc.page_content)
                
                # Create metadata for this chunk
                chunk_meta = file_meta.copy()
                chunk_meta.update({
                    "source": os.path.basename(file_path),
                    "full_path": file_path,
                    "chunk_id": j
                })
                
                # If the document has metadata, merge it with our metadata
                if hasattr(doc, 'metadata') and doc.metadata:
                    for key, value in doc.metadata.items():
                        if key not in chunk_meta:
                            chunk_meta[key] = value
                
                metadatas.append(chunk_meta)
                ids.append(f"{doc_id}_{j}")
            
            # Add texts to the vector store
            if texts:
                vector_store.add_texts(
                    texts=texts,
                    ids=ids,
                    metadatas=metadatas
                )
                
                added_doc_ids.append(doc_id)
            else:
                print(f"Warning: No text content extracted from {file_path}")

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            continue

    return added_doc_ids

