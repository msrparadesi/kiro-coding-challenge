# Events API Backend

FastAPI REST API for managing events with DynamoDB storage, deployable as a serverless application on AWS.

## Features

- ✅ Full CRUD operations for events
- ✅ DynamoDB integration with proper error handling
- ✅ Comprehensive input validation with Pydantic
- ✅ Production-ready CORS configuration
- ✅ Structured error responses
- ✅ Health check endpoint with database connectivity test
- ✅ Serverless deployment (Lambda + API Gateway)
- ✅ Docker-based Lambda function
- ✅ Interactive API documentation (Swagger UI)

## Event Properties

- `eventId`: Unique identifier (auto-generated UUID)
- `title`: Event title (1-200 characters)
- `description`: Event description (1-1000 characters)
- `date`: Event date (ISO 8601 format)
- `location`: Event location (1-200 characters)
- `capacity`: Maximum attendees (1-100,000)
- `organizer`: Event organizer name (1-100 characters)
- `status`: Event status (draft, published, cancelled, completed)
- `createdAt`: Creation timestamp (auto-generated)
- `updatedAt`: Last update timestamp (auto-generated)

## Local Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and settings
```

3. Run the API locally:
```bash
uvicorn app.main:app --reload
```

4. Access the API:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment to AWS

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment instructions.

### Quick Deploy

```bash
# From project root
./deploy.sh
```

This deploys:
- Lambda function (Docker-based)
- API Gateway (REST API)
- DynamoDB table
- CloudWatch logs

## API Endpoints

### Events

- `POST /events` - Create a new event
- `GET /events` - List all events (supports `?limit=N` and `?status=published`)
- `GET /events/{event_id}` - Get a specific event
- `PUT /events/{event_id}` - Update an event (partial updates supported)
- `DELETE /events/{event_id}` - Delete an event

### System

- `GET /` - API information
- `GET /health` - Health check with database connectivity test

## Example Requests

### Create Event

```bash
curl -X POST "https://your-api-url/prod/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference featuring industry leaders",
    "date": "2024-06-15T09:00:00Z",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Events Inc",
    "status": "published"
  }'
```

### List Events

```bash
# All events
curl "https://your-api-url/prod/events"

# With filters
curl "https://your-api-url/prod/events?status=published&limit=10"
```

### Get Event

```bash
curl "https://your-api-url/prod/events/{event_id}"
```

### Update Event

```bash
curl -X PUT "https://your-api-url/prod/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled"
  }'
```

### Delete Event

```bash
curl -X DELETE "https://your-api-url/prod/events/{event_id}"
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # Pydantic models with validation
│   ├── database.py       # DynamoDB client and operations
│   ├── config.py         # Configuration settings
│   ├── exceptions.py     # Custom exceptions and handlers
│   └── validators.py     # Additional validation functions
├── lambda_handler.py     # Lambda entry point (Mangum adapter)
├── Dockerfile           # Docker image for Lambda
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## Error Handling

The API provides structured error responses:

### Validation Error (422)
```json
{
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "capacity",
      "message": "Capacity must be at least 1",
      "type": "value_error"
    }
  ]
}
```

### Not Found (404)
```json
{
  "error": "Not Found",
  "message": "Event with ID 'abc-123' not found",
  "event_id": "abc-123"
}
```

### Database Error (500)
```json
{
  "error": "Database Error",
  "message": "An error occurred while accessing the database",
  "detail": "Failed to create event: ..."
}
```

## Configuration

Environment variables (`.env`):

```bash
# API Configuration
API_TITLE=Events API
API_VERSION=1.0.0

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=EventsTable
AWS_REGION=us-east-1

# Validation Settings (optional)
MAX_TITLE_LENGTH=200
MAX_DESCRIPTION_LENGTH=1000
MAX_CAPACITY=100000
```

## Testing

### Health Check

```bash
curl https://your-api-url/prod/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

## Monitoring

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --follow
```

### API Gateway Metrics

View in AWS Console:
- API Gateway → Your API → Dashboard
- Metrics: requests, latency, errors, cache hits

## Security Features

- Input validation on all fields
- SQL injection prevention (NoSQL database)
- CORS configuration
- Request throttling (API Gateway)
- CloudWatch logging
- IAM-based Lambda permissions

## Performance

- Lambda cold start: ~1-2 seconds (Docker image)
- Lambda warm execution: ~50-200ms
- DynamoDB latency: ~10-20ms
- API Gateway overhead: ~10-50ms

## Cost Optimization

- Pay-per-request billing (no idle costs)
- Lambda: $0.20 per 1M requests
- API Gateway: $3.50 per 1M requests
- DynamoDB: Pay-per-request mode
- Free tier covers most development/testing

## Troubleshooting

### Lambda Timeout

Increase timeout in `infrastructure-stack.ts`:
```typescript
timeout: cdk.Duration.seconds(60)
```

### CORS Issues

Check CORS configuration in `config.py` and `infrastructure-stack.ts`

### Database Connection

Verify IAM permissions and table name in environment variables

## Documentation

### Interactive API Documentation
- Swagger UI: `https://your-api-url/prod/docs`
- ReDoc: `https://your-api-url/prod/redoc`
- OpenAPI spec: `https://your-api-url/prod/openapi.json`

### Generated API Documentation

Auto-generated Python API documentation is available in the `docs/` folder. This documentation is generated from the Python docstrings using pdoc.

**View Documentation:**
- Open `backend/docs/index.html` in your browser
- Or view online if deployed to GitHub Pages

**Generate Documentation:**
```bash
# Using the script
./generate-docs.sh

# Or manually
pip install pdoc
pdoc app -o docs
```

The generated documentation includes:
- All modules, classes, and functions
- Type annotations and signatures
- Docstrings and usage examples
- Cross-referenced links between components
