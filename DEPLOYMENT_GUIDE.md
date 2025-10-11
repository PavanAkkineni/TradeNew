# 🚀 Deployment Guide - From Docker to Live Website

This guide shows you how to deploy your Trading Analytics Platform as a public website using various cloud platforms.

---

## 🚨 CRITICAL: API Routing Fix (MUST READ FIRST!)

### ✅ **Issue FIXED** (v2.7 - October 10, 2025)

**Previous Issue**: The frontend had a hardcoded `http://localhost:8000/api` URL that would fail in production.

**Solution Applied**: The API_BASE URL is now **dynamic** and environment-aware:
- **Local Development**: Uses `http://localhost:8000/api` (when hostname is localhost)
- **Production**: Uses `/api` (relative URL on your deployed domain)

**File Modified**: `frontend/static/js/app_new.js` (Lines 9-12)

```javascript
// API Base URL - Dynamic based on environment
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'  // Local development
    : '/api';  // Production - relative URL
```

### 📋 Deployment Requirements

For this to work correctly in production, ensure:

1. **Backend and Frontend on Same Domain** (Recommended)
   - ✅ Frontend: `https://yourdomain.com`
   - ✅ Backend API: `https://yourdomain.com/api`
   - This is the standard setup and requires no CORS configuration

2. **Or Configure CORS if Different Domains**
   - If backend is on different domain/subdomain
   - Add CORS middleware in `app/main.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### ✅ **You're Now Ready to Deploy!**

The critical API routing issue has been resolved. Proceed with any deployment option below.

---

## 📋 Table of Contents
1. [Quick Comparison](#quick-comparison)
2. [Option 1: Render (Easiest - Free Tier)](#option-1-render-easiest---free-tier)
3. [Option 2: Railway (Easy - Free Trial)](#option-2-railway-easy---free-trial)
4. [Option 3: AWS EC2 (Most Control)](#option-3-aws-ec2-most-control)
5. [Option 4: Google Cloud Run (Serverless)](#option-4-google-cloud-run-serverless)
6. [Option 5: Azure Container Instances](#option-5-azure-container-instances)
7. [Custom Domain Setup](#custom-domain-setup)

---

## 🎯 Quick Comparison

| Platform | Difficulty | Free Tier | Best For |
|----------|-----------|-----------|----------|
| **Render** | ⭐ Easy | ✅ Yes | Beginners, quick deployment |
| **Railway** | ⭐ Easy | ✅ Trial ($5 credit) | Fast setup, modern UI |
| **Fly.io** | ⭐⭐ Medium | ✅ Yes (limited) | Global edge deployment |
| **AWS EC2** | ⭐⭐⭐ Hard | ✅ Yes (12 months) | Full control, scalability |
| **Google Cloud Run** | ⭐⭐ Medium | ✅ Yes (generous) | Serverless, auto-scaling |
| **Azure** | ⭐⭐ Medium | ✅ Yes ($200 credit) | Enterprise integration |

---

## Option 1: Render (Easiest - Free Tier)

### ✅ Pros
- 100% free tier available
- Automatic HTTPS
- Easy GitHub integration
- No credit card required

### 📝 Steps

#### 1. Create `render.yaml` in your project root
```yaml
services:
  - type: web
    name: trading-analytics-platform
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: ALPHA_VANTAGE_API_KEY
        sync: false
      - key: NEWS_API_KEY
        sync: false
    healthCheckPath: /
```

#### 2. Push to GitHub
```powershell
git add .
git commit -m "Add Render deployment config"
git push origin main
```

#### 3. Deploy on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your repository
5. Render auto-detects Docker
6. Add environment variables in dashboard
7. Click **"Create Web Service"**

#### 4. Your site will be live at:
```
https://trading-analytics-platform.onrender.com
```

**⚠️ Note**: Free tier sleeps after 15 min of inactivity (cold starts ~30 seconds)

---

## Option 2: Railway (Easy - Free Trial)

### ✅ Pros
- $5 free trial credit
- Extremely fast deployment
- Beautiful dashboard
- Automatic HTTPS

### 📝 Steps

#### 1. Install Railway CLI
```powershell
# Using npm
npm install -g @railway/cli

# Or download from railway.app
```

#### 2. Login and Deploy
```powershell
# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set GEMINI_API_KEY="your-key-here"
railway variables set ALPHA_VANTAGE_API_KEY="your-key-here"
railway variables set NEWS_API_KEY="your-key-here"

# Deploy
railway up
```

#### 3. Get your URL
```powershell
railway domain
```

Your site will be live at: `https://your-app.up.railway.app`

---

## Option 3: AWS EC2 (Most Control)

### ✅ Pros
- Full control over server
- 12 months free tier
- Highly scalable
- Industry standard

### 📝 Steps

#### 1. Launch EC2 Instance
1. Go to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **EC2** → **Launch Instance**
3. Choose **Ubuntu Server 22.04 LTS**
4. Select **t2.micro** (free tier)
5. Configure Security Group:
   - Allow **SSH (22)** from your IP
   - Allow **HTTP (80)** from anywhere
   - Allow **HTTPS (443)** from anywhere
   - Allow **Custom TCP (8000)** from anywhere
6. Create/download key pair
7. Launch instance

#### 2. Connect to Your Instance
```powershell
# Convert .pem to .ppk if using PuTTY on Windows
# Or use PowerShell SSH
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

#### 3. Install Docker on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu
newgrp docker

# Verify
docker --version
```

#### 4. Transfer Your Docker Image

**Option A: Push to Docker Hub**
```powershell
# On your local machine
docker login
docker tag trading-analytics-platform your-dockerhub-username/trading-analytics-platform
docker push your-dockerhub-username/trading-analytics-platform
```

**Option B: Clone from GitHub**
```bash
# On EC2
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### 5. Create .env file on EC2
```bash
nano .env
```
Add your environment variables:
```
GEMINI_API_KEY=your-key-here
ALPHA_VANTAGE_API_KEY=your-key-here
NEWS_API_KEY=your-key-here
```

#### 6. Build and Run
```bash
# If using GitHub
docker build -t trading-analytics-platform .

# Or pull from Docker Hub
docker pull your-dockerhub-username/trading-analytics-platform

# Run container
docker run -d \
  --name trading-app \
  -p 80:8000 \
  --env-file .env \
  --restart unless-stopped \
  trading-analytics-platform
```

#### 7. Access Your Site
```
http://your-ec2-public-ip
```

#### 8. (Optional) Setup Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/trading-app
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/trading-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Option 4: Google Cloud Run (Serverless)

### ✅ Pros
- Pay only for what you use
- Auto-scaling (0 to millions)
- Generous free tier
- Automatic HTTPS

### 📝 Steps

#### 1. Install Google Cloud CLI
Download from: https://cloud.google.com/sdk/docs/install

#### 2. Initialize and Login
```powershell
gcloud init
gcloud auth login
```

#### 3. Create Project
```powershell
gcloud projects create trading-analytics-platform --name="Trading Platform"
gcloud config set project trading-analytics-platform
```

#### 4. Enable Required APIs
```powershell
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### 5. Build and Push to Google Container Registry
```powershell
# Configure Docker for GCR
gcloud auth configure-docker

# Tag image
docker tag trading-analytics-platform gcr.io/trading-analytics-platform/trading-app

# Push to GCR
docker push gcr.io/trading-analytics-platform/trading-app
```

#### 6. Deploy to Cloud Run
```powershell
gcloud run deploy trading-app \
  --image gcr.io/trading-analytics-platform/trading-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your-key",ALPHA_VANTAGE_API_KEY="your-key",NEWS_API_KEY="your-key"
```

#### 7. Get Your URL
Your service will be deployed at:
```
https://trading-app-xxxxx-uc.a.run.app
```

---

## Option 5: Azure Container Instances

### ✅ Pros
- $200 free credit
- Simple container deployment
- Good Windows integration

### 📝 Steps

#### 1. Install Azure CLI
```powershell
winget install Microsoft.AzureCLI
```

#### 2. Login
```powershell
az login
```

#### 3. Create Resource Group
```powershell
az group create --name trading-platform-rg --location eastus
```

#### 4. Push to Azure Container Registry
```powershell
# Create ACR
az acr create --resource-group trading-platform-rg --name tradingplatformacr --sku Basic

# Login to ACR
az acr login --name tradingplatformacr

# Tag and push
docker tag trading-analytics-platform tradingplatformacr.azurecr.io/trading-app:latest
docker push tradingplatformacr.azurecr.io/trading-app:latest
```

#### 5. Deploy Container
```powershell
az container create \
  --resource-group trading-platform-rg \
  --name trading-app \
  --image tradingplatformacr.azurecr.io/trading-app:latest \
  --dns-name-label trading-analytics-platform \
  --ports 8000 \
  --environment-variables GEMINI_API_KEY="your-key" ALPHA_VANTAGE_API_KEY="your-key" NEWS_API_KEY="your-key"
```

#### 6. Get Your URL
```powershell
az container show --resource-group trading-platform-rg --name trading-app --query ipAddress.fqdn
```

---

## 🌐 Custom Domain Setup

### After deploying to any platform:

#### 1. Get Your Platform URL
- **Render**: `trading-analytics-platform.onrender.com`
- **Railway**: `your-app.up.railway.app`
- **AWS EC2**: Your EC2 public IP
- **Cloud Run**: `trading-app-xxxxx-uc.a.run.app`

#### 2. Buy a Domain (Optional)
- [Namecheap](https://www.namecheap.com) - $8-15/year
- [Google Domains](https://domains.google) - $12/year
- [Cloudflare](https://www.cloudflare.com/products/registrar/) - At cost

#### 3. Configure DNS

**For Render/Railway/Cloud Run:**
1. Go to your domain registrar
2. Add CNAME record:
   - **Name**: `www` or `@`
   - **Value**: Your platform URL
   - **TTL**: 3600

**For AWS EC2:**
1. Add A record:
   - **Name**: `@`
   - **Value**: Your EC2 IP address
   - **TTL**: 3600

#### 4. Enable HTTPS (Free with Let's Encrypt)

**For AWS EC2 with Nginx:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
```

**For other platforms:** HTTPS is automatic! 🎉

---

## 🎯 Recommended Path for Beginners

### Start Here:
1. **Render.com** (Free, easiest)
   - Deploy in 5 minutes
   - Free HTTPS
   - No credit card needed

### Then Graduate To:
2. **Google Cloud Run** (When you need scale)
   - Pay per use
   - Auto-scaling
   - Still very affordable

### For Production:
3. **AWS EC2 + Load Balancer** (Enterprise ready)
   - Full control
   - Maximum customization
   - Industry standard

---

## 📊 Cost Estimates

| Platform | Free Tier | Paid Tier (Small App) |
|----------|-----------|----------------------|
| **Render** | ✅ Forever free | $7/month |
| **Railway** | $5 credit | ~$5-10/month |
| **Fly.io** | Limited free | ~$3-5/month |
| **AWS EC2** | 12 months | ~$5-10/month |
| **Cloud Run** | Generous | ~$0-5/month (pay per use) |
| **Azure** | $200 credit | ~$10-15/month |

---

## 🔒 Security Checklist

Before going live:

- [ ] Environment variables are set (not hardcoded)
- [ ] HTTPS is enabled
- [ ] CORS is configured properly
- [ ] Rate limiting is enabled
- [ ] API keys are rotated regularly
- [ ] Logs are monitored
- [ ] Backups are configured
- [ ] Firewall rules are set

---

## 🚨 Common Issues

### Issue: "Container keeps restarting"
**Solution**: Check logs for missing environment variables
```powershell
# Render/Railway: Check dashboard logs
# AWS: docker logs trading-app
# Cloud Run: gcloud run logs read
```

### Issue: "502 Bad Gateway"
**Solution**: 
- Ensure app listens on `0.0.0.0`, not `localhost`
- Check port mapping (container port 8000)
- Verify health check endpoint

### Issue: "Slow cold starts"
**Solution**:
- Use paid tier (keeps container warm)
- Implement health check pinging
- Consider Cloud Run min instances

---

## 📞 Next Steps

1. Choose a platform from above
2. Follow the deployment steps
3. Test your live website
4. (Optional) Add custom domain
5. Monitor and optimize

**Need help?** Check platform-specific documentation:
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [AWS Docs](https://docs.aws.amazon.com)
- [Cloud Run Docs](https://cloud.google.com/run/docs)

---

## 🎉 Congratulations!

Your Docker container is now a live website accessible from anywhere in the world! 🌍
