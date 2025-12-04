# FastAPI + CDK Project

## Structure

- `backend/` - FastAPI Python application
- `infrastructure/` - AWS CDK Infrastructure as Code

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Infrastructure Setup

```bash
cd infrastructure
npm install
cdk deploy
```
