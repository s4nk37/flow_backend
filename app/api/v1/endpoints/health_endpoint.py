"""
Health check endpoint for monitoring and load balancers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.utils.response import success_response, server_error_response
from app.core.config import settings

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    Returns service status and database connectivity.
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.VERSION,
        "database": db_status,
        "service": settings.PROJECT_NAME
    }
    
    if db_status == "healthy":
        return success_response(
            data=health_data,
            message="Service is healthy"
        )
    else:
        return server_error_response(
            message="Service is degraded - database connection failed"
        )

