#!/usr/bin/env python3
"""
Test endpoint for token validation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service
from models.auth_models import TokenValidationResponse

app = FastAPI()
security = HTTPBearer()

@app.get("/test-token")
async def test_token_validation(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test endpoint for token validation"""
    token = credentials.credentials
    
    # Get detailed validation response
    validation_response = auth_service.validate_token(token)
    
    return {
        "token_received": bool(token),
        "token_length": len(token) if token else 0,
        "validation_result": {
            "valid": validation_response.valid,
            "error": validation_response.error,
            "user_email": validation_response.user.email if validation_response.user else None
        }
    }

@app.get("/test-token-raw")
async def test_token_raw(token: str):
    """Test endpoint for raw token validation (for debugging)"""
    validation_response = auth_service.validate_token(token)
    
    return {
        "token": token,
        "validation_result": {
            "valid": validation_response.valid,
            "error": validation_response.error,
            "user_email": validation_response.user.email if validation_response.user else None
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
