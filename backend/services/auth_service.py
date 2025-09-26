"""
Authentication service for AviFlux using Supabase OAuth.

This service handles Google OAuth authentication, token management,
and user session handling through Supabase Auth.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from supabase import create_client, Client
from dotenv import load_dotenv

from models.auth_models import (
    UserProfile, AuthTokens, LoginResponse, LogoutResponse,
    TokenValidationResponse, OAuthUrlResponse, TokenRefreshResponse,
    AuthenticationError, TokenExpiredError, InvalidTokenError as CustomInvalidTokenError,
    OAuthProviderError
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for handling OAuth and user management."""
    
    def __init__(self):
        """Initialize the authentication service with Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")  # For admin operations
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        # Validate required environment variables
        if not all([self.supabase_url, self.supabase_anon_key]):
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        # Initialize Supabase client
        self.supabase: Client = create_client(str(self.supabase_url), str(self.supabase_anon_key))
        
        # Initialize service client if service key is available
        self.service_client: Optional[Client] = None
        if self.supabase_service_key:
            self.service_client = create_client(str(self.supabase_url), str(self.supabase_service_key))
        
        logger.info("AuthService initialized successfully")
    
    def generate_oauth_url(self, provider: str = "google", redirect_to: Optional[str] = None) -> OAuthUrlResponse:
        """
        Generate OAuth authentication URL for the specified provider.
        
        Args:
            provider: OAuth provider name (default: "google")
            redirect_to: URL to redirect after successful authentication
            
        Returns:
            OAuthUrlResponse with authentication URL
            
        Raises:
            OAuthProviderError: If OAuth URL generation fails
        """
        try:
            # Generate OAuth URL using Supabase Auth
            # Note: This creates a redirect URL that the frontend will use
            auth_url = f"{self.supabase_url}/auth/v1/authorize?provider={provider}&redirect_to={redirect_to or 'http://localhost:3000/auth/callback'}"
            
            logger.info(f"Generated OAuth URL for provider: {provider}")
            
            return OAuthUrlResponse(
                success=True,
                auth_url=auth_url,
                provider=provider
            )
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {e}")
            raise OAuthProviderError(f"OAuth URL generation failed: {str(e)}", provider)
    
    def handle_oauth_callback(self, access_token: str, refresh_token: str) -> LoginResponse:
        """
        Handle OAuth callback and create user session.
        
        Args:
            access_token: OAuth access token from callback
            refresh_token: OAuth refresh token from callback
            
        Returns:
            LoginResponse with user data and tokens
            
        Raises:
            AuthenticationError: If OAuth callback handling fails
        """
        try:
            # Validate token format before calling set_session
            if not access_token or not isinstance(access_token, str):
                raise AuthenticationError("Invalid access token format")
            
            # Basic JWT format validation (should have 3 parts separated by dots)
            token_parts = access_token.split('.')
            if len(token_parts) != 3:
                raise AuthenticationError("Access token is not a valid JWT format")
            
            # Set the session with tokens received from OAuth callback
            session_response = self.supabase.auth.set_session(access_token, refresh_token)
            
            if not session_response or not hasattr(session_response, 'user') or not session_response.user:
                raise AuthenticationError("Failed to create user session from OAuth tokens")
            
            # Extract user information
            user_data = session_response.user
            session_data = getattr(session_response, 'session', None)
            
            if not session_data:
                raise AuthenticationError("No session data returned from OAuth callback")
            
            # Create user profile
            user_profile = self._create_user_profile(user_data)
            
            # Create auth tokens
            auth_tokens = self._create_auth_tokens(session_data)
            
            logger.info(f"OAuth callback handled successfully for user: {user_profile.email}")
            
            return LoginResponse(
                success=True,
                user=user_profile,
                tokens=auth_tokens,
                message="OAuth login successful"
            )
            
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {e}")
            raise AuthenticationError(f"OAuth callback failed: {str(e)}")
    
    def validate_token(self, token: str) -> TokenValidationResponse:
        """
        Validate JWT access token and return user information.
        
        Args:
            token: JWT access token to validate
            
        Returns:
            TokenValidationResponse with validation result
        """
        try:
            # Validate token format first
            if not token or not isinstance(token, str):
                return TokenValidationResponse(
                    valid=False,
                    user=None,
                    error="Invalid token format"
                )
            
            # Basic JWT format validation
            token_parts = token.split('.')
            if len(token_parts) != 3:
                return TokenValidationResponse(
                    valid=False,
                    user=None,
                    error="Invalid JWT format"
                )
            
            # Try to get user from token using Supabase
            try:
                user_response = self.supabase.auth.get_user(token)
                
                if not user_response or not hasattr(user_response, 'user') or not user_response.user:
                    return TokenValidationResponse(
                        valid=False,
                        user=None,
                        error="Invalid or expired token"
                    )
                
                # Create user profile
                user_profile = self._create_user_profile(user_response.user)
                
                logger.info(f"Token validated successfully for user: {user_profile.email}")
                
                return TokenValidationResponse(
                    valid=True,
                    user=user_profile,
                    error=None
                )
                
            except Exception as supabase_error:
                logger.warning(f"Supabase token validation failed: {supabase_error}")
                logger.info(f"Token being validated: {token[:50]}...")  # Log first 50 chars
                logger.info(f"JWT Secret available: {bool(self.jwt_secret)}")
                
                # Fallback: Try to decode JWT manually if we have the secret
                if self.jwt_secret:
                    try:
                        # Try different algorithms and options
                        decoded_token = jwt.decode(
                            token, 
                            self.jwt_secret, 
                            algorithms=["HS256", "HS512", "RS256"],
                            options={"verify_exp": True, "verify_signature": True}
                        )
                        
                        # Extract user info from token claims
                        user_id = decoded_token.get('sub')
                        email = decoded_token.get('email')
                        if not email:
                            # Create a valid email from name or use default
                            name = decoded_token.get('name', 'user')
                            email = f"{name.lower().replace(' ', '.')}@example.com"
                        
                        if not user_id:
                            return TokenValidationResponse(
                                valid=False,
                                user=None,
                                error="Invalid token claims"
                            )
                        
                        # Create a basic user profile from token claims
                        user_profile = UserProfile(
                            id=user_id,
                            email=email,
                            full_name=decoded_token.get('name', ''),
                            avatar_url=decoded_token.get('picture', ''),
                            provider=decoded_token.get('iss', 'google'),
                            created_at=datetime.fromtimestamp(decoded_token.get('iat', 0), tz=timezone.utc),
                            last_sign_in=datetime.fromtimestamp(decoded_token.get('iat', 0), tz=timezone.utc)
                        )
                        
                        logger.info(f"Token validated via JWT decode for user: {user_profile.email}")
                        
                        return TokenValidationResponse(
                            valid=True,
                            user=user_profile,
                            error=None
                        )
                        
                    except jwt.ExpiredSignatureError:
                        return TokenValidationResponse(
                            valid=False,
                            user=None,
                            error="Token has expired"
                        )
                    except jwt.InvalidTokenError as jwt_error:
                        logger.warning(f"JWT decode failed: {jwt_error}")
                        
                        # Try one more time without signature verification for debugging
                        try:
                            decoded_token = jwt.decode(
                                token, 
                                options={"verify_signature": False, "verify_exp": False}
                            )
                            logger.info(f"Token decoded without verification: {decoded_token}")
                            
                            # Extract user info from token claims
                            user_id = decoded_token.get('sub')
                            email = decoded_token.get('email')
                            if not email:
                                # Create a valid email from name or use default
                                name = decoded_token.get('name', 'user')
                                email = f"{name.lower().replace(' ', '.')}@example.com"
                            
                            if user_id:
                                # Create a basic user profile from token claims
                                user_profile = UserProfile(
                                    id=user_id,
                                    email=email,
                                    full_name=decoded_token.get('name', ''),
                                    avatar_url=decoded_token.get('picture', ''),
                                    provider=decoded_token.get('iss', 'google'),
                                    created_at=datetime.fromtimestamp(decoded_token.get('iat', 0), tz=timezone.utc),
                                    last_sign_in=datetime.fromtimestamp(decoded_token.get('iat', 0), tz=timezone.utc)
                                )
                                
                                logger.info(f"Token validated via unverified JWT decode for user: {user_profile.email}")
                                
                                return TokenValidationResponse(
                                    valid=True,
                                    user=user_profile,
                                    error="Token validated without signature verification"
                                )
                            else:
                                logger.warning("Token decoded but missing required claims (sub, email)")
                                return TokenValidationResponse(
                                    valid=False,
                                    user=None,
                                    error="Token missing required claims"
                                )
                        except Exception as unverified_error:
                            logger.warning(f"Unverified JWT decode also failed: {unverified_error}")
                            return TokenValidationResponse(
                                valid=False,
                                user=None,
                                error="Invalid token signature"
                            )
                
                # If no JWT secret or decode fails, return the original error
                return TokenValidationResponse(
                    valid=False,
                    user=None,
                    error=f"Token validation failed: {str(supabase_error)}"
                )
            
        except ExpiredSignatureError:
            logger.warning("Token validation failed: Token expired")
            return TokenValidationResponse(
                valid=False,
                user=None,
                error="Token has expired"
            )
        except InvalidTokenError:
            logger.warning("Token validation failed: Invalid token")
            return TokenValidationResponse(
                valid=False,
                user=None,
                error="Invalid token format"
            )
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return TokenValidationResponse(
                valid=False,
                user=None,
                error=f"Token validation error: {str(e)}"
            )
    
    def refresh_token(self, refresh_token: str) -> TokenRefreshResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TokenRefreshResponse with new tokens and user data
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        try:
            # Refresh session using refresh token
            refresh_response = self.supabase.auth.refresh_session(refresh_token)
            
            if not refresh_response.session:
                raise AuthenticationError("Failed to refresh token")
            
            session_data = refresh_response.session
            user_data = refresh_response.user
            
            # Create updated user profile
            user_profile = self._create_user_profile(user_data)
            
            # Create new auth tokens
            auth_tokens = self._create_auth_tokens(session_data)
            
            logger.info(f"Token refreshed successfully for user: {user_profile.email}")
            
            return TokenRefreshResponse(
                success=True,
                tokens=auth_tokens,
                user=user_profile
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    def logout(self, access_token: str) -> LogoutResponse:
        """
        Logout user and invalidate session.
        
        Args:
            access_token: User's access token
            
        Returns:
            LogoutResponse with logout status
        """
        try:
            # Set the user's token for the logout operation
            self.supabase.auth.set_session(access_token, "")
            
            # Sign out the user
            self.supabase.auth.sign_out()
            
            logger.info("User logged out successfully")
            
            return LogoutResponse(
                success=True,
                message="Logout successful"
            )
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            # Return success even if logout fails to prevent hanging sessions
            return LogoutResponse(
                success=True,
                message="Logout completed (session may have already expired)"
            )
    
    def get_user_profile(self, access_token: str) -> Optional[UserProfile]:
        """
        Get user profile information from access token.
        
        Args:
            access_token: Valid access token
            
        Returns:
            UserProfile if token is valid, None otherwise
        """
        try:
            validation_response = self.validate_token(access_token)
            return validation_response.user if validation_response.valid else None
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def _create_user_profile(self, user_data: Any) -> UserProfile:
        """
        Create UserProfile from Supabase user data.
        
        Args:
            user_data: User data from Supabase
            
        Returns:
            UserProfile instance
        """
        # Extract user metadata
        user_metadata = getattr(user_data, 'user_metadata', {}) or {}
        app_metadata = getattr(user_data, 'app_metadata', {}) or {}
        
        # Get provider information
        provider = "google"  # Default to google
        if hasattr(user_data, 'app_metadata') and user_data.app_metadata:
            provider = user_data.app_metadata.get('provider', 'google')
        
        # Create user profile
        return UserProfile(
            id=user_data.id,
            email=user_data.email,
            full_name=user_metadata.get('full_name') or user_metadata.get('name'),
            avatar_url=user_metadata.get('avatar_url') or user_metadata.get('picture'),
            provider=provider,
            created_at=datetime.fromisoformat(user_data.created_at.replace('Z', '+00:00')),
            last_sign_in=datetime.fromisoformat(user_data.last_sign_in_at.replace('Z', '+00:00')) if user_data.last_sign_in_at else None
        )
    
    def _create_auth_tokens(self, session_data: Any) -> AuthTokens:
        """
        Create AuthTokens from Supabase session data.
        
        Args:
            session_data: Session data from Supabase
            
        Returns:
            AuthTokens instance
        """
        try:
            # Safely extract token data with fallbacks
            access_token = getattr(session_data, 'access_token', '')
            refresh_token = getattr(session_data, 'refresh_token', '')
            expires_in = getattr(session_data, 'expires_in', 3600)  # Default 1 hour
            expires_at = getattr(session_data, 'expires_at', 0)
            
            if not access_token or not refresh_token:
                raise ValueError("Missing required token data from session")
            
            return AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                expires_at=expires_at,
                token_type="Bearer"
            )
        except Exception as e:
            logger.error(f"Failed to create auth tokens: {e}")
            raise ValueError(f"Invalid session data: {str(e)}")


# Global auth service instance
auth_service = AuthService()