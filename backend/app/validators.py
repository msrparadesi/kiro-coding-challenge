from datetime import datetime
from typing import Optional
from .exceptions import ValidationException


def validate_date_format(date_str: str) -> bool:
    """Validate that date string is in ISO format and is a valid date"""
    try:
        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        raise ValidationException(
            message="Date must be in ISO format (e.g., 2024-06-15T09:00:00Z)",
            field="date"
        )


def validate_future_date(date_str: str, allow_past: bool = False) -> bool:
    """Validate that date is in the future (optional)"""
    try:
        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if not allow_past and parsed_date < datetime.now(parsed_date.tzinfo):
            raise ValidationException(
                message="Event date must be in the future",
                field="date"
            )
        return True
    except ValidationException:
        raise
    except Exception:
        raise ValidationException(
            message="Invalid date format",
            field="date"
        )


def validate_status(status: str) -> bool:
    """Validate event status"""
    valid_statuses = ["draft", "published", "cancelled", "completed"]
    if status not in valid_statuses:
        raise ValidationException(
            message=f"Status must be one of: {', '.join(valid_statuses)}",
            field="status"
        )
    return True


def validate_capacity(capacity: int, min_val: int = 1, max_val: int = 100000) -> bool:
    """Validate event capacity"""
    if capacity < min_val:
        raise ValidationException(
            message=f"Capacity must be at least {min_val}",
            field="capacity"
        )
    if capacity > max_val:
        raise ValidationException(
            message=f"Capacity cannot exceed {max_val}",
            field="capacity"
        )
    return True


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input by trimming whitespace"""
    sanitized = value.strip()
    if not sanitized:
        raise ValidationException(
            message="Field cannot be empty or contain only whitespace"
        )
    if max_length and len(sanitized) > max_length:
        raise ValidationException(
            message=f"Field exceeds maximum length of {max_length} characters"
        )
    return sanitized
