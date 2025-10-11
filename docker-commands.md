# Docker Commands Cheat Sheet for Trading Analytics Platform

## Building and Running

```bash
# Build the image
docker build -t trading-analytics-platform .

# Run container (simple)
docker run -d --name trading-app -p 8000:8000 --env-file .env trading-analytics-platform

# Run with docker-compose (recommended)
docker-compose up -d

# Rebuild and run
docker-compose up --build -d
```

## Management Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs trading-app
docker-compose logs -f

# Stop container
docker stop trading-app
docker-compose down

# Remove container
docker rm trading-app

# Remove image
docker rmi trading-analytics-platform
```

## Debugging Commands

```bash
# Enter running container
docker exec -it trading-app bash

# Check container resource usage
docker stats trading-app

# Inspect container details
docker inspect trading-app

# View container processes
docker top trading-app
```

## Cleanup Commands

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean everything (careful!)
docker system prune -a
```

## Environment Specific Commands

```bash
# Development
docker-compose -f docker-compose.yml up -d

# Production (with nginx)
docker-compose --profile production up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d
```
