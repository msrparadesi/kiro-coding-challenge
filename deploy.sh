#!/bin/bash

# Events API Deployment Script
# This script deploys the Events API to AWS using CDK

set -e

echo "🚀 Starting Events API Deployment"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ Error: AWS CDK is not installed. Install it with: npm install -g aws-cdk"
    exit 1
fi

echo ""
echo "✅ Prerequisites check passed"
echo ""

# Navigate to infrastructure directory
cd infrastructure

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing CDK dependencies..."
    npm install
fi

# Acknowledge CDK notices to reduce noise
cdk acknowledge 34892 2>/dev/null || true

# Bootstrap CDK if needed (this is safe to run multiple times)
echo ""
echo "🔧 Bootstrapping CDK (if needed)..."
cdk bootstrap --quiet 2>/dev/null || cdk bootstrap

# Deploy the stack
echo ""
echo "🚀 Deploying infrastructure..."
cdk deploy --require-approval never

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Your API is now live. Check the outputs above for:"
echo "   - API URL"
echo "   - API Endpoint"
echo "   - API Documentation URL"
echo ""
echo "💡 Test your API with:"
echo "   curl \$(aws cloudformation describe-stacks --stack-name InfrastructureStack --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' --output text)"
echo ""
