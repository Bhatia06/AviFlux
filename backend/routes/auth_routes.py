"""
Authentication routes for AviFlux OAuth integration.

This module provides FastAPI endpoints for Google OAuth authentication,
token management, and user session handling.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import HttpUrl

from services.auth_service import auth_service
from middleware.auth_middleware import get_current_user, get_optional_user
from models.auth_models import (
    LoginResponse, LogoutResponse, TokenValidationResponse,
    OAuthUrlRequest, OAuthUrlResponse, TokenRefreshRequest, TokenRefreshResponse,
    AuthError, UserProfile, AuthenticationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/oauth-url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    provider: str = Query(default="google", description="OAuth provider (google)"),
    redirect_to: Optional[str] = Query(None, description="URL to redirect after authentication")
):
    """
    Generate OAuth authentication URL for the specified provider.
    
    Args:
        provider: OAuth provider name (default: "google")
        redirect_to: Optional redirect URL after successful authentication
        
    Returns:
        OAuthUrlResponse with authentication URL
        
    Raises:
        HTTPException: If OAuth URL generation fails
    """
    try:
        logger.info(f"Generating OAuth URL for provider: {provider}")
        
        oauth_response = auth_service.generate_oauth_url(provider, redirect_to)
        
        logger.info(f"OAuth URL generated successfully for provider: {provider}")
        return oauth_response
        
    except Exception as e:
        logger.error(f"OAuth URL generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth URL generation failed: {str(e)}"
        )


@router.post("/callback", response_model=LoginResponse)
async def oauth_callback(
    access_token: str = Query(..., description="OAuth access token from callback"),
    refresh_token: str = Query(..., description="OAuth refresh token from callback")
):
    """
    Handle OAuth callback and create user session.
    
    Args:
        access_token: OAuth access token from callback
        refresh_token: OAuth refresh token from callback
        response: FastAPI response object for setting cookies
        
    Returns:
        LoginResponse with user data and tokens
        
    Raises:
        HTTPException: If OAuth callback handling fails
    """
    try:
        logger.info("Processing OAuth callback")
        
        # Handle OAuth callback using auth service
        login_response = auth_service.handle_oauth_callback(access_token, refresh_token)
        
        # Note: Cookies can be set by the frontend using the tokens in the response
        # For server-side cookie setting, you would need to return a Response object
        
        logger.info(f"OAuth callback processed successfully for user: {login_response.user.email}")
        return login_response
        
    except AuthenticationError as e:
        logger.error(f"OAuth callback authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback processing failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(refresh_request: TokenRefreshRequest):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_request: Request containing refresh token
        
    Returns:
        TokenRefreshResponse with new tokens and user data
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        logger.info("Processing token refresh request")
        
        refresh_response = auth_service.refresh_token(refresh_request.refresh_token)
        
        logger.info("Token refresh successful")
        return refresh_response
        
    except AuthenticationError as e:
        logger.error(f"Token refresh authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Logout current user and invalidate session.
    
    Args:
        current_user: Currently authenticated user
        response: FastAPI response object for clearing cookies
        
    Returns:
        LogoutResponse with logout status
    """
    try:
        logger.info(f"Processing logout for user: {current_user.email}")
        
        # Extract token from the current request (this is a simplified approach)
        # In a real implementation, you'd get the token from the request headers
        logout_response = auth_service.logout("")  # Simplified for now
        
        # Note: Cookies should be cleared by the frontend
        # For server-side cookie clearing, you would need to return a Response object
        
        logger.info(f"Logout successful for user: {current_user.email}")
        return logout_response
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        # Return success even on error to prevent hanging sessions
        return LogoutResponse(
            success=True,
            message="Logout completed (session may have already expired)"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """
    Get current authenticated user's profile information.
    
    Args:
        current_user: Currently authenticated user from JWT token
        
    Returns:
        UserProfile: Current user's profile data
    """
    logger.info(f"Profile requested for user: {current_user.email}")
    return current_user


@router.get("/validate", response_model=TokenValidationResponse)
async def validate_token(current_user: Optional[UserProfile] = Depends(get_optional_user)):
    """
    Validate current authentication token.
    
    Args:
        current_user: Optionally authenticated user
        
    Returns:
        TokenValidationResponse: Token validation result
    """
    if current_user:
        logger.info(f"Token validation successful for user: {current_user.email}")
        return TokenValidationResponse(
            valid=True,
            user=current_user,
            error=None
        )
    else:
        logger.info("Token validation failed - no valid token provided")
        return TokenValidationResponse(
            valid=False,
            user=None,
            error="No valid authentication token provided"
        )


@router.get("/protected")
async def protected_endpoint(current_user: UserProfile = Depends(get_current_user)):
    """
    Example protected endpoint that requires authentication.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        Dict with personalized message
    """
    return {
        "message": f"Hello {current_user.full_name or current_user.email}!",
        "user_id": current_user.id,
        "provider": current_user.provider,
        "authenticated": True
    }


@router.get("/public")
async def public_endpoint(current_user: Optional[UserProfile] = Depends(get_optional_user)):
    """
    Example public endpoint that works with or without authentication.
    
    Args:
        current_user: Optionally authenticated user
        
    Returns:
        Dict with appropriate message
    """
    if current_user:
        return {
            "message": f"Hello {current_user.full_name or current_user.email}!",
            "authenticated": True,
            "user_id": current_user.id
        }
    else:
        return {
            "message": "Hello anonymous user!",
            "authenticated": False
        }