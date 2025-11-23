"""
PDF Text Service - Handles PDF text extraction with fallback to OCR
This service tries to extract text directly from PDF first, then falls back to OCR if needed
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

# PDF text extraction imports
try:
    import PyPDF2
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False

# OCR imports (fallback)
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class PDFTextService:
    """
    Service class for extracting text from PDF files
    Uses direct text extraction first, falls back to OCR if needed
    """
    
    def __init__(self):
        """
        Initialize the PDF text service and check available libraries
        """
        self.pdf_reader_available = PDF_READER_AVAILABLE
        self.ocr_available = OCR_AVAILABLE
        
        if not self.pdf_reader_available:
            print("⚠️  PyPDF2 not available. Install with: pip install PyPDF2")
        if not self.ocr_available:
            print("⚠️  OCR libraries not available. Install with: pip install pytesseract pdf2image")
    
    def is_service_available(self) -> bool:
        """
        Check if at least one text extraction method is available
        """
        return self.pdf_reader_available or self.ocr_available
    
    def extract_text_from_pdf_bytes(self, file_content: bytes, filename: str, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Extract text from PDF file bytes
        
        Args:
            file_content: PDF file content as bytes
            filename: Original filename for logging
            force_ocr: If True, skip direct text extraction and use OCR
            
        Returns:
            Dict with success, message, data (extracted text), error, and method_used fields
        """
        if not self.is_service_available():
            return {
                "success": False,
                "message": "No PDF text extraction libraries available",
                "error": "NO_EXTRACTION_LIBRARIES",
                "data": None,
                "method_used": None
            }
        
        temp_file_path = None
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # Try direct text extraction first (unless forced to use OCR)
            if not force_ocr and self.pdf_reader_available:
                result = self._extract_text_directly(temp_file_path, filename)
                if result["success"] and result["data"] and result["data"].strip():
                    return result
            
            # Fallback to OCR if direct extraction failed or was forced
            if self.ocr_available:
                return self._extract_text_with_ocr(temp_file_path, filename)
            else:
                return {
                    "success": False,
                    "message": f"Direct text extraction failed and OCR not available for {filename}",
                    "error": "OCR_NOT_AVAILABLE",
                    "data": None,
                    "method_used": "none"
                }
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text from {filename}",
                "error": str(e),
                "data": None,
                "method_used": None
            }
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def extract_text_from_pdf_file(self, pdf_path: str, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Extract text from PDF file path
        
        Args:
            pdf_path: Path to the PDF file
            force_ocr: If True, skip direct text extraction and use OCR
            
        Returns:
            Dict with success, message, data (extracted text), error, and method_used fields
        """
        if not self.is_service_available():
            return {
                "success": False,
                "message": "No PDF text extraction libraries available",
                "error": "NO_EXTRACTION_LIBRARIES",
                "data": None,
                "method_used": None
            }
        
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "message": f"PDF file not found: {pdf_path}",
                "error": "FILE_NOT_FOUND",
                "data": None,
                "method_used": None
            }
        
        try:
            filename = os.path.basename(pdf_path)
            
            # Try direct text extraction first (unless forced to use OCR)
            if not force_ocr and self.pdf_reader_available:
                result = self._extract_text_directly(pdf_path, filename)
                if result["success"] and result["data"] and result["data"].strip():
                    return result
                else:
                    print(f"📄 Direct text extraction failed or returned empty text for {filename}")
            
            # Fallback to OCR if direct extraction failed or was forced
            if self.ocr_available:
                print(f"🔄 Falling back to OCR for {filename}")
                return self._extract_text_with_ocr(pdf_path, filename)
            else:
                return {
                    "success": False,
                    "message": f"Direct text extraction failed and OCR not available for {filename}",
                    "error": "OCR_NOT_AVAILABLE",
                    "data": None,
                    "method_used": "none"
                }
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract text from {pdf_path}",
                "error": str(e),
                "data": None,
                "method_used": None
            }
    
    def _extract_text_directly(self, pdf_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract text directly from PDF using PyPDF2
        
        Args:
            pdf_path: Path to the PDF file
            filename: Filename for logging
            
        Returns:
            Dict with extraction result
        """
        try:
            print(f"📄 Extracting text directly from: {filename}")
            
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                print(f"📖 PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        print(f"✅ Page {page_num + 1}: {len(page_text)} characters")
                    else:
                        print(f"⚠️  Page {page_num + 1}: No text found")
            
            extracted_text = text.strip()
            
            if extracted_text:
                print(f"🎉 Direct extraction successful: {len(extracted_text)} total characters")
                return {
                    "success": True,
                    "message": f"Successfully extracted text directly from {filename}",
                    "data": extracted_text,
                    "error": None,
                    "method_used": "direct"
                }
            else:
                return {
                    "success": False,
                    "message": f"No text found in {filename} using direct extraction",
                    "error": "NO_TEXT_FOUND",
                    "data": None,
                    "method_used": "direct"
                }
                
        except Exception as e:
            print(f"❌ Direct text extraction failed: {str(e)}")
            return {
                "success": False,
                "message": f"Direct text extraction failed for {filename}",
                "error": str(e),
                "data": None,
                "method_used": "direct"
            }
    
    def _extract_text_with_ocr(self, pdf_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR (for scanned/image PDFs)
        
        Args:
            pdf_path: Path to the PDF file
            filename: Filename for logging
            
        Returns:
            Dict with extraction result
        """
        try:
            print(f"🔍 Using OCR to extract text from: {filename}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            print(f"📄 PDF converted to {len(images)} image(s)")
            
            text = ""
            for i, image in enumerate(images):
                print(f"📄 Processing page {i+1}/{len(images)} with OCR...")
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text += page_text + "\n"
                    print(f"✅ Page {i+1}: extracted {len(page_text)} characters")
                else:
                    print(f"⚠️  Page {i+1}: no text extracted")
            
            extracted_text = text.strip()
            print(f"🎉 Total OCR extraction: {len(extracted_text)} characters")
            
            if extracted_text:
                return {
                    "success": True,
                    "message": f"Successfully extracted text using OCR from {filename}",
                    "data": extracted_text,
                    "error": None,
                    "method_used": "ocr"
                }
            else:
                return {
                    "success": False,
                    "message": f"No text found in {filename} using OCR",
                    "error": "NO_TEXT_FOUND",
                    "data": None,
                    "method_used": "ocr"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"OCR extraction failed for {filename}",
                "error": str(e),
                "data": None,
                "method_used": "ocr"
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about PDF text service status
        """
        info = {
            "service_available": self.is_service_available(),
            "direct_extraction_available": self.pdf_reader_available,
            "ocr_available": self.ocr_available,
            "preferred_method": "direct" if self.pdf_reader_available else "ocr" if self.ocr_available else "none"
        }
        
        if self.pdf_reader_available:
            try:
                import PyPDF2
                info["pypdf2_version"] = PyPDF2.__version__
            except:
                info["pypdf2_version"] = "unknown"
        
        if self.ocr_available:
            try:
                import pytesseract
                info["tesseract_version"] = str(pytesseract.get_tesseract_version())
            except:
                info["tesseract_version"] = "unknown"
        
        if not self.is_service_available():
            info["required_packages"] = []
            if not self.pdf_reader_available:
                info["required_packages"].append("PyPDF2")
            if not self.ocr_available:
                info["required_packages"].extend(["pytesseract", "pdf2image"])
            info["install_command"] = f"pip install {' '.join(info['required_packages'])}"
        
        return info

# Global PDF text service instance
pdf_text_service = PDFTextService()
