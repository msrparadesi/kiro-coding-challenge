from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class EventBase(BaseModel):
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Event title",
        examples=["Tech Conference 2024"]
    )
    description: str = Field(
        ..., 
        min_length=1,
        max_length=1000,
        description="Event description",
        examples=["Annual technology conference featuring industry leaders"]
    )
    date: str = Field(
        ..., 
        description="Event date in ISO 8601 format",
        examples=["2024-06-15T09:00:00Z"]
    )
    location: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Event location",
        examples=["San Francisco, CA"]
    )
    capacity: int = Field(
        ..., 
        gt=0,
        le=100000,
        description="Maximum number of attendees",
        examples=[500]
    )
    organizer: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Event organizer name",
        examples=["Tech Events Inc"]
    )
    status: Literal["draft", "published", "active", "cancelled", "completed"] = Field(
        ...,
        description="Event status",
        examples=["published", "active"]
    )

    @field_validator('title', 'description', 'location', 'organizer')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure strings are not just whitespace"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip()

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate ISO 8601 date format (accepts both date and datetime)"""
        try:
            # Try parsing as full datetime first
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError):
            try:
                # Try parsing as date only (YYYY-MM-DD)
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except (ValueError, AttributeError):
                raise ValueError('Date must be in ISO 8601 format (e.g., 2024-06-15 or 2024-06-15T09:00:00Z)')

    @field_validator('capacity')
    @classmethod
    def validate_capacity_range(cls, v: int) -> int:
        """Validate capacity is within reasonable range"""
        if v < 1:
            raise ValueError('Capacity must be at least 1')
        if v > 100000:
            raise ValueError('Capacity cannot exceed 100,000')
        return v


class EventCreate(EventBase):
    """Model for creating a new event"""
    eventId: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Optional custom event ID. If not provided, a UUID will be generated.",
        examples=["api-test-event-456"]
    )
    
    @field_validator('eventId')
    @classmethod
    def validate_event_id(cls, v: Optional[str]) -> Optional[str]:
        """Ensure eventId is not just whitespace if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Event ID cannot be empty or contain only whitespace')
        return v.strip() if v else v


class EventUpdate(BaseModel):
    """Model for updating an existing event (all fields optional)"""
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Event title"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1000,
        description="Event description"
    )
    date: Optional[str] = Field(
        None,
        description="Event date in ISO 8601 format"
    )
    location: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Event location"
    )
    capacity: Optional[int] = Field(
        None, 
        gt=0,
        le=100000,
        description="Maximum number of attendees"
    )
    organizer: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100,
        description="Event organizer name"
    )
    status: Optional[Literal["draft", "published", "active", "cancelled", "completed"]] = Field(
        None,
        description="Event status"
    )

    @field_validator('title', 'description', 'location', 'organizer')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure strings are not just whitespace if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip() if v else v

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO 8601 date format if provided (accepts both date and datetime)"""
        if v is not None:
            try:
                # Try parsing as full datetime first
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Try parsing as date only (YYYY-MM-DD)
                    datetime.strptime(v, '%Y-%m-%d')
                except (ValueError, AttributeError):
                    raise ValueError('Date must be in ISO 8601 format (e.g., 2024-06-15 or 2024-06-15T09:00:00Z)')
        return v

    @field_validator('capacity')
    @classmethod
    def validate_capacity_range(cls, v: Optional[int]) -> Optional[int]:
        """Validate capacity is within reasonable range if provided"""
        if v is not None:
            if v < 1:
                raise ValueError('Capacity must be at least 1')
            if v > 100000:
                raise ValueError('Capacity cannot exceed 100,000')
        return v


class Event(EventBase):
    """Complete event model with system-generated fields"""
    eventId: str = Field(..., description="Unique event identifier (UUID)")
    createdAt: str = Field(..., description="Creation timestamp (ISO 8601)")
    updatedAt: str = Field(..., description="Last update timestamp (ISO 8601)")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: list[ValidationErrorDetail] = Field(..., description="List of validation errors")
