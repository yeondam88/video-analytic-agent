from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
import uuid
from typing import Dict, Any

# Create router without prefix
router = APIRouter()

@router.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Welcome to the Video Analytics API",
        "version": "1.0.0",
        "status": "healthy"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running"
    }

class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(APIException):
    """Raised when request validation fails."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)

class NotFoundError(APIException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)

class ProcessingError(APIException):
    """Raised when video/audio processing fails."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

async def request_middleware(request: Request, call_next):
    """Middleware to add request ID and handle errors."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Request {request_id} failed")
        return await handle_exception(request, e)

async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all routes."""
    if isinstance(exc, APIException):
        status_code = exc.status_code
        content = {
            "message": exc.message,
            "details": exc.details,
            "request_id": request.state.request_id
        }
    else:
        status_code = 500
        content = {
            "message": "Internal server error",
            "details": {"error": str(exc)},
            "request_id": request.state.request_id
        }
    
    logger.error(f"Request {request.state.request_id} failed: {exc}")
    return JSONResponse(status_code=status_code, content=content)

def setup_error_handling(app):
    """Configure global error handling for the application."""
    app.middleware("http")(request_middleware)
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return await handle_exception(request, exc)
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return await handle_exception(request, exc)
    
    logger.info("Configured global error handling") 