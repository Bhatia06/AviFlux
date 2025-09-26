#!/usr/bin/env python3
"""
Debug script for authentication token issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service
from models.auth_models import LoginResponse

def test_auth_service():
    """Test the auth service initialization and basic functionality"""
    print("=== AviFlux Auth Service Debug ===")
    
    # Check environment variables
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_ANON_KEY: {'Set' if os.getenv('SUPABASE_ANON_KEY') else 'Not Set'}")
    print(f"SUPABASE_JWT_SECRET: {'Set' if os.getenv('SUPABASE_JWT_SECRET') else 'Not Set'}")
    
    # Test auth service initialization
    try:
        print(f"\nAuth service initialized: {auth_service is not None}")
        print(f"Supabase client: {auth_service.supabase is not None}")
    except Exception as e:
        print(f"Auth service initialization failed: {e}")
        return
    
    # Test OAuth URL generation
    try:
        oauth_url = auth_service.generate_oauth_url("http://localhost:3000/callback")
        print(f"\nOAuth URL generated: {oauth_url.success}")
        if oauth_url.success:
            print(f"URL: {oauth_url.auth_url}")
        else:
            print(f"Error: {oauth_url.error}")
    except Exception as e:
        print(f"OAuth URL generation failed: {e}")
    
    # Test with dummy tokens (this will likely fail, but we can see the error)
    try:
        print("\nTesting OAuth callback with dummy tokens...")
        # Create a dummy JWT token with proper format (header.payload.signature)
        dummy_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = auth_service.handle_oauth_callback(dummy_jwt, "dummy_refresh_token")
        print(f"Result: {result}")
    except Exception as e:
        print(f"OAuth callback test failed (expected): {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    test_auth_service()
