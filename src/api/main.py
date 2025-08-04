"""
Main FastAPI application
This is the entry point for your API server
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.config.settings import settings
from src.api.routes import router

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",  # Interactive API documentation at /docs
    redoc_url="/redoc"  # Alternative API documentation at /redoc
)

# Add CORS middleware to allow Laravel to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure this for production
)

# Register routes
app.include_router(router)

@app.get("/")
async def root():
    """
    Root endpoint - basic API information
    Note: This is overridden by the web router's root endpoint
    """
    return {
        "message": "API is running",
        "docs": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    """
    This runs when the API starts up
    """
    print(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"📝 API Documentation available at: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🏥 Health check available at: http://{settings.API_HOST}:{settings.API_PORT}/health/")

@app.on_event("shutdown")
async def shutdown_event():
    """
    This runs when the API shuts down
    """
    print("🛑 Shutting down API...")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch any unhandled errors and return a consistent JSON response
    """
    print(f"❌ Unhandled error: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail={
            "success": False,
            "message": "Internal server error",
            "error": "INTERNAL_ERROR"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True  # Auto-reload on code changes (for development)
    )
