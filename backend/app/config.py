from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator


class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Events API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FastAPI backend for managing events with DynamoDB"
    
    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # DynamoDB Settings
    DYNAMODB_TABLE_NAME: str = "EventsTable"
    AWS_REGION: str = "us-east-1"
    
    # Validation Settings
    MAX_TITLE_LENGTH: int = 200
    MAX_DESCRIPTION_LENGTH: int = 1000
    MAX_LOCATION_LENGTH: int = 200
    MAX_ORGANIZER_LENGTH: int = 100
    MIN_CAPACITY: int = 1
    MAX_CAPACITY: int = 100000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
