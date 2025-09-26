#!/usr/bin/env python3
"""
AviFlux OAuth Login Backend Script

This script demonstrates how to use the Supabase OAuth authentication
system with Google for the AviFlux application.

Usage:
    python login_script.py
"""

import os
import sys
import asyncio
import aiohttp
import json
from dotenv import load_dotenv
from urllib.parse import parse_qs, urlparse

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service
from models.auth_models import AuthenticationError

# Load environment variables
load_dotenv()


class LoginBackendScript:
    """Backend script for handling OAuth login flow."""
    
    def __init__(self):
        """Initialize the login script."""
        self.api_base_url = "http://localhost:8000"  # Assuming FastAPI runs on port 8000
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
    async def start_oauth_flow(self) -> str:
        """
        Start the OAuth authentication flow.
        
        Returns:
            OAuth authentication URL for user to visit
        """
        try:
            print("🚀 Starting OAuth authentication flow...")
            
            # Generate OAuth URL
            oauth_response = auth_service.generate_oauth_url(
                provider="google",
                redirect_to=f"{self.frontend_url}/auth/callback"
            )
            
            print(f"✅ OAuth URL generated successfully!")
            print(f"🔗 Authentication URL: {oauth_response.auth_url}")
            print("\n📋 Instructions:")
            print("1. Copy the URL above and paste it in your web browser")
            print("2. Complete the Google OAuth login process")
            print("3. You will be redirected to your frontend application")
            print("4. The frontend should handle the callback and extract tokens")
            
            return oauth_response.auth_url
            
        except Exception as e:
            print(f"❌ Failed to start OAuth flow: {e}")
            raise
    
    async def simulate_callback_handling(self, access_token: str, refresh_token: str):
        """
        Simulate handling OAuth callback with tokens.
        
        Args:
            access_token: OAuth access token from callback
            refresh_token: OAuth refresh token from callback
        """
        try:
            print("🔄 Processing OAuth callback...")
            
            # Handle OAuth callback
            login_response = auth_service.handle_oauth_callback(access_token, refresh_token)
            
            print("✅ OAuth callback processed successfully!")
            print(f"👤 User: {login_response.user.full_name} ({login_response.user.email})")
            print(f"🔐 Access Token: {login_response.tokens.access_token[:50]}...")
            print(f"🔄 Refresh Token: {login_response.tokens.refresh_token[:50]}...")
            print(f"⏰ Expires in: {login_response.tokens.expires_in} seconds")
            
            return login_response
            
        except AuthenticationError as e:
            print(f"❌ OAuth callback failed: {e}")
            raise
    
    async def validate_token(self, access_token: str):
        """
        Validate an access token.
        
        Args:
            access_token: JWT access token to validate
        """
        try:
            print("🔍 Validating access token...")
            
            validation_response = auth_service.validate_token(access_token)
            
            if validation_response.valid and validation_response.user:
                print("✅ Token is valid!")
                user = validation_response.user
                print(f"👤 User: {user.full_name} ({user.email})")
                print(f"🆔 User ID: {user.id}")
                print(f"🏢 Provider: {user.provider}")
            else:
                print(f"❌ Token validation failed: {validation_response.error}")
                
            return validation_response
            
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            raise
    
    async def refresh_user_token(self, refresh_token: str):
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
        """
        try:
            print("🔄 Refreshing access token...")
            
            refresh_response = auth_service.refresh_token(refresh_token)
            
            print("✅ Token refresh successful!")
            print(f"🔐 New Access Token: {refresh_response.tokens.access_token[:50]}...")
            print(f"🔄 New Refresh Token: {refresh_response.tokens.refresh_token[:50]}...")
            print(f"⏰ Expires in: {refresh_response.tokens.expires_in} seconds")
            
            return refresh_response
            
        except AuthenticationError as e:
            print(f"❌ Token refresh failed: {e}")
            raise
    
    async def test_protected_endpoint(self, access_token: str):
        """
        Test a protected API endpoint with access token.
        
        Args:
            access_token: Valid access token
        """
        try:
            print("🧪 Testing protected endpoint...")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/auth/protected", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Protected endpoint access successful!")
                        print(f"📝 Response: {json.dumps(data, indent=2)}")
                    else:
                        error_data = await response.text()
                        print(f"❌ Protected endpoint access failed: {response.status}")
                        print(f"📝 Error: {error_data}")
                        
        except Exception as e:
            print(f"❌ Protected endpoint test failed: {e}")
            raise
    
    def display_setup_instructions(self):
        """Display setup instructions for OAuth configuration."""
        print("📋 OAuth Setup Instructions:")
        print("=" * 50)
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to Authentication > Settings")
        print("3. Configure Google OAuth provider:")
        print("   - Enable Google provider")
        print("   - Add your Google OAuth client ID and secret")
        print("   - Set redirect URL to: http://localhost:3000/auth/callback")
        print("4. Update your .env file with Supabase credentials:")
        print("   - SUPABASE_URL=https://your-project-id.supabase.co")
        print("   - SUPABASE_ANON_KEY=your-anon-key")
        print("   - SUPABASE_SERVICE_KEY=your-service-key")
        print("5. Start your FastAPI server: python main.py")
        print("6. Run this script: python login_script.py")
        print("=" * 50)


async def main():
    """Main function to run the login script."""
    script = LoginBackendScript()
    
    print("🛡️ AviFlux OAuth Login Backend Script")
    print("=====================================")
    
    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY"):
        print("❌ Missing required environment variables!")
        script.display_setup_instructions()
        return
    
    print("✅ Environment variables configured")
    
    try:
        # Start OAuth flow
        auth_url = await script.start_oauth_flow()
        
        print("\n⏳ Waiting for manual OAuth completion...")
        print("After completing OAuth in browser, you can test token operations manually.")
        print("\nExample usage after getting tokens from OAuth callback:")
        print("- Copy access_token and refresh_token from callback")
        print("- Use script.validate_token(access_token)")
        print("- Use script.test_protected_endpoint(access_token)")
        print("- Use script.refresh_user_token(refresh_token)")
        
        # Interactive mode for testing with actual tokens
        while True:
            print("\n🎮 Interactive Mode Commands:")
            print("1. validate <access_token> - Validate access token")
            print("2. refresh <refresh_token> - Refresh token")
            print("3. test <access_token> - Test protected endpoint")
            print("4. oauth - Generate new OAuth URL")
            print("5. quit - Exit script")
            
            command = input("\n💻 Enter command: ").strip()
            
            if command == "quit":
                break
            elif command == "oauth":
                await script.start_oauth_flow()
            elif command.startswith("validate "):
                token = command.split(" ", 1)[1]
                await script.validate_token(token)
            elif command.startswith("refresh "):
                token = command.split(" ", 1)[1]
                await script.refresh_user_token(token)
            elif command.startswith("test "):
                token = command.split(" ", 1)[1]
                await script.test_protected_endpoint(token)
            else:
                print("❌ Unknown command. Please try again.")
        
    except KeyboardInterrupt:
        print("\n\n👋 Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())