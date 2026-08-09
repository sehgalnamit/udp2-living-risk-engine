#!/bin/bash
set -euo pipefail

RESOURCE_GROUP="rg-udp2-living-risk"
LOCATION="eastus"
ACR_NAME="acrudp2livingrisk"
CONTAINER_APP_NAME="udp2-living-risk-engine"

az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}"
az acr create --resource-group "${RESOURCE_GROUP}" --name "${ACR_NAME}" --sku Basic
az acr login --name "${ACR_NAME}"

IMAGE_TAG="${ACR_NAME}.azurecr.io/udp2-engine:v1"
docker build -t "${IMAGE_TAG}" -f deployment/Dockerfile .
docker push "${IMAGE_TAG}"

az containerapp env create --name udp2-env --resource-group "${RESOURCE_GROUP}" --location "${LOCATION}"
az containerapp create \
  --name "${CONTAINER_APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --environment udp2-env \
  --image "${IMAGE_TAG}" \
  --target-port 8080 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi

