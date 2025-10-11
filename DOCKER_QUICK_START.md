# Docker Quick Start Guide - Trading Analytics Platform

## What You Need to Know

### Docker Concepts (Simple)
- **Image**: A blueprint/template of your app (like a recipe)
- **Container**: A running instance of an image (like a cooked meal from the recipe)
- **Dockerfile**: Instructions to build the image
- **docker-compose**: Tool to manage multiple containers easily

---

## Quick Commands (Copy & Paste)

### 1️⃣ Build Your Application Image
```powershell
docker build -t trading-analytics-platform .
```
**What it does**: Creates a packaged version of your app
**Time**: 2-3 minutes first time, faster after that

---

### 2️⃣ Run Your Application
```powershell
docker run -d --name trading-app -p 8000:8000 --env-file .env trading-analytics-platform
```
**What it does**: Starts your app in a container
**Breakdown**:
- `-d` = Run in background (detached mode)
- `--name trading-app` = Give container a friendly name
- `-p 8000:8000` = Map port 8000 (container) to 8000 (your computer)
- `--env-file .env` = Load environment variables from .env file
- `trading-analytics-platform` = Use this image

**Access your app**: http://localhost:8000

---

### 3️⃣ Check If It's Running
```powershell
docker ps
```
**What it shows**: All running containers

---

### 4️⃣ View Application Logs
```powershell
docker logs trading-app
```
**What it shows**: Output from your FastAPI application

To follow logs in real-time:
```powershell
docker logs -f trading-app
```
(Press Ctrl+C to stop watching)

---

### 5️⃣ Stop Your Application
```powershell
docker stop trading-app
```

---

### 6️⃣ Start It Again
```powershell
docker start trading-app
```

---

### 7️⃣ Remove Container (When Stopped)
```powershell
docker rm trading-app
```

---

## Using Docker Compose (Easier Method)

### Start Everything
```powershell
docker-compose up -d
```
**What it does**: Builds and runs everything defined in docker-compose.yml

### View Logs
```powershell
docker-compose logs -f
```

### Stop Everything
```powershell
docker-compose down
```

### Rebuild and Restart
```powershell
docker-compose up --build -d
```

---

## Troubleshooting

### Container Won't Start?
```powershell
# Check logs for errors
docker logs trading-app

# Check if port 8000 is already in use
netstat -ano | findstr :8000
```

### Need to Go Inside the Container?
```powershell
docker exec -it trading-app bash
```
(Type `exit` to leave)

### Clean Up Everything
```powershell
# Stop all containers
docker stop $(docker ps -q)

# Remove all stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f
```

---

## Common Workflow

### Development Workflow
1. Make code changes
2. Rebuild image: `docker-compose up --build -d`
3. Test: http://localhost:8000
4. Check logs: `docker-compose logs -f`

### Production Deployment
1. Build image: `docker build -t trading-analytics-platform .`
2. Tag for registry: `docker tag trading-analytics-platform myregistry/trading-app:v1.0`
3. Push to registry: `docker push myregistry/trading-app:v1.0`
4. Deploy on server: `docker pull myregistry/trading-app:v1.0`
5. Run: `docker run -d -p 8000:8000 myregistry/trading-app:v1.0`

---

## Why Docker vs GitHub Pages?

| Feature | GitHub Pages | Docker |
|---------|-------------|--------|
| **Type** | Static files only | Full applications |
| **Backend** | ❌ No | ✅ Yes (Python, FastAPI) |
| **API Calls** | ❌ Client-side only | ✅ Server-side |
| **Databases** | ❌ No | ✅ Yes |
| **Environment Control** | ❌ Limited | ✅ Complete |
| **Scalability** | ❌ Fixed | ✅ Easy to scale |
| **Use Case** | Documentation, portfolios | Real applications |

**Your FastAPI app needs Docker because:**
- It runs Python server-side code
- It makes API calls to Alpha Vantage, Gemini
- It processes data with pandas/numpy
- It serves dynamic content
- GitHub Pages can't run Python servers!

---

## Next Steps After Docker

1. ✅ **Docker**: Package your app (You're here!)
2. 🔄 **Jenkins**: Automate building and deployment
3. ☁️ **Cloud Deployment**: AWS, Azure, or Google Cloud
4. 📊 **Monitoring**: Add logging and metrics
5. 🔒 **Security**: HTTPS, authentication, rate limiting

---

## Quick Reference Card

```
BUILD:    docker build -t trading-analytics-platform .
RUN:      docker run -d --name trading-app -p 8000:8000 trading-analytics-platform
LOGS:     docker logs -f trading-app
STOP:     docker stop trading-app
START:    docker start trading-app
REMOVE:   docker rm trading-app
LIST:     docker ps
COMPOSE:  docker-compose up -d
```

Save this file for quick reference! 📌
