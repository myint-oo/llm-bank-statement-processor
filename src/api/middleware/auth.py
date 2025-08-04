"""
Authentication middleware for API security
This ensures only your Laravel app can access the API
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config.settings import settings

# Create security scheme - this will expect a Bearer token in the header
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify that the API key in the request matches our configured API key
    
    How Laravel will use this:
    - Add header: Authorization: Bearer your-api-key-here
    - This function checks if the key matches what's in .env
    """
    if credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Alternative simpler API key check via header
async def verify_simple_api_key(api_key: str):
    """
    Simple API key verification for easier Laravel integration
    Laravel can send: X-API-Key: your-api-key-here
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True
