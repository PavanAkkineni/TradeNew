# 🔧 Jenkins Setup Checklist - What You Need

This document lists everything you need to configure before running your Jenkins pipeline.

---

## 📋 Required Information

### 1. Docker Hub Account (For Image Registry)

**What you need:**
- Docker Hub username
- Docker Hub password or access token

**Where to get it:**
1. Go to: https://hub.docker.com/signup
2. Create free account (if you don't have one)
3. Your username will be something like: `pavanakkineni` or `yourusername`

**How to create access token (recommended over password):**
1. Login to Docker Hub
2. Go to: Account Settings → Security → Access Tokens
3. Click "New Access Token"
4. Name: `jenkins-token`
5. Copy the token (you'll need this in Jenkins)

**Cost:** FREE

---

### 2. GitHub Personal Access Token

**What you need:**
- GitHub username: `PavanAkkineni` ✅ (you have this)
- Personal Access Token (PAT)

**Where to get it:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `jenkins-access`
4. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `admin:repo_hook` (write repo hooks)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

**Cost:** FREE

---

### 3. API Keys (Environment Variables)

**What you need:**
Your existing API keys from `.env` file:

```
GEMINI_API_KEY=your-key-here
ALPHA_VANTAGE_API_KEY=your-key-here
NEWS_API_KEY=your-key-here
FINNHUB_API_KEY=your-key-here (if you have it)
POLYGON_API_KEY=your-key-here (if you have it)
```

**Where to get them:**
- You already have these in your `.env` file ✅
- Just copy them from there

---

### 4. Email Configuration (Optional - for notifications)

**What you need:**
- Your email address
- SMTP server details (if you want email notifications)

**For Gmail:**
```
SMTP Server: smtp.gmail.com
Port: 587
Username: your-email@gmail.com
Password: App-specific password (not your regular password)
```

**How to get Gmail app password:**
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to: App passwords
4. Generate password for "Mail"

**Cost:** FREE

---

### 5. Branch Strategy

**Current setup:**
- Main branch: `master` ✅ (you're using this)

**Jenkins expects:**
- `main` or `master` for production
- `develop` for staging (optional)

**Action needed:**
- Keep using `master` (we'll update Jenkinsfile to match)

---

## 🎯 Updated Configuration Values

Based on your project, here's what to use:

### Docker Configuration:
```groovy
DOCKER_IMAGE = 'pavanakkineni/trading-analytics-platform'
// Replace 'pavanakkineni' with YOUR Docker Hub username
```

### Registry:
```groovy
DOCKER_REGISTRY = 'registry.hub.docker.com'
// This is Docker Hub's registry URL
```

### Branch:
```groovy
branch 'master'  // Your current branch
```

### Health Check Endpoint:
```
http://localhost:8001/api/health  ✅ (Already correct in your app)
```

---

## 📝 Jenkins Credentials to Create

You'll need to add these credentials in Jenkins:

### 1. Docker Hub Credentials
- **ID:** `dockerhub-credentials`
- **Type:** Username with password
- **Username:** Your Docker Hub username
- **Password:** Your Docker Hub token (from step 1)

### 2. GitHub Token
- **ID:** `github-token`
- **Type:** Secret text
- **Secret:** Your GitHub PAT (from step 2)

### 3. API Keys (as separate secrets)
- **ID:** `gemini-api-key`
- **Type:** Secret text
- **Secret:** Your Gemini API key

- **ID:** `alpha-vantage-api-key`
- **Type:** Secret text
- **Secret:** Your Alpha Vantage API key

- **ID:** `news-api-key`
- **Type:** Secret text
- **Secret:** Your News API key

---

## 🚀 Quick Start: Minimal Setup

If you want to start simple, you only NEED:

### Absolutely Required:
1. ✅ Docker Hub account + credentials
2. ✅ GitHub repository (you have this)
3. ✅ Jenkins installed

### Optional (can add later):
- ⬜ Email notifications
- ⬜ Staging environment
- ⬜ Advanced security scans

---

## 📊 Setup Steps Summary

### Step 1: Create Accounts
- [ ] Docker Hub account created
- [ ] Docker Hub access token generated

### Step 2: Generate Tokens
- [ ] GitHub Personal Access Token created
- [ ] Tokens saved securely

### Step 3: Install Jenkins
- [ ] Jenkins running (http://localhost:8080)
- [ ] Required plugins installed

### Step 4: Add Credentials to Jenkins
- [ ] Docker Hub credentials added
- [ ] GitHub token added
- [ ] API keys added

### Step 5: Create Pipeline
- [ ] New pipeline job created
- [ ] Connected to GitHub repository
- [ ] Jenkinsfile detected

### Step 6: Test
- [ ] Manual build triggered
- [ ] Pipeline runs successfully

---

## 🔍 Where to Find Each Piece of Information

| Information | Location | Example |
|-------------|----------|---------|
| Docker Hub Username | https://hub.docker.com | `pavanakkineni` |
| Docker Hub Token | Account Settings → Security | `dckr_pat_xxxxx` |
| GitHub Username | Your profile | `PavanAkkineni` ✅ |
| GitHub Token | Settings → Developer → Tokens | `ghp_xxxxx` |
| API Keys | Your `.env` file | `AIzaSy...` |
| Repository URL | GitHub repo page | `https://github.com/PavanAkkineni/TradeSignal.git` ✅ |

---

## ⚠️ Common Issues & Solutions

### Issue: "Docker Hub credentials invalid"
**Solution:** Use access token, not password

### Issue: "GitHub webhook not working"
**Solution:** Ensure Jenkins is accessible from internet (use ngrok for local testing)

### Issue: "Cannot find Dockerfile"
**Solution:** Jenkinsfile looks in project root - your Dockerfile is there ✅

### Issue: "API keys not found"
**Solution:** Add them as Jenkins credentials, not in .env file

---

## 🎯 Next Steps

1. **Gather all credentials** (use this checklist)
2. **I'll update your Jenkinsfile** with correct values
3. **Install Jenkins** (if not already)
4. **Add credentials to Jenkins**
5. **Run your first pipeline!**

---

## 📞 Ready to Proceed?

Once you have:
- ✅ Docker Hub username
- ✅ Docker Hub token
- ✅ GitHub token (optional for now)

Tell me your Docker Hub username, and I'll update the Jenkinsfile with the correct configuration!
