"""
File upload utilities
"""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import List
import magic

# Configure upload paths
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    
    # Images
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    
    # Videos
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    
    # Audio
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav"
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

def validate_file(file: UploadFile, allowed_types: List[str] = None) -> bool:
    """
    Validate file type and size
    """
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset file pointer
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Get file mime type
    file_content = file.file.read(2048)  # Read first 2048 bytes
    file.file.seek(0)  # Reset file pointer
    mime_type = magic.from_buffer(file_content, mime=True)
    
    # Check file type
    if allowed_types:
        valid_mime_types = [ALLOWED_EXTENSIONS[ext] for ext in allowed_types]
        if mime_type not in valid_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
    
    return True

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """
    Save uploaded file to destination
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Save file
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return destination
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )

async def delete_file(file_path: str) -> bool:
    """
    Delete a file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not delete file: {str(e)}"
        )
