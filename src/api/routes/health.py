"""
Health Routes - Health check and monitoring endpoints
"""
from fastapi import APIRouter
from src.api.controllers.health_controller import HealthController
from src.api.schemas.responses import APIResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", response_model=HealthResponse)
def health_check():
    """Basic health check endpoint"""
    return HealthController.health_check()

@router.get("/detailed", response_model=APIResponse)
def detailed_health_check():
    """Detailed health check with comprehensive information"""
    return HealthController.detailed_health_check()
