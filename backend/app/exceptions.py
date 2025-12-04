from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union
import logging

logger = logging.getLogger(__name__)


class EventNotFoundException(Exception):
    """Raised when an event is not found"""
    def __init__(self, event_id: str):
        self.event_id = event_id
        self.message = f"Event with ID '{event_id}' not found"
        super().__init__(self.message)


class DatabaseException(Exception):
    """Raised when a database operation fails"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class ValidationException(Exception):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


async def event_not_found_handler(request: Request, exc: EventNotFoundException):
    """Handle EventNotFoundException"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "event_id": exc.event_id
        }
    )


async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle DatabaseException"""
    logger.error(f"Database error: {exc.message}", exc_info=exc.original_error)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "An error occurred while accessing the database",
            "detail": exc.message
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle ValidationException"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "field": exc.field
        }
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": errors
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )
