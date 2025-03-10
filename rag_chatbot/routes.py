import os
import uuid
import datetime
from flask import Blueprint, request, jsonify, send_from_directory
from .services.file_processing import process_file
from .utils.helpers import get_uploaded_files, get_file_metadata, format_file_size
from .config import Config
from .services.vectorstore import get_vectorstore

main = Blueprint("main", __name__)


@main.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    # Use allowed extensions from Config
    allowed_extensions = Config.ALLOWED_EXTENSIONS
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    files = request.files.getlist('file')
    if files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    uploaded_files = []  # Store uploaded filenames for response
    file_metadata = []   # Store metadata for response

    # Ensure upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            # Generate a unique filename to prevent overwriting
            original_filename = file.filename
            file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
            
            # Create a filename with format: original_name_uuid.extension
            unique_id = uuid.uuid4().hex[:8]  # Use shorter UUID for readability
            unique_filename = f"{base_name}_{unique_id}.{file_extension}" if file_extension else f"{base_name}_{unique_id}"
            
            filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Get current timestamp
            upload_time = datetime.datetime.now()
            
            # Create metadata
            metadata = {
                "original_filename": original_filename,
                "stored_filename": unique_filename,
                "file_extension": file_extension,
                "file_size": file_size,
                "formatted_file_size": format_file_size(file_size),
                "upload_date": upload_time.strftime("%Y-%m-%d"),
                "upload_time": upload_time.strftime("%H:%M:%S"),
                "timestamp": upload_time.timestamp(),
                "file_path": filepath,
                "doc_id": unique_id  # For compatibility with vectorstore metadata
            }
            uploaded_files.append(filepath)
            file_metadata.append(metadata)
        else:
            return jsonify({"error": f"Unsupported file type for {file.filename}. Allowed types: {', '.join(allowed_extensions)}"}), 403

    try:
        # Process files and pass metadata
        process_file(uploaded_files, file_metadata)
        return jsonify({
            "message": "Files processed successfully",
            # "files": file_metadata
        }), 200
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        return jsonify({"error": str(e)}), 500


@main.route("/files", methods=["GET"])
def list_files():
    """API to list all uploaded files with metadata"""
    try:
        # First, get files directly from the upload directory
        files = get_uploaded_files()
        file_metadata_list = []
        stored_file_metadata = {}

        # Try to get additional metadata from vectorstore
        vectorstore = get_vectorstore()
        if vectorstore:
            try:
                all_docs = vectorstore.get(include=["metadatas"])
                if all_docs and "metadatas" in all_docs and all_docs["metadatas"]:
                    # Process metadata from vectorstore
                    # Group by doc_id to avoid duplicates (since documents are chunked)
                    for metadata in all_docs["metadatas"]:
                        if "stored_filename" in metadata and "doc_id" in metadata:
                            stored_filename = metadata.get("stored_filename")
                            doc_id = metadata.get("doc_id")
                            
                            # Only add if not already in our list
                            if stored_filename not in stored_file_metadata:
                                stored_file_metadata[stored_filename] = metadata
            except Exception as e:
                print(f"Error retrieving metadata from vectorstore: {str(e)}")
                # Continue with file system metadata only

        # If still no files found, return empty list
        for filename in files:
            # Check if we already have metadata from vectorstore
            if filename in stored_file_metadata:
                metadata = stored_file_metadata[filename]
                # Format file size for display if not already formatted
                if "file_size" in metadata and "formatted_file_size" not in metadata:
                    metadata["formatted_file_size"] = format_file_size(metadata["file_size"])
                file_metadata_list.append(metadata)
            else:
                # Get metadata from filesystem
                metadata = get_file_metadata(filename)
                if metadata:
                    # Format file size for display
                    if "file_size" in metadata:
                        metadata["formatted_file_size"] = format_file_size(metadata["file_size"])
                    file_metadata_list.append(metadata)
        
        # Sort by upload time if available
        file_metadata_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return jsonify(file_metadata_list)
    except Exception as e:
        print(f"Error in list_files: {str(e)}")
        return jsonify({"error": str(e)}), 500


@main.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """API to download or open an uploaded file with metadata"""
    upload_folder = os.path.abspath(Config.UPLOAD_FOLDER)
    
    # Check if metadata parameter is provided and is true
    metadata_only = request.args.get("metadata", "").lower() == "true"
    
    # Check if the filename exists directly in the upload folder
    file_path = os.path.join(upload_folder, filename)
    
    if os.path.exists(file_path):
        # File exists directly
        file_metadata = get_file_metadata(filename)
        
        # Add formatted file size
        if file_metadata and "file_size" in file_metadata:
            file_metadata["formatted_file_size"] = format_file_size(file_metadata["file_size"])
        
        if metadata_only:
            return jsonify(file_metadata)
        
        # Return the file
        return send_from_directory(upload_folder, filename, conditional=False)
    
    # File doesn't exist directly, try to find it in the vectorstore
    try:
        vectorstore = get_vectorstore()
        if not vectorstore:
            return jsonify({"error": "File not found and vectorstore not available"}), 404
            
        all_docs = vectorstore.get(include=["metadatas"])
        
        if all_docs and "metadatas" in all_docs:
            # First, try to find by stored_filename
            for metadata in all_docs["metadatas"]:
                if metadata.get("stored_filename") == filename:
                    stored_filename = metadata["stored_filename"]
                    file_path = os.path.join(upload_folder, stored_filename)
                    
                    if os.path.exists(file_path):
                        if metadata_only:
                            # Add formatted file size
                            if "file_size" in metadata:
                                metadata["formatted_file_size"] = format_file_size(metadata["file_size"])
                            return jsonify(metadata)
                        
                        return send_from_directory(upload_folder, stored_filename, conditional=False)
            
            # Next, try to find by original_filename
            for metadata in all_docs["metadatas"]:
                if metadata.get("original_filename") == filename and "stored_filename" in metadata:
                    stored_filename = metadata["stored_filename"]
                    file_path = os.path.join(upload_folder, stored_filename)
                    
                    if os.path.exists(file_path):
                        if metadata_only:
                            # Add formatted file size
                            if "file_size" in metadata:
                                metadata["formatted_file_size"] = format_file_size(metadata["file_size"])
                            return jsonify(metadata)
                        
                        return send_from_directory(upload_folder, stored_filename, conditional=False)
            
            # Finally, try to find by source
            for metadata in all_docs["metadatas"]:
                if metadata.get("source") == filename and "stored_filename" in metadata:
                    stored_filename = metadata["stored_filename"]
                    file_path = os.path.join(upload_folder, stored_filename)
                    
                    if os.path.exists(file_path):
                        if metadata_only:
                            # Add formatted file size
                            if "file_size" in metadata:
                                metadata["formatted_file_size"] = format_file_size(metadata["file_size"])
                            return jsonify(metadata)
                        
                        return send_from_directory(upload_folder, stored_filename, conditional=False)
    
    except Exception as e:
        print(f"Error retrieving file from vectorstore: {str(e)}")
    
    # If we get here, the file was not found
    return jsonify({"error": "File not found"}), 404


@main.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    """API to delete a file and its embeddings"""
    try:
        upload_folder = os.path.abspath(Config.UPLOAD_FOLDER)
        file_path = os.path.join(upload_folder, filename)
        
        # Initialize variables to track deletion
        file_deleted = False
        embeddings_deleted = False
        doc_id = None
        stored_filename = None
        
        # Get vectorstore
        vectorstore = get_vectorstore()
        if not vectorstore:
            return jsonify({"error": "Vectorstore not available"}), 500
        
        # Check if the file exists directly
        if os.path.exists(file_path):
            stored_filename = filename
            # Get metadata to find doc_id
            metadata = get_file_metadata(filename)
            if metadata and "doc_id" in metadata:
                doc_id = metadata["doc_id"]
            
            # Delete the physical file
            os.remove(file_path)
            file_deleted = True
        else:
            # Try to find by original filename in vectorstore
            all_docs = vectorstore.get(include=["metadatas"])
            
            if all_docs and "metadatas" in all_docs:
                # Try to find by original_filename or source
                for metadata in all_docs["metadatas"]:
                    if (metadata.get("original_filename") == filename or 
                        metadata.get("stored_filename") == filename or
                        metadata.get("source") == filename):
                        
                        # Found the file, use stored_filename
                        stored_filename = metadata.get("stored_filename")
                        doc_id = metadata.get("doc_id")
                        
                        if stored_filename:
                            file_path = os.path.join(upload_folder, stored_filename)
                            if os.path.exists(file_path):
                                # Delete the physical file
                                os.remove(file_path)
                                file_deleted = True
                        break
        
        # Delete from vectorstore if doc_id is available
        if doc_id:
            # Delete all chunks with this doc_id
            vectorstore.delete(where={"doc_id": doc_id})
            embeddings_deleted = True
        
        # If we found a filename but no doc_id, try to delete by source or filename
        if stored_filename and not embeddings_deleted:
            # Try deleting by source field
            vectorstore.delete(where={"source": filename})
            vectorstore.delete(where={"source": stored_filename})
            
            # Also try by original_filename
            vectorstore.delete(where={"original_filename": filename})
            vectorstore.delete(where={"stored_filename": stored_filename})
            
            embeddings_deleted = True
        
        if file_deleted or embeddings_deleted:
            return jsonify({
                "message": f"File {filename} processed: file_deleted={file_deleted}, embeddings_deleted={embeddings_deleted}"
            }), 200
        else:
            return jsonify({"error": "File not found and no embeddings deleted"}), 404
            
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return jsonify({"error": str(e)}), 500