# Events API Infrastructure

AWS CDK infrastructure for deploying the Events API as a serverless application.

## Architecture

- **API Gateway**: REST API with CORS support
- **Lambda**: Docker-based function running FastAPI
- **DynamoDB**: NoSQL database for event storage

## Prerequisites

1. AWS CLI configured with credentials
2. Node.js and npm installed
3. AWS CDK CLI installed: `npm install -g aws-cdk`
4. Docker installed and running

## Deployment

### First Time Setup

1. Install dependencies:
```bash
npm install
```

2. Bootstrap CDK (only needed once per AWS account/region):
```bash
cdk bootstrap
```

### Deploy the Stack

```bash
cdk deploy
```

This will:
- Build the Docker image for the Lambda function
- Create the DynamoDB table
- Deploy the Lambda function
- Create the API Gateway
- Output the public API URL

### View Outputs

After deployment, you'll see outputs like:
```
Outputs:
InfrastructureStack.ApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
InfrastructureStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/events
InfrastructureStack.ApiDocsUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/docs
```

## Testing the API

### Using curl

```bash
# Get API info
curl https://your-api-url.amazonaws.com/prod/

# Create an event
curl -X POST "https://your-api-url.amazonaws.com/prod/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-06-15T09:00:00Z",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Events Inc",
    "status": "published"
  }'

# List all events
curl https://your-api-url.amazonaws.com/prod/events

# Get a specific event
curl https://your-api-url.amazonaws.com/prod/events/{event_id}
```

### Using the Swagger UI

Visit the API documentation URL (shown in outputs) to interact with the API through a web interface.

## Monitoring

### CloudWatch Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --follow
```

### API Gateway Metrics

View API metrics in the AWS Console:
- Go to API Gateway → Your API → Dashboard
- View request count, latency, errors, etc.

## Updating the API

After making changes to the backend code:

```bash
cdk deploy
```

CDK will automatically rebuild the Docker image and update the Lambda function.

## Cleanup

To delete all resources:

```bash
cdk destroy
```

**Note**: The DynamoDB table has `removalPolicy: DESTROY` set, so it will be deleted along with all data. Change this to `RETAIN` in production.

## Cost Optimization

This serverless architecture is cost-effective:
- **Lambda**: Pay only for execution time (free tier: 1M requests/month)
- **API Gateway**: Pay per request (free tier: 1M requests/month)
- **DynamoDB**: Pay-per-request billing (free tier: 25GB storage)

## Troubleshooting

### Docker Build Issues

If Docker build fails, ensure Docker is running:
```bash
docker ps
```

### Lambda Timeout

If requests timeout, increase the timeout in `infrastructure-stack.ts`:
```typescript
timeout: cdk.Duration.seconds(60)
```

### CORS Issues

CORS is configured to allow all origins. To restrict:
```typescript
allowOrigins: ['https://yourdomain.com']
```

## Security Considerations

For production:
1. Enable API Gateway authentication (API keys, Cognito, or IAM)
2. Restrict CORS origins to your domain
3. Enable AWS WAF for DDoS protection
4. Use VPC for Lambda if accessing private resources
5. Enable CloudTrail for audit logging
6. Set DynamoDB table to `RETAIN` mode
