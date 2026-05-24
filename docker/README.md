# Docker Deployment Guide

This guide explains how to deploy the NeurForge service with its frontend using Docker.

## Prerequisites

- Docker installed on your system
  - Visit https://www.docker.com/ to download and install Docker if needed
  - Verify your installation by running `docker --version`

## Deployment Steps

### Step 1. Clone the Repository

Execute the command below to clone the project repository:

```bash
git clone https://github.com/AaronHung/neurforge.git
```

### Step 2. Build the Docker Image

Build the NeurForge Docker image.

> Note: The Dockerfile is located in the docker/ directory.

```bash
cd neurforge/docker
docker build -t neurforge .
```

### Step 3. Configure the Environment

1. Create a configuration file by copying the template:

```bash
cp .env.docker.example .env
```

2. Configure the following required variables in `.env`:

```plaintext
# LLM Configuration (required)
NEURFORGE_LLM_TYPE=chat.completions
NEURFORGE_LLM_MODEL=deepseek-chat
NEURFORGE_LLM_BASE_URL=https://api.deepseek.com/v1
NEURFORGE_LLM_API_KEY=<your-api-key> # Required

# Serper API Configuration
# Get your key from https://serper.dev/playground
SERPER_API_KEY=<your-serper-key>

# Frontend Configuration
# Note: IP must be 0.0.0.0 for Docker container port forwarding
UTU_WEBUI_PORT=8848
UTU_WEBUI_IP=0.0.0.0
```

### Step 4. Launch the Service

#### Option 1: Run the Default Web Search Agent Demo

Replace /path/to/your/.env with the actual path to your .env file, then run:

```bash
docker run -it \
    -p 8848:8848 \
    -v "/path/to/your/.env:/neurforge/.env" \
    neurforge
```

The service will be accessible at http://127.0.0.1:8848

#### Option 2: Interactive Shell Access

To run other examples or custom configurations by replacing the `/path/to/your/.env`:

```bash
docker run -it \
    -p 8848:8848 \
    -v "/path/to/your/.env:/neurforge/.env" \
    neurforge \
    bash
```
