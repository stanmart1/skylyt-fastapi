import os
import uuid
from typing import Dict, Any
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


class FileUploadService:
    
    def __init__(self, upload_dir: str = "uploads/payment_proofs"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def save_payment_proof(self, file: UploadFile, transfer_reference: str) -> Dict[str, Any]:
        """Save uploaded payment proof file"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{transfer_reference}_{uuid.uuid4().hex[:8]}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            file_info = {
                "file_path": file_path,
                "file_name": file.filename,
                "unique_filename": unique_filename,
                "file_size": len(content),
                "mime_type": file.content_type
            }
            
            logger.info(f"Saved payment proof: {unique_filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to save payment proof: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file"""
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        max_size = 5 * 1024 * 1024  # 5MB
        
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        # Check file type
        if file.content_type not in allowed_types:
            validation_result["valid"] = False
            validation_result["errors"].append("Invalid file type. Only JPEG, PNG, and PDF files are allowed.")
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            validation_result["valid"] = False
            validation_result["errors"].append("File size exceeds 5MB limit.")
        
        if file_size == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("File is empty.")
        
        return validation_result