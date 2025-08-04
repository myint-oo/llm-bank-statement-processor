"""
Bank Statement Controller - Handles bank statement processing endpoints
"""
from fastapi import HTTPException, UploadFile
from typing import Optional
from src.app.services.bank_statement_service import bank_statement_service
from src.api.schemas.requests import ProcessBankStatementRequest
from src.config.settings import settings

class BankStatementController:
    """
    Controller for bank statement processing endpoints
    """
    
    @staticmethod
    def process_text(request: ProcessBankStatementRequest):
        """
        Process bank statement from text content
        """
        if not request.text_content:
            raise HTTPException(status_code=400, detail="text_content is required")
        
        result = bank_statement_service.process_text(
            text_content=request.text_content,
            customer_id=request.customer_id
        )
        
        return result
    @staticmethod
    def process_file(file: UploadFile, customer_id: Optional[str] = None):
        """
        Process bank statement from uploaded PDF file
        """
        # Validate file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        try:
            # Read file content
            file_content = file.file.read()
            
            # Check file size
            if len(file_content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Process the file
            result = bank_statement_service.process_file(
                file_content=file_content,
                filename=file.filename,
                customer_id=customer_id
            )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")
    
    @staticmethod
    async def process_file_async(file: UploadFile, customer_id: Optional[str] = None):
        """
        Async version of process_file for better performance
        """
        # Validate file type
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        try:
            # Read file content asynchronously
            file_content = await file.read()
            
            # Check file size
            if len(file_content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Process the file
            result = bank_statement_service.process_file(
                file_content=file_content,
                filename=file.filename,
                customer_id=customer_id
            )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
