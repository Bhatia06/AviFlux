"""
Authentication data models and DTOs for AviFlux OAuth integration.

This module contains Pydantic models for handling authentication data,
including user information, tokens, and OAuth responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


class UserProfile(BaseModel):
    """User profile data from Supabase Auth."""
    id: str = Field(..., description="Unique user identifier from Supabase")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name from OAuth provider")
    avatar_url: Optional[str] = Field(None, description="User's profile picture URL")
    provider: str = Field(..., description="OAuth provider (e.g., 'google')")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_sign_in: Optional[datetime] = Field(None, description="Last successful login")


class AuthTokens(BaseModel):
    """Authentication tokens returned by Supabase."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token for token renewal")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: int = Field(..., description="Token expiration timestamp")
    token_type: str = Field(default="Bearer", description="Token type")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    success: bool = Field(True, description="Login success status")
    user: UserProfile = Field(..., description="User profile information")
    tokens: AuthTokens = Field(..., description="Authentication tokens")
    message: str = Field(default="Login successful", description="Response message")


class LogoutResponse(BaseModel):
    """Response model for logout operation."""
    success: bool = Field(True, description="Logout success status")
    message: str = Field(default="Logout successful", description="Response message")


class TokenValidationResponse(BaseModel):
    """Response model for token validation."""
    valid: bool = Field(..., description="Token validity status")
    user: Optional[UserProfile] = Field(None, description="User data if token is valid")
    error: Optional[str] = Field(None, description="Error message if token is invalid")


class AuthError(BaseModel):
    """Error response model for authentication failures."""
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class OAuthUrlRequest(BaseModel):
    """Request model for OAuth URL generation."""
    provider: str = Field(..., description="OAuth provider name (e.g., 'google')")
    redirect_to: Optional[str] = Field(None, description="URL to redirect after authentication")


class OAuthUrlResponse(BaseModel):
    """Response model for OAuth URL generation."""
    success: bool = Field(True, description="URL generation success status")
    auth_url: str = Field(..., description="OAuth authentication URL")
    provider: str = Field(..., description="OAuth provider name")


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenRefreshResponse(BaseModel):
    """Response model for token refresh."""
    success: bool = Field(True, description="Refresh success status")
    tokens: AuthTokens = Field(..., description="New authentication tokens")
    user: UserProfile = Field(..., description="Updated user profile")


# Custom exceptions for authentication
class AuthenticationError(Exception):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class TokenExpiredError(AuthenticationError):
    """Raised when an authentication token has expired."""
    
    def __init__(self, message: str = "Authentication token has expired"):
        super().__init__(message, error_code="TOKEN_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """Raised when an authentication token is invalid."""
    
    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(message, error_code="INVALID_TOKEN")


class OAuthProviderError(AuthenticationError):
    """Raised when OAuth provider returns an error."""
    
    def __init__(self, message: str, provider: Optional[str] = None):
        details = {"provider": provider} if provider else {}
        super().__init__(message, error_code="OAUTH_PROVIDER_ERROR", details=details)