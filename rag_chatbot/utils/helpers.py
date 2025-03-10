import os
import datetime
from ..config import Config
from ..services.vectorstore import get_vectorstore

def get_uploaded_files():
    """
    Get a list of all files in the upload folder
    
    Returns:
        list: List of filenames in the upload folder
    """
    upload_folder = Config.UPLOAD_FOLDER
    if not os.path.exists(upload_folder):
        return []

    return os.listdir(upload_folder)

def get_file_metadata(stored_filename):
    """
    Get metadata for a file in the upload folder
    
    Args:
        filename (str): Name of the file
        
    Returns:
        dict: Metadata for the file or None if file doesn't exist
    """
    try:
        vectorstore = get_vectorstore()
        if vectorstore:
            all_docs = vectorstore.get(include=["metadatas"])
            if all_docs and "metadatas" in all_docs:
                for metadata in all_docs["metadatas"]:
                    if metadata.get("stored_filename") == stored_filename:
                        return metadata  # Return the metadata from the vector store

        # If not found in vector store, check the filesystem
        upload_folder = Config.UPLOAD_FOLDER
        file_path = os.path.join(upload_folder, stored_filename)
        
        if not os.path.exists(file_path):
            return None
        
        # Get file stats
        file_stats = os.stat(file_path)

        # Get file creation/modification times
        creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        modification_time = datetime.datetime.fromtimestamp(file_stats.st_mtime)
        
        # Get file extension
        file_extension = stored_filename.rsplit('.', 1)[1].lower() if '.' in stored_filename else ''
        
        # Try to extract original filename from stored filename
        # Format is original_name_uuid.extension
        original_filename = stored_filename
        if '_' in stored_filename:
            # Try to extract the UUID part (last 8 characters before extension)
            parts = stored_filename.rsplit('.', 1)[0].split('_')
            if len(parts) > 1:
                # The last part should be the UUID
                uuid_part = parts[-1]
                if len(uuid_part) == 8:  # Our UUID length
                    # Reconstruct original filename without UUID
                    original_name = '_'.join(parts[:-1])
                    original_filename = f"{original_name}.{file_extension}" if file_extension else original_name

        # Create metadata
        metadata = {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_extension": file_extension,
            "file_size": file_stats.st_size,
            "creation_date": creation_time.strftime("%Y-%m-%d"),
            "creation_time": creation_time.strftime("%H:%M:%S"),
            "modification_date": modification_time.strftime("%Y-%m-%d"),
            "modification_time": modification_time.strftime("%H:%M:%S"),
            "timestamp": modification_time.timestamp(),
            "file_path": file_path,
            "doc_id": stored_filename.rsplit('.', 1)[0].split('_')[-1] if '_' in stored_filename else ""
        }
        
        return metadata
    except Exception as e:
        print(f"Error getting metadata for file {stored_filename}: {str(e)}")
        return None

def format_file_size(size_in_bytes):
    """
    Format file size in human-readable format
    
    Args:
        size_in_bytes (int): File size in bytes
        
    Returns:
        str: Formatted file size
    """
    # Convert to KB, MB, GB as appropriate
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"
