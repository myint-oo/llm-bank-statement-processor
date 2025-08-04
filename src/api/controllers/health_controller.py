"""
Health Controller - Handles health check endpoints
"""
from src.app.services.bank_statement_service import bank_statement_service
from src.app.services.pdf_text_service import pdf_text_service
from src.config.settings import settings
from datetime import datetime

class HealthController:
    """
    Controller for health check endpoints
    """
    
    @staticmethod
    def health_check():
        """
        Basic health check
        """
        health_status = bank_statement_service.get_health_status()
        
        return {
            "status": health_status["status"],
            "model_loaded": health_status["model_loaded"],
            "version": settings.API_VERSION,
            "timestamp": datetime.now()
        }
    
    @staticmethod
    def detailed_health_check():
        """
        Detailed health check with more information
        """
        health_status = bank_statement_service.get_health_status()
        pdf_service_info = pdf_text_service.get_service_info()
        
        health_data = {
            "api_status": health_status["api_status"],
            "model_status": health_status["model_status"],
            "pdf_service_status": health_status["pdf_service_status"],
            "model_name": settings.BASE_MODEL,
            "pdf_service_info": pdf_service_info,
            "version": settings.API_VERSION,
        }
        
        return {
            "success": True,
            "message": "API is running",
            "data": health_data
        }
