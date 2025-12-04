# Quick Start Guide

Get your Events API deployed and running in 5 minutes!

## ⚡ Super Quick Deploy

```bash
# 1. Clone and enter directory
cd kiro-coding-challenge

# 2. Deploy (one command!)
./deploy.sh

# 3. Get your API URL from the output
# Look for: InfrastructureStack.ApiUrl = https://...
```

## 🧪 Test Your API

```bash
# Replace YOUR-API-URL with the URL from deployment output
./test-api.sh https://YOUR-API-URL/prod
```

## 📖 View Documentation

Open in browser:
```
https://YOUR-API-URL/prod/docs
```

## 🎯 Common Commands

### Create an Event
```bash
curl -X POST "https://YOUR-API-URL/prod/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Event",
    "description": "Event description",
    "date": "2024-12-15T10:00:00Z",
    "location": "San Francisco",
    "capacity": 100,
    "organizer": "Me",
    "status": "published"
  }'
```

### List All Events
```bash
curl "https://YOUR-API-URL/prod/events"
```

### Get Specific Event
```bash
curl "https://YOUR-API-URL/prod/events/{EVENT_ID}"
```

### Update Event
```bash
curl -X PUT "https://YOUR-API-URL/prod/events/{EVENT_ID}" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

### Delete Event
```bash
curl -X DELETE "https://YOUR-API-URL/prod/events/{EVENT_ID}"
```

## 🔍 Monitoring

### View Logs
```bash
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --follow
```

### Check Health
```bash
curl "https://YOUR-API-URL/prod/health"
```

## 🔄 Update After Code Changes

```bash
cd infrastructure
cdk deploy
```

## 🧹 Delete Everything

```bash
cd infrastructure
cdk destroy
```

## ❓ Troubleshooting

### Can't find API URL?
```bash
aws cloudformation describe-stacks \
  --stack-name InfrastructureStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### Deployment failed?
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name InfrastructureStack

# Check if Docker is running
docker ps

# Verify AWS credentials
aws sts get-caller-identity
```

### Lambda errors?
```bash
# View recent logs
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --since 10m
```

## 📚 Need More Info?

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- API documentation: [backend/README.md](backend/README.md)
- Infrastructure details: [infrastructure/README.md](infrastructure/README.md)

## 💡 Tips

1. **Save your API URL** - You'll need it for testing
2. **Check the docs** - Visit `/docs` endpoint for interactive API testing
3. **Monitor costs** - Check AWS Billing Dashboard (should be ~$0-5/month)
4. **Enable authentication** - Add API keys or Cognito for production use
5. **Restrict CORS** - Update allowed origins for production

---

**That's it!** You now have a production-ready, auto-scaling API running on AWS. 🚀
