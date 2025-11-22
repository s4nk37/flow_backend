from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.utils.logger import logger
from app.utils.response import (
    server_error_response,
    validation_error_response,
    ErrorCode
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Flow Todo Backend API with standardized responses"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = exc.errors()
    details = {
        "fields": [
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg"),
                "type": error.get("type")
            }
            for error in errors
        ]
    }
    return validation_error_response(
        message="Invalid data format",
        details=details
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standardized format"""
    from app.utils.response import error_response, ErrorCode
    
    # Map status codes to error codes
    status_to_code = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
    }
    
    error_code = status_to_code.get(exc.status_code, ErrorCode.SERVER_ERROR)
    message = exc.detail if isinstance(exc.detail, str) else "An error occurred"
    
    return error_response(
        message=message,
        error_code=error_code,
        status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions - only catch truly unexpected errors"""
    logger.error(f"Unexpected exception: {exc}", exc_info=True)
    return server_error_response(
        message="Internal server error"
    )


app.include_router(api_router, prefix=settings.API_V1_STR)

