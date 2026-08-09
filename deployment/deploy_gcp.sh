#!/bin/bash
set -euo pipefail

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/udp2-living-risk-engine:latest"

docker build -t "${IMAGE_NAME}" -f deployment/Dockerfile .
docker push "${IMAGE_NAME}"

gcloud run deploy udp2-living-risk-engine \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --min-instances 0 \
  --memory 512Mi \
  --port 8080

