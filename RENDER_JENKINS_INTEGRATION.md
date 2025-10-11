# 🚀 Jenkins → Render Deployment Integration

Complete guide to deploy your app to Render cloud through Jenkins pipeline.

---

## 🎯 What You'll Achieve

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE CI/CD FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

YOU PUSH CODE TO GITHUB
         │
         ▼
JENKINS PIPELINE RUNS
         ├─> Checkout code
         ├─> Install dependencies
         ├─> Run tests
         ├─> Security scan
         ├─> Build Docker image
         ├─> Test Docker image
         ├─> Push to Docker Hub
         └─> Deploy to local production
         │
         ▼
JENKINS TRIGGERS RENDER DEPLOYMENT  ← NEW STAGE!
         │
         ▼
RENDER BUILDS & DEPLOYS TO CLOUD
         │
         ▼
✅ YOUR WEBSITE IS LIVE AT:
   https://trading-analytics-platform.onrender.com
```

---

## 📋 Step-by-Step Setup

### **Step 1: Create Render Web Service**

#### 1.1 Sign Up for Render
1. Go to: https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub account
4. Authorize Render to access your repositories

#### 1.2 Create New Web Service
1. Click **"New"** → **"Web Service"**
2. Connect your repository:
   - Select: `PavanAkkineni/TradeSignal`
   - Click "Connect"

#### 1.3 Configure Web Service
```
Name: trading-analytics-platform
Environment: Docker
Region: Choose closest to you (e.g., Oregon, Frankfurt)
Branch: master
Dockerfile Path: ./Dockerfile  (should auto-detect)
```

#### 1.4 Add Environment Variables
Click "Advanced" and add these environment variables:

```
GEMINI_API_KEY = your-gemini-api-key
ALPHA_VANTAGE_API_KEY = your-alpha-vantage-key
NEWS_API_KEY = your-news-api-key
FINNHUB_API_KEY = your-finnhub-key (if you have it)
POLYGON_API_KEY = your-polygon-key (if you have it)
```

**⚠️ Important:** Copy these from your `.env` file

#### 1.5 Configure Plan
```
Instance Type: Free (or upgrade if needed)
Auto-Deploy: OFF  ← IMPORTANT! We'll deploy via Jenkins
```

**Why turn off Auto-Deploy?**
- Jenkins will control when deployments happen
- Prevents duplicate deployments
- Maintains CI/CD pipeline control

#### 1.6 Create Web Service
1. Click **"Create Web Service"**
2. Wait for initial deployment (5-10 minutes)
3. Your app will be live at: `https://trading-analytics-platform.onrender.com`

---

### **Step 2: Get Render Deploy Hook**

#### 2.1 Navigate to Settings
1. Go to your Render dashboard
2. Click on your web service: `trading-analytics-platform`
3. Go to **"Settings"** tab

#### 2.2 Find Deploy Hook
1. Scroll down to **"Deploy Hook"** section
2. You'll see a URL like:
   ```
   https://api.render.com/deploy/srv-xxxxxxxxxxxxx?key=xxxxxxxxxxxxxx
   ```
3. Click **"Copy"** to copy the full URL

**⚠️ IMPORTANT:**
- This URL is secret - treat it like a password!
- Anyone with this URL can trigger deployments
- Never commit it to GitHub

---

### **Step 3: Add Deploy Hook to Jenkins**

#### 3.1 Open Jenkins Credentials
1. Go to Jenkins: http://localhost:8080
2. Click **"Manage Jenkins"**
3. Click **"Credentials"**
4. Click **"System"**
5. Click **"Global credentials (unrestricted)"**
6. Click **"Add Credentials"**

#### 3.2 Add Render Deploy Hook
```
Kind: Secret text
Scope: Global
Secret: [Paste your Render Deploy Hook URL here]
ID: render-deploy-hook  ← MUST BE EXACTLY THIS!
Description: Render Deploy Hook for trading-analytics-platform
```

**Example Secret:**
```
https://api.render.com/deploy/srv-xxxxxxxxxxxxx?key=xxxxxxxxxxxxxx
```

7. Click **"Create"**

---

### **Step 4: Verify Credentials in Jenkins**

You should now have these credentials:

| ID | Type | Description |
|----|------|-------------|
| `dockerhub-credentials` | Username with password | Docker Hub login |
| `render-deploy-hook` | Secret text | Render deployment trigger |

**To verify:**
1. Go to: Manage Jenkins → Credentials
2. Check both credentials are listed
3. IDs must match exactly (case-sensitive!)

---

### **Step 5: Commit and Push Updated Jenkinsfile**

I've already updated your Jenkinsfile with the new Render deployment stage.

```powershell
# Commit the changes
git add Jenkinsfile
git commit -m "Add Render cloud deployment to Jenkins pipeline"
git push origin master
```

---

### **Step 6: Trigger Jenkins Build**

#### Option A: Manual Trigger
1. Go to Jenkins: http://localhost:8080
2. Click on `Trading-Analytics-Pipeline`
3. Click **"Build Now"**
4. Watch the stages execute

#### Option B: Automatic Trigger
- Push any change to GitHub
- Jenkins will auto-build after ~5 minutes (or immediately if webhook is set up)

---

## 📊 New Pipeline Flow

Your updated pipeline now has **13 stages**:

```
1. ✅ Checkout Code              (~10s)
2. ✅ Environment Setup           (~5s)
3. ✅ Install Dependencies        (~2-3min)
4. ✅ Run Tests                   (~30s)
5. ✅ Security Scan               (~1min)
6. ✅ Build Docker Image          (~2-3min)
7. ✅ Test Docker Image           (~1min)
8. ✅ Push to Docker Hub          (~2-3min)
9. ⏸️  Deploy to Staging          (SKIPPED - develop branch only)
10. ⏸️ Deploy to Production       (WAITS for manual approval)
    │
    ├─> Click "Deploy" button
    │
11. ✅ Deploy to Production       (~1min)
12. ✅ Deploy to Render           (~5-10s)  ← NEW STAGE!
    │
    └─> Triggers Render deployment
        │
        ▼
    RENDER BUILDS & DEPLOYS (5-10min)
        │
        ▼
    ✅ LIVE at https://trading-analytics-platform.onrender.com
```

---

## 🎯 What Happens in the Render Stage

### Stage 12: Deploy to Render

```bash
# Jenkins executes:
curl -X POST "https://api.render.com/deploy/srv-xxxxx?key=xxxxx"

# Render responds with:
HTTP 200 OK  ← Deployment triggered!

# Jenkins shows:
✅ Render deployment triggered successfully!
🚀 Your app will be live at: https://trading-analytics-platform.onrender.com
⏳ Deployment typically takes 5-10 minutes
📊 Monitor progress at: https://dashboard.render.com
```

### What Render Does (After Jenkins Triggers):

```
1. Render receives deployment trigger
   │
2. Pulls latest code from GitHub (master branch)
   │
3. Builds Docker image
   ├─> Reads Dockerfile
   ├─> Installs dependencies
   └─> Creates container
   │
4. Runs health check
   ├─> Sends GET request to your app
   └─> Waits for HTTP 200 response
   │
5. Zero-downtime deployment
   ├─> Keeps old version running
   ├─> Starts new version
   ├─> Runs health checks on new version
   ├─> Routes 100% traffic to new version
   └─> Stops old version
   │
6. ✅ Deployment complete!
   └─> https://trading-analytics-platform.onrender.com is live
```

---

## ✅ Verify Deployment

### Check Jenkins
1. Go to build console output
2. Look for stage "Deploy to Render"
3. Should see:
   ```
   ✅ Render deployment triggered successfully!
   🚀 Your app will be live at: https://trading-analytics-platform.onrender.com
   ```

### Check Render Dashboard
1. Go to: https://dashboard.render.com
2. Click on `trading-analytics-platform`
3. You'll see:
   ```
   Status: Deploying... 
   └─> Building
   └─> Deploying
   └─> Live ✅
   ```

### Test Your Website
```bash
# Health check
curl https://trading-analytics-platform.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-05T04:50:00.000Z"
}
```

### Visit in Browser
```
https://trading-analytics-platform.onrender.com
```

You should see your trading analytics dashboard!

---

## 🚨 Troubleshooting

### Issue 1: "render-deploy-hook not found"

**Error in Jenkins:**
```
groovy.lang.MissingPropertyException: No such property: render-deploy-hook
```

**Solution:**
1. Check credential ID is EXACTLY: `render-deploy-hook`
2. Go to: Manage Jenkins → Credentials
3. Verify it exists
4. ID must match (case-sensitive!)

---

### Issue 2: "Failed to trigger Render deployment. HTTP Status: 401"

**Cause:** Invalid Deploy Hook URL

**Solution:**
1. Go to Render dashboard
2. Settings → Deploy Hook
3. Copy the FULL URL (including `?key=...`)
4. Update Jenkins credential with new URL

---

### Issue 3: "Failed to trigger Render deployment. HTTP Status: 404"

**Cause:** Web service doesn't exist or was deleted

**Solution:**
1. Go to Render dashboard
2. Verify web service exists
3. Get new Deploy Hook URL
4. Update Jenkins credential

---

### Issue 4: Render deployment stuck at "Building"

**Cause:** Build error in Dockerfile or missing dependencies

**Solution:**
1. Go to Render dashboard → Logs
2. Check build logs for errors
3. Common issues:
   - Missing packages in `requirements.txt`
   - Syntax errors in Dockerfile
   - Missing environment variables

---

### Issue 5: Render health check failing

**Error in Render:**
```
Health check failed: GET / returned 404
```

**Solution:**

Update `render.yaml` to use correct health check path:
```yaml
healthCheckPath: /api/health  # Change from / to /api/health
```

Or remove health check temporarily:
```yaml
# healthCheckPath: /  # Comment out
```

---

## 🎓 Understanding the Integration

### Jenkins's Role:
```
✅ Builds Docker image
✅ Runs tests
✅ Pushes to Docker Hub
✅ Deploys locally (optional)
✅ Triggers Render deployment  ← Just triggers!
```

### Render's Role:
```
✅ Receives trigger from Jenkins
✅ Pulls code from GitHub
✅ Builds Docker image (independent of Jenkins)
✅ Deploys to cloud
✅ Manages hosting, scaling, HTTPS
```

### Why This Setup?

**Pros:**
- ✅ Single source of truth (GitHub)
- ✅ Jenkins controls when deployments happen
- ✅ Consistent build process
- ✅ Easy rollbacks (use different build number)
- ✅ Production-ready CI/CD

**Cons:**
- ⚠️ Render builds its own image (not using Jenkins's Docker Hub image)
- ⚠️ Two separate build processes
- ⚠️ Slightly longer deployment time

---

## 🚀 Alternative: Deploy Docker Hub Image to Render

If you want Render to use the exact image Jenkins built:

### Option A: Use Docker Hub Image

Update `render.yaml`:
```yaml
services:
  - type: web
    name: trading-analytics-platform
    env: docker
    image:
      url: docker.io/pavanakkineni/trading-analytics-platform:latest
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      # ... other env vars
```

**Pros:**
- Uses exact same image Jenkins tested
- Faster Render deployments (no build needed)
- Single build process

**Cons:**
- Need to update image URL for each build
- Requires Docker Hub credentials in Render

---

## 📊 Complete Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR COMPLETE CI/CD PIPELINE                     │
└─────────────────────────────────────────────────────────────────────┘

                         YOU PUSH CODE
                               │
                               ▼
                    ┌──────────────────────┐
                    │   GitHub Repository   │
                    │   (master branch)     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   JENKINS PIPELINE   │
                    └──────────┬───────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Test & Build   │  │  Push to Docker  │  │ Trigger Render  │
│  (Stages 1-7)   │  │  Hub (Stage 8)   │  │ (Stage 12)      │
└────────┬────────┘  └────────┬─────────┘  └────────┬────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ Image on        │  │ Image on         │  │ Render receives │
│ Jenkins server  │  │ Docker Hub       │  │ webhook         │
└─────────────────┘  └──────────────────┘  └────────┬────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────┐
                                          │ Render builds &  │
                                          │ deploys to cloud │
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │  ✅ WEBSITE LIVE │
                                          │  ON THE CLOUD!   │
                                          └──────────────────┘
                            https://trading-analytics-platform.onrender.com
```

---

## ✅ Final Checklist

Before running your pipeline, verify:

- [ ] Render web service created
- [ ] Auto-Deploy turned OFF in Render
- [ ] Environment variables added to Render
- [ ] Deploy Hook URL copied from Render
- [ ] `render-deploy-hook` credential added to Jenkins (EXACT ID!)
- [ ] `dockerhub-credentials` credential added to Jenkins
- [ ] Updated Jenkinsfile committed and pushed
- [ ] Jenkins pipeline exists

---

## 🎯 Expected Timeline

```
Total Pipeline Duration: ~15-20 minutes

Jenkins Pipeline:        ~10-15 minutes
├─ Checkout              10s
├─ Setup                 5s
├─ Dependencies          2-3min
├─ Tests                 30s
├─ Security              1min
├─ Build Image           2-3min
├─ Test Image            1min
├─ Push to Docker Hub    2-3min
├─ Deploy Local          1min
└─ Trigger Render        5-10s

Render Deployment:       ~5-10 minutes (in parallel)
├─ Pull code             30s
├─ Build image           3-5min
├─ Deploy                1-2min
└─ Health checks         1min

Your website is LIVE!    ✅
```

---

## 🎉 Success!

Once everything is set up, your workflow becomes:

```bash
# 1. Make changes to your code
vim app/main.py

# 2. Commit and push
git add .
git commit -m "Add new feature"
git push origin master

# 3. Jenkins automatically:
✅ Runs tests
✅ Builds Docker image
✅ Pushes to Docker Hub
✅ Triggers Render deployment

# 4. Render automatically:
✅ Pulls latest code
✅ Builds and deploys
✅ Makes your app live

# 5. Your website is updated!
https://trading-analytics-platform.onrender.com ✅
```

---

## 📞 Next Steps

1. **Set up Render web service** (Step 1)
2. **Get Deploy Hook URL** (Step 2)
3. **Add to Jenkins credentials** (Step 3)
4. **Push updated Jenkinsfile** (Step 5)
5. **Trigger a build** (Step 6)
6. **Watch your app go live!** 🚀

---

**Your complete CI/CD pipeline is now ready! From code to cloud in one push!** 🎉
