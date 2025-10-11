# 🚀 Jenkins Deployment - Step-by-Step Guide

Complete walkthrough to deploy your Jenkins pipeline.

---

## 📋 What I Updated in Your Jenkinsfile

### Changes Made:

1. ✅ **Fixed Docker Hub configuration**
   - Changed from generic registry to Docker Hub
   - Added placeholder for your username

2. ✅ **Fixed branch names**
   - Changed `main` to `master` (your current branch)

3. ✅ **Fixed Windows commands**
   - Changed `sh` to `bat` (for Windows)
   - Updated syntax for Windows batch files

4. ✅ **Fixed health check endpoint**
   - Using `/api/health` (confirmed in your app)

5. ✅ **Simplified credential IDs**
   - `dockerhub-credentials` (easy to remember)

---

## 🎯 What You Need to Provide

### 1. Docker Hub Username

**Where to find it:**
- Go to: https://hub.docker.com
- Your username is displayed in the top-right corner
- Example: `pavanakkineni`, `john_doe`, etc.

**What to do:**
```groovy
// In Jenkinsfile, line 6, replace:
DOCKER_HUB_USERNAME = 'YOUR_DOCKERHUB_USERNAME'

// With your actual username:
DOCKER_HUB_USERNAME = 'pavanakkineni'  // Use YOUR username
```

---

### 2. Docker Hub Access Token

**How to create:**
1. Login to Docker Hub
2. Click your profile → Account Settings
3. Go to **Security** tab
4. Click **New Access Token**
5. Name: `jenkins-pipeline`
6. Permissions: **Read, Write, Delete**
7. Click **Generate**
8. **COPY THE TOKEN** (starts with `dckr_pat_...`)

**Save this token** - you'll add it to Jenkins in the next step.

---

## 🔧 Jenkins Installation & Setup

### Step 1: Install Jenkins (Choose One Method)

#### Option A: Jenkins in Docker (Recommended - Easiest)

```powershell
# Create volume for Jenkins data
docker volume create jenkins_home

# Run Jenkins container
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v //var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts

# Wait 30 seconds, then get admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**Copy the password** that appears.

#### Option B: Jenkins Windows Installer

1. Download: https://www.jenkins.io/download/
2. Run the `.msi` installer
3. Follow the wizard
4. Jenkins will start automatically

---

### Step 2: Initial Jenkins Setup

1. **Open Jenkins:**
   - Go to: http://localhost:8080

2. **Unlock Jenkins:**
   - Paste the admin password you copied

3. **Install Plugins:**
   - Click **"Install suggested plugins"**
   - Wait for installation (5-10 minutes)

4. **Create Admin User:**
   - Username: (your choice)
   - Password: (your choice)
   - Full name: (your name)
   - Email: (your email)

5. **Jenkins URL:**
   - Keep default: `http://localhost:8080`
   - Click **"Save and Finish"**

---

### Step 3: Install Required Plugins

1. Go to: **Manage Jenkins** → **Plugins** → **Available plugins**

2. Search and install these plugins:
   - ✅ **Docker Pipeline**
   - ✅ **Docker**
   - ✅ **GitHub Integration**
   - ✅ **Pipeline**
   - ✅ **Git**

3. Check **"Restart Jenkins when installation is complete"**

4. Wait for restart (2-3 minutes)

---

### Step 4: Add Credentials to Jenkins

#### A. Add Docker Hub Credentials

1. Go to: **Manage Jenkins** → **Credentials** → **System** → **Global credentials (unrestricted)**

2. Click **"Add Credentials"**

3. Fill in:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** Your Docker Hub username (e.g., `pavanakkineni`)
   - **Password:** Your Docker Hub token (starts with `dckr_pat_...`)
   - **ID:** `dockerhub-credentials` (EXACTLY this - case sensitive!)
   - **Description:** Docker Hub Login

4. Click **"Create"**

#### B. Add API Keys (Optional - for production deployment)

Repeat the above process for each API key:

**Gemini API Key:**
- **Kind:** Secret text
- **Secret:** Your Gemini API key
- **ID:** `gemini-api-key`

**Alpha Vantage API Key:**
- **Kind:** Secret text
- **Secret:** Your Alpha Vantage API key
- **ID:** `alpha-vantage-api-key`

**News API Key:**
- **Kind:** Secret text
- **Secret:** Your News API key
- **ID:** `news-api-key`

---

### Step 5: Create Jenkins Pipeline

1. **Go to Jenkins Dashboard**
   - http://localhost:8080

2. **Click "New Item"**

3. **Configure:**
   - **Name:** `Trading-Analytics-Pipeline`
   - **Type:** Select **"Pipeline"**
   - Click **"OK"**

4. **General Settings:**
   - ✅ Check **"GitHub project"**
   - **Project URL:** `https://github.com/PavanAkkineni/TradeSignal`

5. **Build Triggers:**
   - ✅ Check **"Poll SCM"**
   - **Schedule:** `H/5 * * * *` (checks GitHub every 5 minutes)
   - OR
   - ✅ Check **"GitHub hook trigger for GITScm polling"** (if you set up webhooks)

6. **Pipeline Configuration:**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/PavanAkkineni/TradeSignal.git`
   - **Credentials:** (leave blank if public repo)
   - **Branch Specifier:** `*/master`
   - **Script Path:** `Jenkinsfile`

7. **Click "Save"**

---

## 🎯 Update Your Jenkinsfile

### Before Running Pipeline:

1. **Open:** `Jenkinsfile` in your project

2. **Find line 6:**
   ```groovy
   DOCKER_HUB_USERNAME = 'YOUR_DOCKERHUB_USERNAME'
   ```

3. **Replace with your username:**
   ```groovy
   DOCKER_HUB_USERNAME = 'pavanakkineni'  // Use YOUR actual username
   ```

4. **Save the file**

5. **Commit and push:**
   ```powershell
   git add Jenkinsfile
   git commit -m "Configure Jenkins with Docker Hub username"
   git push origin master
   ```

---

## 🚀 Run Your First Pipeline

### Option 1: Manual Trigger

1. Go to Jenkins Dashboard
2. Click on **"Trading-Analytics-Pipeline"**
3. Click **"Build Now"**
4. Watch the build progress in **"Build History"**
5. Click on the build number (e.g., `#1`)
6. Click **"Console Output"** to see logs

### Option 2: Automatic Trigger (After Git Push)

1. Make any change to your code
2. Commit and push to GitHub
3. Wait 5 minutes (or less if webhook is set up)
4. Jenkins automatically starts building

---

## 📊 Understanding the Pipeline Stages

Your pipeline will execute these stages:

```
1. Checkout Code
   ├─ Pulls latest code from GitHub
   └─ Duration: ~10 seconds

2. Environment Setup
   ├─ Copies .env.example to .env
   └─ Duration: ~5 seconds

3. Install Dependencies
   ├─ Creates Python virtual environment
   ├─ Installs packages from requirements.txt
   └─ Duration: ~2-3 minutes

4. Run Tests
   ├─ Runs pytest (if tests exist)
   ├─ Verifies app imports successfully
   └─ Duration: ~30 seconds

5. Security Scan
   ├─ Checks for vulnerable packages
   ├─ Scans code for security issues
   └─ Duration: ~1 minute

6. Build Docker Image
   ├─ Creates Docker image from Dockerfile
   ├─ Tags with build number and 'latest'
   └─ Duration: ~2-3 minutes

7. Test Docker Image
   ├─ Runs container on port 8001
   ├─ Tests health endpoint
   ├─ Stops and removes test container
   └─ Duration: ~1 minute

8. Push to Docker Hub
   ├─ Logs into Docker Hub
   ├─ Pushes image with build number
   ├─ Pushes 'latest' tag
   └─ Duration: ~2-3 minutes

9. Deploy to Production (optional)
   ├─ Requires manual approval
   ├─ Stops old container
   ├─ Starts new container
   └─ Duration: ~1 minute

Total Duration: ~10-15 minutes
```

---

## ✅ Verify Successful Deployment

### Check Jenkins:
1. Build shows **green checkmark** ✅
2. Console output shows: `✅ Pipeline completed successfully!`

### Check Docker Hub:
1. Go to: https://hub.docker.com/r/YOUR_USERNAME/trading-analytics-platform
2. You should see your image with tags:
   - `latest`
   - `1`, `2`, `3`, etc. (build numbers)

### Check Local Docker:
```powershell
# List images
docker images | findstr trading-analytics-platform

# You should see:
# YOUR_USERNAME/trading-analytics-platform   latest   ...
# YOUR_USERNAME/trading-analytics-platform   1        ...
```

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "Docker Hub credentials invalid"

**Cause:** Wrong credential ID or invalid token

**Solution:**
1. Go to Jenkins → Manage Jenkins → Credentials
2. Check credential ID is EXACTLY: `dockerhub-credentials`
3. Verify token is correct (starts with `dckr_pat_`)
4. Try creating a new access token

---

### Issue 2: "Cannot connect to Docker daemon"

**Cause:** Jenkins can't access Docker

**Solution for Docker Desktop:**
```powershell
# Ensure Docker Desktop is running
# In Docker Desktop settings:
# General → Enable "Expose daemon on tcp://localhost:2375"
```

**Solution for Jenkins in Docker:**
```powershell
# Give Jenkins container access to Docker
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

---

### Issue 3: "Python not found"

**Cause:** Python not in PATH

**Solution:**
1. Go to Jenkins → Manage Jenkins → Tools
2. Add Python installation
3. Or ensure Python is in system PATH

---

### Issue 4: "Health check failed"

**Cause:** Container not starting or wrong endpoint

**Solution:**
1. Check Docker logs: `docker logs test-container`
2. Verify `.env` file has all required API keys
3. Test manually: `docker run -d -p 8001:8000 --env-file .env YOUR_IMAGE`

---

### Issue 5: "Push to Docker Hub failed"

**Cause:** Authentication or network issue

**Solution:**
1. Test Docker Hub login manually:
   ```powershell
   docker login
   # Enter username and token
   ```
2. Verify internet connection
3. Check Docker Hub is not down: https://status.docker.com

---

## 🎓 Using the Simplified Jenkinsfile

If the full Jenkinsfile is too complex, use the simplified version:

```powershell
# Rename files
mv Jenkinsfile Jenkinsfile.full
mv Jenkinsfile.simple Jenkinsfile

# Commit and push
git add .
git commit -m "Use simplified Jenkinsfile"
git push origin master
```

The simplified version:
- ✅ Skips security scans
- ✅ Skips staging deployment
- ✅ Focuses on core: Build → Test → Push
- ✅ Easier to debug

---

## 📈 Next Steps After First Successful Build

### 1. Set Up GitHub Webhook (Instant Triggers)

Instead of polling every 5 minutes, get instant builds:

1. Go to your GitHub repo
2. Settings → Webhooks → Add webhook
3. **Payload URL:** `http://YOUR_JENKINS_URL:8080/github-webhook/`
4. **Content type:** `application/json`
5. **Events:** Just the push event
6. Click "Add webhook"

**Note:** For local Jenkins, use ngrok to expose it:
```powershell
ngrok http 8080
# Use the ngrok URL in webhook
```

---

### 2. Add Email Notifications

Get notified when builds fail:

1. Go to: Manage Jenkins → System
2. Find **"Extended E-mail Notification"**
3. Configure SMTP server (Gmail, Outlook, etc.)
4. Notifications will be sent automatically

---

### 3. Create Staging Environment

Test changes before production:

1. Create `develop` branch:
   ```powershell
   git checkout -b develop
   git push origin develop
   ```

2. Push changes to `develop` first
3. Jenkins deploys to staging (port 8002)
4. Test on staging
5. Merge to `master` for production

---

## 🎉 Success Checklist

- [ ] Jenkins installed and running
- [ ] Docker Hub account created
- [ ] Docker Hub credentials added to Jenkins
- [ ] Jenkinsfile updated with your username
- [ ] Pipeline created in Jenkins
- [ ] First build completed successfully ✅
- [ ] Docker image visible on Docker Hub
- [ ] Can pull and run image locally

---

## 📞 Summary

**What you need:**
1. Docker Hub username (e.g., `pavanakkineni`)
2. Docker Hub access token
3. Jenkins running on http://localhost:8080

**What to update:**
1. Line 6 in `Jenkinsfile`: Replace `YOUR_DOCKERHUB_USERNAME`
2. Add `dockerhub-credentials` in Jenkins

**How to run:**
1. Click "Build Now" in Jenkins
2. Or push to GitHub (automatic)

**Result:**
- ✅ Code tested automatically
- ✅ Docker image built
- ✅ Image pushed to Docker Hub
- ✅ Ready to deploy anywhere!

---

## 🔗 Quick Reference

| Item | Value |
|------|-------|
| Jenkins URL | http://localhost:8080 |
| Docker Hub | https://hub.docker.com |
| Your Repo | https://github.com/PavanAkkineni/TradeSignal |
| Credential ID | `dockerhub-credentials` |
| Branch | `master` |
| Health Endpoint | `/api/health` |

---

**Ready to start?** Tell me your Docker Hub username and I'll update the Jenkinsfile for you!
