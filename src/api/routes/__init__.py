"""
Routes Package - Auto-register all route files
This automatically discovers and imports all route files in this directory
"""
import os
import importlib
from pathlib import Path
from fastapi import APIRouter

def auto_register_routes():
    """
    Automatically discover and register all route files in this directory
    Each route file should have a 'router' variable that will be included
    """
    main_router = APIRouter()
    
    # Get the current directory (routes folder)
    routes_dir = Path(__file__).parent
    
    # Get all Python files in this directory except __init__.py
    route_files = [
        f.stem for f in routes_dir.glob("*.py") 
        if f.is_file() and f.stem != "__init__"
    ]
    
    # Import each route file and include its router
    for route_file in route_files:
        try:
            # Import the module dynamically
            module = importlib.import_module(f"src.api.routes.{route_file}")
            
            # Check if the module has a router
            if hasattr(module, 'router'):
                main_router.include_router(module.router)
                print(f"✅ Registered routes from: {route_file}.py")
            else:
                print(f"⚠️  No router found in: {route_file}.py")
                
        except Exception as e:
            print(f"❌ Failed to import {route_file}.py: {e}")
    
    return main_router

# Create the main router with all auto-registered routes
router = auto_register_routes()

# Export for main.py to import
__all__ = ["router"]
