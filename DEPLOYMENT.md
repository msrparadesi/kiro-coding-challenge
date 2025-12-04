# Events API - Quick Deployment Guide

This guide will help you deploy the Events API to AWS in minutes.

## 🚀 Quick Start

### Prerequisites

Before deploying, ensure you have:

1. ✅ **AWS Account** with appropriate permissions
2. ✅ **AWS CLI** installed and configured (`aws configure`)
3. ✅ **Docker** installed and running
4. ✅ **Node.js** (v18+) and npm installed
5. ✅ **AWS CDK** installed globally: `npm install -g aws-cdk`

### One-Command Deployment

```bash
./deploy.sh
```

That's it! The script will:
- Check prerequisites
- Install dependencies
- Bootstrap CDK (if needed)
- Build and deploy everything

## 📋 Manual Deployment Steps

If you prefer manual control:

### 1. Install Infrastructure Dependencies

```bash
cd infrastructure
npm install
```

### 2. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap
```

### 3. Deploy

```bash
cdk deploy
```

### 4. Get Your API URL

After deployment, you'll see outputs like:

```
✅  InfrastructureStack

Outputs:
InfrastructureStack.ApiUrl = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
InfrastructureStack.ApiEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/events
InfrastructureStack.ApiDocsUrl = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/docs
```

## 🧪 Testing Your Deployment

### 1. Check API Health

```bash
curl https://YOUR-API-URL/prod/health
```

### 2. Create a Test Event

```bash
curl -X POST "https://YOUR-API-URL/prod/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "description": "Testing the deployed API",
    "date": "2024-12-15T10:00:00Z",
    "location": "Virtual",
    "capacity": 100,
    "organizer": "Test Organizer",
    "status": "published"
  }'
```

### 3. List Events

```bash
curl https://YOUR-API-URL/prod/events
```

### 4. View Interactive Documentation

Open in your browser:
```
https://YOUR-API-URL/prod/docs
```

## 🔍 Monitoring

### View Lambda Logs

```bash
# Get the function name from CDK outputs
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --follow
```

### View API Metrics

Go to AWS Console → API Gateway → Your API → Dashboard

## 🔄 Updating the API

After making code changes:

```bash
cd infrastructure
cdk deploy
```

CDK will automatically:
- Rebuild the Docker image
- Update the Lambda function
- Deploy changes with zero downtime

## 🧹 Cleanup

To delete all resources and avoid charges:

```bash
cd infrastructure
cdk destroy
```

**Warning**: This will delete the DynamoDB table and all data!

## 💰 Cost Estimate

With AWS Free Tier:
- **Lambda**: 1M requests/month free
- **API Gateway**: 1M requests/month free (first 12 months)
- **DynamoDB**: 25GB storage + 25 read/write units free

Expected cost for moderate usage: **$0-5/month**

## 🔒 Security Notes

The default deployment is configured for development/testing:
- CORS allows all origins
- No authentication required
- Public API access

For production, consider:
1. Adding API Gateway authentication (API keys, Cognito)
2. Restricting CORS to your domain
3. Enabling AWS WAF
4. Using VPC for Lambda
5. Enabling CloudTrail logging

## 🐛 Troubleshooting

### Docker Not Running

```bash
# Start Docker Desktop or Docker daemon
docker ps
```

### AWS CLI Not Configured

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### CDK Not Installed

```bash
npm install -g aws-cdk
```

### Deployment Fails

Check CloudFormation events:
```bash
aws cloudformation describe-stack-events --stack-name InfrastructureStack
```

### Lambda Timeout

Increase timeout in `infrastructure/lib/infrastructure-stack.ts`:
```typescript
timeout: cdk.Duration.seconds(60)
```

## 📚 Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Lambda Documentation](https://docs.aws.amazon.com/lambda/)

## 🆘 Need Help?

1. Check the logs: `aws logs tail /aws/lambda/YOUR-FUNCTION-NAME --follow`
2. Review CloudFormation events in AWS Console
3. Verify Docker is running: `docker ps`
4. Ensure AWS credentials are valid: `aws sts get-caller-identity`

---

**Ready to deploy?** Run `./deploy.sh` and you'll have a live API in minutes! 🚀
