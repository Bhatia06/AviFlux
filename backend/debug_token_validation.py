#!/usr/bin/env python3
"""
Debug script for token validation issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service
from models.auth_models import TokenValidationResponse

def test_token_validation():
    """Test token validation with different scenarios"""
    print("=== Token Validation Debug ===")
    
    # Test 1: Empty token
    print("\n1. Testing empty token...")
    result = auth_service.validate_token("")
    print(f"Empty token result: valid={result.valid}, error='{result.error}'")
    
    # Test 2: Invalid format token
    print("\n2. Testing invalid format token...")
    result = auth_service.validate_token("invalid_token")
    print(f"Invalid format result: valid={result.valid}, error='{result.error}'")
    
    # Test 3: Valid JWT format but invalid token
    print("\n3. Testing valid JWT format but invalid token...")
    dummy_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    result = auth_service.validate_token(dummy_jwt)
    print(f"Valid JWT format result: valid={result.valid}, error='{result.error}'")
    
    # Test 4: Check JWT secret availability
    print(f"\n4. JWT Secret available: {'Yes' if auth_service.jwt_secret else 'No'}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    test_token_validation()
