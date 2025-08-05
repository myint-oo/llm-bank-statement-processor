"""
Bank Statement Service - Business logic for processing bank statements
Moved to app layer for better organization
"""
import json
import time
from typing import Dict, Any, Optional
from src.app.BankStatement.processor import BankStatementProcessor
from src.app.services.pdf_text_service import pdf_text_service

class BankStatementService:
    """
    Service class that handles bank statement processing business logic
    """
    
    def __init__(self):
        """
        Initialize the service with the bank statement processor
        """
        self.processor = None
        self._initialize_processor()
    
    def _initialize_processor(self):
        """
        Initialize the bank statement processor
        """
        try:
            print("🔄 Initializing AI model...")
            self.processor = BankStatementProcessor()
            print("✅ AI model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load AI model: {str(e)}")
            self.processor = None
    
    def is_model_ready(self) -> bool:
        """
        Check if the AI model is loaded and ready
        """
        return self.processor is not None
    
    def is_pdf_service_ready(self) -> bool:
        """
        Check if PDF text extraction service is available
        """
        return pdf_text_service.is_service_available()
    
    def process_text(self, text_content: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process bank statement text and return structured data
        """
        if not self.processor:
            return {
                "success": False,
                "message": "AI model not loaded",
                "error": "MODEL_NOT_LOADED",
                "data": None
            }
        
        if not text_content or not text_content.strip():
            return {
                "success": False,
                "message": "Empty text content provided",
                "error": "TEXT_EMPTY",
                "data": None
            }
        
        try:
            start_time = time.time()
            
            print(f"🔄 Processing bank statement for customer: {customer_id or 'unknown'}")
            result = self.processor.process(text_content)
            
            processing_time = time.time() - start_time

            return {
                "success": True,
                "message": f"Bank statement processed successfully in {processing_time:.2f} seconds",
                "data": result,
                "error": None
            }
            
            try:
                parsed_result = json.loads(result)
                parsed_result["processed_at"] = time.time()
                parsed_result["processing_time_seconds"] = round(processing_time, 2)
                
                if not self._validate_result_structure(parsed_result):
                    return {
                        "success": False,
                        "message": "AI model returned invalid data structure",
                        "error": "INVALID_AI_OUTPUT",
                        "data": None
                    }
                
                return {
                    "success": True,
                    "message": f"Bank statement processed successfully in {processing_time:.2f} seconds",
                    "data": parsed_result,
                    "error": None
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse AI model output as JSON: {e}")
                return {
                    "success": False,
                    "message": "AI model returned invalid JSON",
                    "error": "INVALID_JSON_OUTPUT",
                    "data": None
                }
                
        except Exception as e:
            print(f"❌ Error processing bank statement: {str(e)}")
            return {
                "success": False,
                "message": "Failed to process bank statement",
                "error": str(e),
                "data": None
            }
    
    def process_file(self, file_content: bytes, filename: str, customer_id: Optional[str] = None, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Process a PDF file and return structured data
        """
        if not self.processor:
            return {
                "success": False,
                "message": "AI model not loaded",
                "error": "MODEL_NOT_LOADED",
                "data": None
            }
        
        if not pdf_text_service.is_service_available():
            return {
                "success": False,
                "message": "PDF text extraction service not available",
                "error": "PDF_SERVICE_NOT_AVAILABLE",
                "data": None
            }
        
        try:
            print(f"🔄 Extracting text from PDF: {filename}")
            extraction_result = pdf_text_service.extract_text_from_pdf_bytes(file_content, filename, force_ocr)
            
            if not extraction_result["success"]:
                return extraction_result
            
            extracted_text = extraction_result["data"]
            extraction_method = extraction_result.get("method_used", "unknown")
            
            print(f"✅ Text extracted using {extraction_method} method")
            
            result = self.process_text(extracted_text, customer_id)
            
            if result["success"] and result["data"]:
                result["data"]["extraction_method"] = extraction_method
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing PDF file: {str(e)}")
            return {
                "success": False,
                "message": "Failed to process PDF file",
                "error": str(e),
                "data": None
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status information
        """
        model_ready = self.is_model_ready()
        pdf_service_ready = self.is_pdf_service_ready()
        
        return {
            "status": "healthy" if (model_ready and pdf_service_ready) else "degraded",
            "model_loaded": model_ready,
            "pdf_service_available": pdf_service_ready,
            "api_status": "running",
            "model_status": "loaded" if model_ready else "not_loaded",
            "pdf_service_status": "available" if pdf_service_ready else "not_available"
        }
    
    def _validate_result_structure(self, result: Dict[str, Any]) -> bool:
        """
        Validate that the AI model returned the expected data structure
        """
        required_fields = ["bank_name", "statement_period", "accounts"]
        
        for field in required_fields:
            if field not in result:
                print(f"❌ Missing required field: {field}")
                return False
        
        if not isinstance(result.get("statement_period"), dict):
            return False
        
        period = result["statement_period"]
        if "start_date" not in period or "end_date" not in period:
            return False
        
        if not isinstance(result.get("accounts"), list):
            return False
        
        return True

# Global service instance
bank_statement_service = BankStatementService()
