from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
from dotenv import load_dotenv
import logging

from .models import Event, EventCreate, EventUpdate
from .database import db_client
from .config import settings
from .exceptions import (
    EventNotFoundException,
    DatabaseException,
    ValidationException,
    event_not_found_handler,
    database_exception_handler,
    validation_exception_handler,
    request_validation_exception_handler,
    generic_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS with proper settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Register exception handlers
app.add_exception_handler(EventNotFoundException, event_not_found_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Events API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection by attempting to list events with limit
        db_client.list_events(limit=1)
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.post(
    "/events",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
    description="Create a new event with all required fields",
    responses={
        201: {"description": "Event created successfully"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
def create_event(event: EventCreate):
    """
    Create a new event with the following information:
    
    - **title**: Event title (1-200 characters)
    - **description**: Event description (1-1000 characters)
    - **date**: Event date in ISO 8601 format
    - **location**: Event location (1-200 characters)
    - **capacity**: Maximum attendees (1-100,000)
    - **organizer**: Organizer name (1-100 characters)
    - **status**: Event status (draft, published, cancelled, completed)
    """
    try:
        event_data = event.model_dump()
        created_event = db_client.create_event(event_data)
        logger.info(f"Created event: {created_event['eventId']}")
        return created_event
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating event: {str(e)}")
        raise DatabaseException("Failed to create event", original_error=e)


@app.get(
    "/events",
    response_model=List[Event],
    summary="List all events",
    description="Retrieve a list of all events",
    responses={
        200: {"description": "List of events"},
        500: {"description": "Internal server error"}
    }
)
def list_events(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of events to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by event status")
):
    """
    List all events with optional filtering:
    
    - **limit**: Maximum number of events to return (1-1000)
    - **status**: Filter by event status (draft, published, cancelled, completed)
    """
    try:
        events = db_client.list_events(limit=limit)
        
        # Apply status filter if provided
        if status_filter:
            events = [e for e in events if e.get('status') == status_filter]
        
        logger.info(f"Listed {len(events)} events")
        return events
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing events: {str(e)}")
        raise DatabaseException("Failed to list events", original_error=e)


@app.get(
    "/events/{event_id}",
    response_model=Event,
    summary="Get a specific event",
    description="Retrieve a single event by its ID",
    responses={
        200: {"description": "Event found"},
        404: {"description": "Event not found"},
        500: {"description": "Internal server error"}
    }
)
def get_event(event_id: str):
    """
    Get a specific event by ID:
    
    - **event_id**: Unique event identifier (UUID)
    """
    try:
        event = db_client.get_event(event_id)
        if not event:
            raise EventNotFoundException(event_id)
        logger.info(f"Retrieved event: {event_id}")
        return event
    except EventNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting event {event_id}: {str(e)}")
        raise DatabaseException("Failed to retrieve event", original_error=e)


@app.put(
    "/events/{event_id}",
    response_model=Event,
    summary="Update an event",
    description="Update an existing event (partial updates supported)",
    responses={
        200: {"description": "Event updated successfully"},
        404: {"description": "Event not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
def update_event(event_id: str, event_update: EventUpdate):
    """
    Update an existing event:
    
    - **event_id**: Unique event identifier (UUID)
    - All fields are optional for partial updates
    """
    try:
        # Extract only fields that were actually provided
        update_data = event_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise ValidationException("No fields provided for update")
        
        # Update event (will raise EventNotFoundException if not found)
        updated_event = db_client.update_event(event_id, update_data)
        logger.info(f"Updated event: {event_id}")
        return updated_event
    except EventNotFoundException:
        raise
    except ValidationException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating event {event_id}: {str(e)}")
        raise DatabaseException("Failed to update event", original_error=e)


@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event",
    description="Delete an existing event",
    responses={
        204: {"description": "Event deleted successfully"},
        404: {"description": "Event not found"},
        500: {"description": "Internal server error"}
    }
)
def delete_event(event_id: str):
    """
    Delete an event:
    
    - **event_id**: Unique event identifier (UUID)
    """
    try:
        # Delete event (will raise EventNotFoundException if not found)
        db_client.delete_event(event_id)
        logger.info(f"Deleted event: {event_id}")
        return None
    except EventNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting event {event_id}: {str(e)}")
        raise DatabaseException("Failed to delete event", original_error=e)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"DynamoDB Table: {settings.DYNAMODB_TABLE_NAME}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info(f"Shutting down {settings.API_TITLE}")
