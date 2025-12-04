# Events API - Serverless FastAPI Backend

A production-ready REST API for managing events, built with FastAPI and deployed as a serverless application on AWS.

## 🚀 Quick Deploy

```bash
./deploy.sh
```

Your API will be live in ~5 minutes with a public HTTPS endpoint!

## ✨ Features

- **Full CRUD Operations** - Create, read, update, and delete events
- **Serverless Architecture** - AWS Lambda + API Gateway + DynamoDB
- **Production Ready** - Comprehensive error handling, validation, and logging
- **Auto-scaling** - Handles traffic spikes automatically
- **Cost Effective** - Pay only for what you use (~$0-5/month)
- **Interactive Docs** - Built-in Swagger UI
- **CORS Enabled** - Ready for web applications

## 📋 Event Properties

Each event includes:
- `eventId` - Unique identifier (UUID, auto-generated)
- `title` - Event title (1-200 chars)
- `description` - Event description (1-1000 chars)
- `date` - Event date (ISO 8601 format)
- `location` - Event location (1-200 chars)
- `capacity` - Max attendees (1-100,000)
- `organizer` - Organizer name (1-100 chars)
- `status` - Status (draft, published, cancelled, completed)
- `createdAt` - Creation timestamp (auto-generated)
- `updatedAt` - Last update timestamp (auto-generated)

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│  (Browser)  │      │  (REST API)  │      │  (FastAPI)  │      │ (EventsTable)│
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

- **API Gateway**: Public HTTPS endpoint with CORS, throttling, and logging
- **Lambda**: Docker-based function running FastAPI (auto-scales)
- **DynamoDB**: NoSQL database with pay-per-request billing

## 📦 Project Structure

```
.
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # API routes and application
│   │   ├── models.py       # Pydantic models with validation
│   │   ├── database.py     # DynamoDB client
│   │   ├── config.py       # Configuration settings
│   │   ├── exceptions.py   # Error handling
│   │   └── validators.py   # Custom validators
│   ├── Dockerfile          # Lambda container image
│   ├── lambda_handler.py   # Lambda entry point
│   └── requirements.txt    # Python dependencies
├── infrastructure/          # AWS CDK infrastructure
│   └── lib/
│       └── infrastructure-stack.ts  # CDK stack definition
├── deploy.sh               # One-command deployment script
└── DEPLOYMENT.md          # Detailed deployment guide
```

## 🎯 API Endpoints

### Events
- `POST /events` - Create event
- `GET /events` - List events (supports `?limit=N&status=published`)
- `GET /events/{id}` - Get event by ID
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event

### System
- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🚀 Deployment

### Prerequisites

- AWS Account with CLI configured
- Docker installed and running
- Node.js (v18+) and npm
- AWS CDK: `npm install -g aws-cdk`

### Deploy

```bash
# Quick deploy
./deploy.sh

# Or manually
cd infrastructure
npm install
cdk bootstrap  # First time only
cdk deploy
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🧪 Testing

### Create an Event

```bash
curl -X POST "https://YOUR-API-URL/prod/events" \
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
```

### List Events

```bash
curl "https://YOUR-API-URL/prod/events"
```

### Interactive Testing

Visit `https://YOUR-API-URL/prod/docs` for Swagger UI

## 💻 Local Development

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AWS credentials
uvicorn app.main:app --reload
```

Access at http://localhost:8000

### Generate API Documentation

```bash
cd backend
pip install -r requirements.txt
pdoc app -o docs
```

This generates HTML documentation in `backend/docs/` from the Python docstrings.

## 🔍 Monitoring

### View Logs

```bash
aws logs tail /aws/lambda/InfrastructureStack-EventsApiFunction --follow
```

### Metrics

AWS Console → API Gateway → Your API → Dashboard

## 🔄 Updates

After code changes:

```bash
cd infrastructure
cdk deploy
```

Zero-downtime deployment with automatic rollback on errors.

## 🧹 Cleanup

```bash
cd infrastructure
cdk destroy
```

## 💰 Cost

With AWS Free Tier:
- Lambda: 1M requests/month free
- API Gateway: 1M requests/month free (first year)
- DynamoDB: 25GB storage free

**Estimated cost**: $0-5/month for moderate usage

## 🔒 Security

Current configuration (development):
- ✅ CORS enabled for all origins
- ✅ Input validation
- ✅ Error handling
- ✅ CloudWatch logging
- ⚠️ No authentication (add for production)

For production:
- Add API Gateway authentication
- Restrict CORS origins
- Enable AWS WAF
- Use VPC for Lambda

## 📚 Documentation

- [Backend README](backend/README.md) - API details
- [API Documentation](backend/docs/index.html) - Auto-generated API docs (pdoc)
- [Infrastructure README](infrastructure/README.md) - CDK details
- [Deployment Guide](DEPLOYMENT.md) - Step-by-step deployment
- [Quick Start Guide](QUICK_START.md) - 5-minute setup
- [Project Summary](PROJECT_SUMMARY.md) - Complete overview

## 🛠️ Tech Stack

- **Backend**: FastAPI, Pydantic, Boto3
- **Infrastructure**: AWS CDK (TypeScript)
- **AWS Services**: Lambda, API Gateway, DynamoDB, CloudWatch
- **Container**: Docker (Lambda runtime)

## 📝 License

MIT

---

**Ready to deploy?** Run `./deploy.sh` and get your API live in minutes! 🚀
