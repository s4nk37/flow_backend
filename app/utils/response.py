"""
Standardized API response utilities.
Implements the API specification for consistent response formatting.
"""
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response format"""
    success: bool = True
    message: Optional[str] = None
    data: Any = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    success: bool = False
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


# Error codes
class ErrorCode:
    """Standard error codes"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    SERVER_ERROR = "SERVER_ERROR"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TODO_NOT_FOUND = "TODO_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        meta: Optional metadata (pagination, sync info, etc.)
        status_code: HTTP status code
    
    Returns:
        JSONResponse with standardized format
    """
    response = SuccessResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True)
    )


def error_response(
    message: str,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Human-readable error message
        error_code: Error code for programmatic handling
        details: Optional additional error details
        status_code: HTTP status code
    
    Returns:
        JSONResponse with standardized error format
    """
    response = ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True)
    )


def validation_error_response(
    message: str = "Invalid data format",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a validation error response (400)"""
    return error_response(
        message=message,
        error_code=ErrorCode.VALIDATION_ERROR,
        details=details,
        status_code=400
    )


def unauthorized_response(
    message: str = "Invalid or expired token",
    error_code: str = ErrorCode.UNAUTHORIZED
) -> JSONResponse:
    """Create an unauthorized error response (401)"""
    return error_response(
        message=message,
        error_code=error_code,
        status_code=401
    )


def forbidden_response(
    message: str = "Access denied",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a forbidden error response (403)"""
    return error_response(
        message=message,
        error_code=ErrorCode.FORBIDDEN,
        details=details,
        status_code=403
    )


def not_found_response(
    message: str = "Resource not found",
    error_code: str = ErrorCode.NOT_FOUND,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a not found error response (404)"""
    return error_response(
        message=message,
        error_code=error_code,
        details=details,
        status_code=404
    )


def conflict_response(
    message: str = "Version conflict",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a conflict error response (409)"""
    return error_response(
        message=message,
        error_code=ErrorCode.CONFLICT,
        details=details,
        status_code=409
    )


def server_error_response(
    message: str = "Internal server error"
) -> JSONResponse:
    """Create a server error response (500)"""
    return error_response(
        message=message,
        error_code=ErrorCode.SERVER_ERROR,
        status_code=500
    )

