#!/usr/bin/env python3
"""
API Startup Script
This script starts the Bank Statement Processor API server
"""
import sys
import os
import uvicorn

# Add the project root to Python path so imports work
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.config.settings import settings

def main():
    """
    Start the API server
    """
    print(f"🚀 Starting {settings.API_TITLE}")
    print(f"📍 Server will run on: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📝 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🔑 API Key: {settings.API_KEY}")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

if __name__ == "__main__":
    main()
