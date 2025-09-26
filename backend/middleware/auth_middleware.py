"""
Authentication middleware and dependencies for FastAPI endpoints.

This module provides JWT token validation, user authentication,
and route protection decorators for the AviFlux application.
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service
from models.auth_models import UserProfile, TokenValidationResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for FastAPI."""
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
        """
        Get current authenticated user from JWT token.
        
        Args:
            credentials: HTTP Bearer token credentials
            
        Returns:
            UserProfile: Authenticated user profile
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Extract token from Bearer credentials
            token = credentials.credentials
            
            # Validate token using auth service
            validation_response: TokenValidationResponse = auth_service.validate_token(token)
            
            if not validation_response.valid or not validation_response.user:
                logger.warning(f"Authentication failed: {validation_response.error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=validation_response.error or "Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"User authenticated: {validation_response.user.email}")
            return validation_response.user
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserProfile]:
        """
        Get current user if authenticated, None otherwise.
        Useful for endpoints that work with or without authentication.
        
        Args:
            credentials: Optional HTTP Bearer token credentials
            
        Returns:
            Optional[UserProfile]: User profile if authenticated, None otherwise
        """
        if not credentials:
            return None
        
        try:
            token = credentials.credentials
            validation_response = auth_service.validate_token(token)
            
            if validation_response.valid and validation_response.user:
                logger.info(f"Optional user authenticated: {validation_response.user.email}")
                return validation_response.user
            else:
                logger.info("Optional authentication failed, continuing without user")
                return None
                
        except Exception as e:
            logger.warning(f"Optional authentication error: {e}")
            return None
    
    @staticmethod
    def validate_admin_user(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        """
        Validate that current user has admin privileges.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            UserProfile: Admin user profile
            
        Raises:
            HTTPException: If user doesn't have admin privileges
        """
        # TODO: Implement admin role checking logic
        # For now, we'll assume all authenticated users have admin access
        # In production, you'd check user roles from database or token claims
        
        logger.info(f"Admin access granted to user: {current_user.email}")
        return current_user


# Convenience dependency functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """
    Dependency function to get current authenticated user.
    
    Usage:
        @app.get("/protected")
        async def protected_endpoint(user: UserProfile = Depends(get_current_user)):
            return {"message": f"Hello {user.full_name}"}
    """
    return AuthMiddleware.get_current_user(credentials)


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserProfile]:
    """
    Dependency function to get optional current user.
    
    Usage:
        @app.get("/public")
        async def public_endpoint(user: Optional[UserProfile] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.full_name}"}
            else:
                return {"message": "Hello anonymous user"}
    """
    return AuthMiddleware.get_optional_user(credentials)


def get_admin_user(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """
    Dependency function to get current admin user.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(admin: UserProfile = Depends(get_admin_user)):
            return {"message": f"Admin access for {admin.full_name}"}
    """
    return AuthMiddleware.validate_admin_user(current_user)


def verify_token(token: str) -> Optional[UserProfile]:
    """
    Utility function to verify a token and return user profile.
    
    Args:
        token: JWT access token
        
    Returns:
        Optional[UserProfile]: User profile if token is valid, None otherwise
    """
    try:
        validation_response = auth_service.validate_token(token)
        return validation_response.user if validation_response.valid else None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Optional[str]: JWT token if found, None otherwise
    """
    if not authorization:
        return None
    
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return None
        return token
    except Exception:
        return None