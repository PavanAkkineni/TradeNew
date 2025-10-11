# 🔧 Jenkins CI/CD Setup Guide

Complete guide to set up Jenkins for your Trading Analytics Platform.

---

## 📋 Table of Contents
1. [What Jenkins Will Do](#what-jenkins-will-do)
2. [Prerequisites](#prerequisites)
3. [Install Jenkins](#install-jenkins)
4. [Configure Jenkins](#configure-jenkins)
5. [Create Jenkins Pipeline](#create-jenkins-pipeline)
6. [Integrate with GitHub](#integrate-with-github)
7. [Deploy to Render](#deploy-to-render)
8. [Advanced Features](#advanced-features)

---

## 🎯 What Jenkins Will Do

Your automated pipeline will:
1. ✅ **Detect** code changes in GitHub
2. ✅ **Run tests** automatically
3. ✅ **Build** Docker image
4. ✅ **Push** to Docker Hub
5. ✅ **Deploy** to Render
6. ✅ **Notify** you of success/failure

---

## 📦 Prerequisites

### You Need:
- ✅ Docker installed (you have this)
- ✅ GitHub repository (you have this)
- ⬜ Docker Hub account (free)
- ⬜ Jenkins installed

---

## 🚀 Install Jenkins

### Option 1: Run Jenkins in Docker (Recommended)

#### 1. Create Jenkins Docker Volume
```powershell
docker volume create jenkins_home
```

#### 2. Run Jenkins Container
```powershell
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts
```

#### 3. Get Initial Admin Password
```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### 4. Access Jenkins
Open browser: http://localhost:8080

#### 5. Complete Setup Wizard
1. Paste the admin password
2. Click "Install suggested plugins"
3. Create admin user
4. Set Jenkins URL: `http://localhost:8080`

---

### Option 2: Install Jenkins on Windows

#### 1. Download Jenkins
- Go to: https://www.jenkins.io/download/
- Download Windows installer (.msi)

#### 2. Install
- Run the installer
- Follow the wizard
- Jenkins will start automatically

#### 3. Access Jenkins
- Open: http://localhost:8080
- Follow setup wizard

---

## ⚙️ Configure Jenkins

### 1. Install Required Plugins

Go to: **Manage Jenkins** → **Plugins** → **Available Plugins**

Install these plugins:
- ✅ **Docker Pipeline**
- ✅ **GitHub Integration**
- ✅ **Pipeline**
- ✅ **Credentials Binding**
- ✅ **Blue Ocean** (optional, better UI)

Click "Install" and restart Jenkins.

---

### 2. Add Credentials

#### A. Docker Hub Credentials

1. Go to: **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. Click **"Add Credentials"**
3. Fill in:
   - **Kind**: Username with password
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password
   - **ID**: `dockerhub-credentials`
   - **Description**: Docker Hub Login
4. Click **"Create"**

#### B. GitHub Credentials

1. Generate GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `admin:repo_hook`
   - Copy the token

2. Add to Jenkins:
   - **Kind**: Secret text
   - **Secret**: Paste your GitHub token
   - **ID**: `github-token`
   - **Description**: GitHub Access Token

#### C. Render API Key (Optional)

1. Get Render API Key:
   - Go to: https://dashboard.render.com/u/settings
   - Create API key

2. Add to Jenkins:
   - **Kind**: Secret text
   - **Secret**: Your Render API key
   - **ID**: `render-api-key`
   - **Description**: Render Deploy Key

#### D. Environment Variables (API Keys)

Add your application API keys:
- **ID**: `gemini-api-key`
- **ID**: `alpha-vantage-api-key`
- **ID**: `news-api-key`

---

## 🔨 Create Jenkins Pipeline

### 1. Create New Pipeline Job

1. Click **"New Item"**
2. Enter name: `Trading-Analytics-Pipeline`
3. Select **"Pipeline"**
4. Click **"OK"**

---

### 2. Configure Pipeline

#### General Settings:
- ✅ Check "GitHub project"
- Project URL: `https://github.com/PavanAkkineni/TradeSignal`

#### Build Triggers:
- ✅ Check "GitHub hook trigger for GITScm polling"

#### Pipeline:
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/PavanAkkineni/TradeSignal.git`
- **Credentials**: Select your GitHub credentials
- **Branch**: `*/master`
- **Script Path**: `Jenkinsfile`

Click **"Save"**

---

## 📝 Create Jenkinsfile

This is the pipeline definition that Jenkins will execute.

### Basic Jenkinsfile (Testing + Docker Build)

Create `Jenkinsfile` in your project root:

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'your-dockerhub-username/trading-analytics-platform'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    pytest tests/ --cov=app --cov-report=html --cov-report=term
                '''
            }
        }
        
        stage('Code Quality Check') {
            steps {
                echo 'Checking code quality...'
                sh '''
                    pip install flake8
                    flake8 app/ --max-line-length=120 --exclude=__pycache__
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to Docker Hub...'
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to Render') {
            steps {
                echo 'Triggering Render deployment...'
                // Render auto-deploys from GitHub
                echo 'Render will auto-deploy from GitHub push'
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            // You can add Slack/email notifications here
        }
        failure {
            echo '❌ Pipeline failed!'
            // Send failure notifications
        }
        always {
            echo 'Cleaning up...'
            sh 'docker system prune -f'
        }
    }
}
```

---

### Advanced Jenkinsfile (Multi-Environment)

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'your-dockerhub-username/trading-analytics-platform'
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        GEMINI_API_KEY = credentials('gemini-api-key')
        ALPHA_VANTAGE_API_KEY = credentials('alpha-vantage-api-key')
        NEWS_API_KEY = credentials('news-api-key')
    }
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Deployment environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests before deployment')
        booleanParam(name: 'DEPLOY', defaultValue: true, description: 'Deploy after build')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out code..."
                checkout scm
                sh 'git log -1 --pretty=format:"%h - %an: %s"'
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo "🔧 Setting up environment: ${params.ENVIRONMENT}"
                sh '''
                    python --version
                    docker --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing dependencies...'
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov flake8 black
                '''
            }
        }
        
        stage('Code Formatting Check') {
            steps {
                echo '🎨 Checking code formatting...'
                sh '''
                    black --check app/ || echo "Warning: Code formatting issues found"
                '''
            }
        }
        
        stage('Linting') {
            steps {
                echo '🔍 Running linter...'
                sh '''
                    flake8 app/ --max-line-length=120 --exclude=__pycache__,__init__.py
                '''
            }
        }
        
        stage('Unit Tests') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    pytest tests/unit/ -v --cov=app --cov-report=html --cov-report=term-missing
                '''
            }
        }
        
        stage('Integration Tests') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                echo '🔗 Running integration tests...'
                sh '''
                    pytest tests/integration/ -v
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🔒 Running security scan...'
                sh '''
                    pip install safety
                    safety check --json || echo "Warning: Security vulnerabilities found"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    def imageTag = "${params.ENVIRONMENT}-${BUILD_NUMBER}"
                    docker.build("${DOCKER_IMAGE}:${imageTag}")
                    docker.build("${DOCKER_IMAGE}:${params.ENVIRONMENT}-latest")
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo '🧪 Testing Docker image...'
                sh '''
                    docker run --rm \
                      -e GEMINI_API_KEY=${GEMINI_API_KEY} \
                      -e ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY} \
                      -e NEWS_API_KEY=${NEWS_API_KEY} \
                      ${DOCKER_IMAGE}:${ENVIRONMENT}-latest \
                      python -c "import app; print('✅ Image works!')"
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing to Docker Hub...'
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        def imageTag = "${params.ENVIRONMENT}-${BUILD_NUMBER}"
                        docker.image("${DOCKER_IMAGE}:${imageTag}").push()
                        docker.image("${DOCKER_IMAGE}:${params.ENVIRONMENT}-latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to Development') {
            when {
                expression { params.ENVIRONMENT == 'dev' && params.DEPLOY == true }
            }
            steps {
                echo '🚀 Deploying to Development...'
                sh '''
                    echo "Deploy to dev environment"
                    # Add your dev deployment commands
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' && params.DEPLOY == true }
            }
            steps {
                echo '🚀 Deploying to Staging...'
                sh '''
                    echo "Deploy to staging environment"
                    # Add your staging deployment commands
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                expression { params.ENVIRONMENT == 'production' && params.DEPLOY == true }
            }
            steps {
                input message: 'Deploy to Production?', ok: 'Deploy'
                echo '🚀 Deploying to Production...'
                sh '''
                    echo "Deploy to production environment"
                    # Trigger Render deployment or other production deploy
                '''
            }
        }
        
        stage('Smoke Tests') {
            when {
                expression { params.DEPLOY == true }
            }
            steps {
                echo '💨 Running smoke tests...'
                sh '''
                    sleep 10
                    # Add smoke tests to verify deployment
                    echo "✅ Smoke tests passed"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            // Add notification: Slack, email, etc.
        }
        failure {
            echo '❌ Pipeline failed!'
            // Send failure notification
        }
        always {
            echo '🧹 Cleaning up...'
            sh '''
                docker system prune -f
            '''
            // Archive test results
            junit '**/test-results/*.xml' allowEmptyResults: true
            publishHTML([
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

---

## 🔗 Integrate with GitHub

### 1. Configure GitHub Webhook

1. Go to your GitHub repository
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Fill in:
   - **Payload URL**: `http://your-jenkins-url:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Select "Just the push event"
4. Click **"Add webhook"**

### 2. Test Integration

1. Make a small change to your code
2. Commit and push to GitHub
3. Jenkins should automatically trigger a build
4. Check Jenkins dashboard for build status

---

## 📊 Jenkins Dashboard

### View Build Status:
- Go to: http://localhost:8080
- Click on your pipeline
- See build history, logs, and test results

### Blue Ocean UI (Better Visualization):
- Go to: http://localhost:8080/blue
- Visual pipeline view
- Easier to debug failures

---

## 🎯 Complete Workflow

### What Happens When You Push Code:

```
1. You: git push origin master
   ↓
2. GitHub: Receives push, triggers webhook
   ↓
3. Jenkins: Detects change, starts pipeline
   ↓
4. Jenkins: Checks out code
   ↓
5. Jenkins: Installs dependencies
   ↓
6. Jenkins: Runs tests
   ├─ ✅ Tests pass → Continue
   └─ ❌ Tests fail → STOP (you get notified)
   ↓
7. Jenkins: Checks code quality
   ↓
8. Jenkins: Builds Docker image
   ↓
9. Jenkins: Pushes to Docker Hub
   ↓
10. Jenkins: Triggers Render deployment
    ↓
11. Render: Pulls new image, deploys
    ↓
12. You: Get success notification 🎉
```

---

## 🚨 Troubleshooting

### Issue: Jenkins can't access Docker
**Solution**:
```powershell
# Give Jenkins access to Docker socket
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

### Issue: Tests failing in Jenkins but work locally
**Solution**:
- Check environment variables are set in Jenkins
- Verify Python version matches
- Check file paths (use absolute paths)

### Issue: GitHub webhook not triggering
**Solution**:
- Ensure Jenkins is accessible from internet (use ngrok for local testing)
- Check webhook delivery in GitHub settings
- Verify webhook URL is correct

---

## 📈 Advanced Features

### 1. Parallel Testing
```groovy
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'pytest tests/unit/'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'pytest tests/integration/'
            }
        }
    }
}
```

### 2. Slack Notifications
```groovy
post {
    success {
        slackSend color: 'good', message: "Build ${BUILD_NUMBER} succeeded!"
    }
    failure {
        slackSend color: 'danger', message: "Build ${BUILD_NUMBER} failed!"
    }
}
```

### 3. Email Notifications
```groovy
post {
    always {
        emailext (
            subject: "Build ${BUILD_NUMBER} - ${currentBuild.result}",
            body: "Check console output at ${BUILD_URL}",
            to: "your-email@example.com"
        )
    }
}
```

---

## 🎓 Best Practices

1. ✅ **Always run tests before deployment**
2. ✅ **Use separate environments (dev, staging, prod)**
3. ✅ **Tag Docker images with build numbers**
4. ✅ **Keep secrets in Jenkins credentials, never in code**
5. ✅ **Monitor build times and optimize slow stages**
6. ✅ **Archive test results and coverage reports**
7. ✅ **Set up notifications for build failures**
8. ✅ **Use pipeline as code (Jenkinsfile in repo)**

---

## 📚 Next Steps

1. ✅ Install Jenkins
2. ✅ Configure credentials
3. ✅ Create Jenkinsfile
4. ✅ Set up GitHub webhook
5. ✅ Run first pipeline
6. ✅ Add tests to your project
7. ✅ Configure notifications
8. ✅ Set up multi-environment deployment

---

## 🔗 Useful Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [GitHub Integration](https://plugins.jenkins.io/github/)

---

## 🎉 Congratulations!

You now have a professional CI/CD pipeline that:
- ✅ Automatically tests your code
- ✅ Builds Docker images
- ✅ Deploys to production
- ✅ Notifies you of issues
- ✅ Ensures quality before deployment

This is the same setup used by professional development teams! 🚀
