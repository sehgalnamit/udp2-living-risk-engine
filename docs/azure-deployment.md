# Azure Deployment Guide

This guide covers deploying the UDP 2.0 Living Risk Engine to Azure using the included deployment script.

## Azure deployment flow

```mermaid
flowchart LR
    classDef infra fill:#1971C2,color:#fff,stroke:#1864AB,stroke-width:1px;
    classDef build fill:#7048E8,color:#fff,stroke:#5F3DC4,stroke-width:1px;
    classDef deploy fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:1px;
    classDef live fill:#F59F00,color:#fff,stroke:#E67700,stroke-width:1px;

    A([az group create]):::infra --> B[az acr create]:::infra
    B --> C[[Build Docker image]]:::build
    C --> D[Push to ACR]:::build
    D --> E{{Create Container\nApps environment}}:::deploy
    E --> F[Deploy Container App\n--target-port 8080]:::deploy
    F --> G(((Public HTTPS endpoint))):::live
```

## Prerequisites

- Azure CLI installed and authenticated
- Docker installed
- An active Azure subscription
- Access to create resource groups and Container Apps

## Deployment script

Use:

```bash
bash deployment/deploy_azure.sh
```

## What the script does

The Azure deployment script performs the following:

1. Creates the resource group
2. Creates Azure Container Registry
3. Logs in to the registry
4. Builds the container image from the repository Dockerfile
5. Pushes the image to ACR
6. Creates a Container Apps environment
7. Deploys the app to Azure Container Apps with public ingress

## Configuration values

The script uses the following defaults:

- resource group: `rg-udp2-living-risk`
- location: `eastus`
- ACR name: `acrudp2livingrisk`
- container app name: `udp2-living-risk-engine`

## Notes

- You may want to adjust naming and region values to match your subscription constraints.
- Container app ports are configured to expose the service on port 8080.

## Related docs

- [../README.md](../README.md)
- [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- [local-deployment.md](local-deployment.md)
- [gcp-deployment.md](gcp-deployment.md)
