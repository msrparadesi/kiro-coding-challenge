---
inclusion: fileMatch
fileMatchPattern: '**/app/**/*.py'
---

# API Standards for This Project

This document defines REST API conventions for this prototype application.

## HTTP Methods

- **GET**: Retrieve resources (safe, idempotent)
- **POST**: Create new resources (not idempotent)
- **PUT**: Update/replace entire resources (idempotent)
- **PATCH**: Partial updates to resources (idempotent)
- **DELETE**: Remove resources (idempotent)

## HTTP Status Codes

### Success (2xx)
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful request with no response body

### Client Errors (4xx)
- **400 Bad Request**: Invalid request format or validation failure
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation errors with details

### Server Errors (5xx)
- **500 Internal Server Error**: Unexpected server error

## JSON Response Format

### Success Response
```json
{
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "detail": "Error message or validation details"
}
```

### List Response
```json
{
  "data": [...],
  "count": 10
}
```

## API Conventions

- Use plural nouns for resource endpoints (e.g., `/users`, `/items`)
- Use path parameters for resource IDs (e.g., `/users/{id}`)
- Use query parameters for filtering, sorting, pagination
- Return appropriate status codes for all responses
- Include descriptive error messages in error responses
