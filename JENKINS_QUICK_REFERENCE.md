# ⚡ Jenkins Quick Reference

One-page guide for your Jenkins pipeline.

---

## 🎯 What You Need to Provide

### 1. Docker Hub Username
**Example:** `pavanakkineni`, `john_doe`, etc.
**Where:** https://hub.docker.com (top-right corner)

### 2. Docker Hub Access Token
**How to get:**
1. Docker Hub → Account Settings → Security
2. New Access Token → Name: `jenkins-pipeline`
3. Copy token (starts with `dckr_pat_...`)

---

## 📝 Files I Updated

### 1. `Jenkinsfile` (Main pipeline - Windows compatible)
- ✅ Fixed for Windows (uses `bat` instead of `sh`)
- ✅ Fixed branch name (`master` instead of `main`)
- ✅ Fixed Docker Hub registry
- ⚠️ **YOU MUST UPDATE:** Line 6 - Add your Docker Hub username

### 2. `Jenkinsfile.simple` (Beginner-friendly version)
- ✅ Simplified stages
- ✅ No advanced features
- ✅ Easier to debug
- ⚠️ **YOU MUST UPDATE:** Line 8 - Add your Docker Hub username

### 3. Documentation Created
- ✅ `JENKINS_SETUP_CHECKLIST.md` - What you need
- ✅ `JENKINS_DEPLOYMENT_STEPS.md` - Complete walkthrough
- ✅ `JENKINS_QUICK_REFERENCE.md` - This file

---

## 🔧 Quick Setup (5 Steps)

### Step 1: Install Jenkins
```powershell
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

### Step 2: Get Admin Password
```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Step 3: Open Jenkins
- Go to: http://localhost:8080
- Paste password
- Install suggested plugins

### Step 4: Add Docker Hub Credentials
1. Manage Jenkins → Credentials → Global → Add Credentials
2. **Kind:** Username with password
3. **Username:** Your Docker Hub username
4. **Password:** Your Docker Hub token
5. **ID:** `dockerhub-credentials` (EXACTLY this!)

### Step 5: Create Pipeline
1. New Item → Name: `Trading-Analytics-Pipeline` → Pipeline
2. **Pipeline → Definition:** Pipeline script from SCM
3. **SCM:** Git
4. **Repository URL:** `https://github.com/PavanAkkineni/TradeSignal.git`
5. **Branch:** `*/master`
6. **Script Path:** `Jenkinsfile`
7. Save

---

## ✏️ Update Jenkinsfile

### Open: `Jenkinsfile`

### Find line 6:
```groovy
DOCKER_HUB_USERNAME = 'YOUR_DOCKERHUB_USERNAME'
```

### Replace with YOUR username:
```groovy
DOCKER_HUB_USERNAME = 'pavanakkineni'  // Use YOUR actual username
```

### Save, commit, push:
```powershell
git add Jenkinsfile
git commit -m "Add Docker Hub username"
git push origin master
```

---

## 🚀 Run Pipeline

### Option 1: Manual
1. Go to Jenkins Dashboard
2. Click `Trading-Analytics-Pipeline`
3. Click "Build Now"

### Option 2: Automatic
1. Push any change to GitHub
2. Jenkins auto-builds (after 5 min or webhook)

---

## 📊 Pipeline Stages

```
✅ Checkout Code         (~10s)
✅ Environment Setup     (~5s)
✅ Install Dependencies  (~2-3min)
✅ Run Tests            (~30s)
✅ Security Scan        (~1min)
✅ Build Docker Image   (~2-3min)
✅ Test Docker Image    (~1min)
✅ Push to Docker Hub   (~2-3min)
✅ Deploy Production    (manual approval)

Total: ~10-15 minutes
```

---

## ✅ Verify Success

### Jenkins:
- Build shows green checkmark ✅
- Console: "Pipeline completed successfully!"

### Docker Hub:
- Go to: `https://hub.docker.com/r/YOUR_USERNAME/trading-analytics-platform`
- See images with tags: `latest`, `1`, `2`, etc.

### Local:
```powershell
docker images | findstr trading-analytics-platform
```

---

## 🚨 Common Issues & Fixes

### "Docker Hub credentials invalid"
```
Fix: Check credential ID is EXACTLY: dockerhub-credentials
     Verify token is correct (dckr_pat_...)
```

### "Cannot connect to Docker daemon"
```
Fix: Ensure Docker Desktop is running
     Or: docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### "Python not found"
```
Fix: Ensure Python is in system PATH
     Or: Add Python in Jenkins → Manage Jenkins → Tools
```

### "Health check failed"
```
Fix: Check .env file has all API keys
     Test manually: docker run -d -p 8001:8000 --env-file .env YOUR_IMAGE
     Check logs: docker logs test-container
```

---

## 🎓 Which Jenkinsfile to Use?

### Use `Jenkinsfile` (default) if:
- ✅ You want full CI/CD pipeline
- ✅ You need security scans
- ✅ You want staging + production environments
- ✅ You're comfortable with complexity

### Use `Jenkinsfile.simple` if:
- ✅ You're learning Jenkins
- ✅ You want quick builds
- ✅ You don't need advanced features
- ✅ You want easier debugging

**To switch:**
```powershell
# Use simplified version
mv Jenkinsfile Jenkinsfile.full
mv Jenkinsfile.simple Jenkinsfile
git add .
git commit -m "Use simplified Jenkinsfile"
git push
```

---

## 📋 Checklist

Before running pipeline:
- [ ] Docker Desktop running
- [ ] Jenkins running (http://localhost:8080)
- [ ] Docker Hub account created
- [ ] Docker Hub credentials added to Jenkins (ID: `dockerhub-credentials`)
- [ ] Jenkinsfile updated with your username (line 6)
- [ ] Pipeline created in Jenkins
- [ ] Repository URL correct
- [ ] Branch set to `master`

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| Jenkins Dashboard | http://localhost:8080 |
| Docker Hub | https://hub.docker.com |
| Your GitHub Repo | https://github.com/PavanAkkineni/TradeSignal |
| Docker Hub Images | https://hub.docker.com/r/YOUR_USERNAME/trading-analytics-platform |

---

## 📞 What to Tell Me

To complete the setup, provide:

1. **Your Docker Hub username**
   - Example: `pavanakkineni`
   - I'll update the Jenkinsfile for you

2. **Any errors you encounter**
   - Copy the error message
   - I'll help you fix it

---

## 🎉 After First Successful Build

You'll have:
- ✅ Automated testing on every commit
- ✅ Docker images on Docker Hub
- ✅ Version history (build 1, 2, 3...)
- ✅ Easy rollback (use older build number)
- ✅ Professional CI/CD pipeline

**Your image will be:**
```
docker pull YOUR_USERNAME/trading-analytics-platform:latest
docker run -d -p 8000:8000 --env-file .env YOUR_USERNAME/trading-analytics-platform:latest
```

---

## 💡 Pro Tips

1. **Use simplified Jenkinsfile first** - easier to debug
2. **Check console output** - shows exactly what's happening
3. **Test Docker Hub login manually** - before running pipeline
4. **Keep Docker Desktop running** - Jenkins needs it
5. **Start with manual builds** - before setting up webhooks

---

**Ready?** Just tell me your Docker Hub username! 🚀
