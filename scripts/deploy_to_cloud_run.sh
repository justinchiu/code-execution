#!/bin/bash
set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your Google Cloud project ID
SERVICE_NAME="code-execution-server"
REGION="us-central1"          # Replace with your preferred region

# Build and push the container image to Google Container Registry
echo "Building and pushing container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300s \
  --concurrency 80 \
  --max-instances 10

echo "Deployment complete!"
echo "Service URL: $(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')"