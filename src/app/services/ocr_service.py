"""
OCR Service - Handles PDF text extraction using Optical Character Recognition
This service is responsible for converting PDF files to text
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

# OCR imports
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class OCRService:
    """
    Service class for handling PDF text extraction using OCR
    """
    
    def __init__(self):
        """
        Initialize the OCR service and check if required libraries are available
        """
        self.is_available = OCR_AVAILABLE
        if not self.is_available:
            print("⚠️  OCR libraries not available. Install with: pip install pytesseract pdf2image")
    
    def is_ocr_available(self) -> bool:
        """
        Check if OCR functionality is available
        """
        return self.is_available
    
    def extract_text_from_pdf_bytes(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from PDF file bytes using OCR
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename for logging
            
        Returns:
            Dict with success, message, data (extracted text), and error fields
        """
        if not self.is_available:
            return {
                "success": False,
                "message": "OCR libraries not available",
                "error": "OCR_NOT_AVAILABLE",
                "data": None
            }
        
        temp_file_path = None
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Extract text using OCR
            extracted_text = self._extract_text_from_pdf_file(temp_file_path, filename)
            
            return {
                "success": True,
                "message": f"Successfully extracted text from {filename}",
                "data": extracted_text,
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text from {filename}",
                "error": str(e),
                "data": None
            }
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def extract_text_from_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file path using OCR
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict with success, message, data (extracted text), and error fields
        """
        if not self.is_available:
            return {
                "success": False,
                "message": "OCR libraries not available",
                "error": "OCR_NOT_AVAILABLE",
                "data": None
            }
        
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "message": f"PDF file not found: {pdf_path}",
                "error": "FILE_NOT_FOUND",
                "data": None
            }
        
        try:
            filename = os.path.basename(pdf_path)
            extracted_text = self._extract_text_from_pdf_file(pdf_path, filename)
            
            return {
                "success": True,
                "message": f"Successfully extracted text from {filename}",
                "data": extracted_text,
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text from {pdf_path}",
                "error": str(e),
                "data": None
            }
    
    def _extract_text_from_pdf_file(self, pdf_path: str, filename: str) -> str:
        """
        Internal method to extract text from PDF file using OCR
        
        Args:
            pdf_path: Path to the PDF file
            filename: Filename for logging
            
        Returns:
            Extracted text as string
        """
        print(f"🔄 Using OCR to extract text from: {filename}")
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        text = ""
        for i, image in enumerate(images):
            print(f"📄 Processing page {i+1} with OCR...")
            page_text = pytesseract.image_to_string(image)
            print(f"✅ Page {i+1} extracted {len(page_text)} characters")
            text += page_text + "\n"
        
        extracted_text = text.strip()
        print(f"🎉 Total extracted text: {len(extracted_text)} characters")
        
        return extracted_text
    
    def get_ocr_info(self) -> Dict[str, Any]:
        """
        Get information about OCR service status
        """
        info = {
            "ocr_available": self.is_available,
            "service_status": "available" if self.is_available else "unavailable"
        }
        
        if self.is_available:
            try:
                # Try to get tesseract version
                import pytesseract
                info["tesseract_version"] = str(pytesseract.get_tesseract_version())
            except:
                info["tesseract_version"] = "unknown"
        else:
            info["required_packages"] = ["pytesseract", "pdf2image"]
            info["install_command"] = "pip install pytesseract pdf2image"
        
        return info

# Global OCR service instance
ocr_service = OCRService()
