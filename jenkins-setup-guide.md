# Jenkins Setup Guide for Trading Analytics Platform

## Prerequisites
- Docker installed and running
- Git repository with your code
- GitHub/GitLab account

## Step 1: Start Jenkins

### Using Docker Compose
```bash
# Navigate to your project directory
cd "c:\Users\admin\Documents\JOB APP\FastAPI\TradeSignal"

# Start Jenkins
docker-compose -f jenkins-docker-compose.yml up -d

# Get initial admin password
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword
```

## Step 2: Initial Jenkins Setup

1. **Access Jenkins**: http://localhost:8080
2. **Unlock Jenkins**: Use the password from step 1
3. **Install Plugins**: Choose "Install suggested plugins"
4. **Create Admin User**: Set up your admin account
5. **Jenkins URL**: Confirm as http://localhost:8080/

## Step 3: Install Required Plugins

Go to **Manage Jenkins > Manage Plugins > Available** and install:
- Docker Pipeline
- Git Plugin
- GitHub Integration Plugin
- Email Extension Plugin
- Blue Ocean (for better UI)
- Pipeline: Stage View Plugin

## Step 4: Configure Docker

1. Go to **Manage Jenkins > Global Tool Configuration**
2. **Docker**: Add Docker installation
   - Name: `docker`
   - Install automatically: ✓
   - Installer: Download from docker.com

## Step 5: Create Pipeline Job

1. **New Item** > **Pipeline** > Name: `trading-analytics-pipeline`
2. **Pipeline** section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your GitHub repo URL
   - Credentials: Add your GitHub credentials
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

## Step 6: Configure Webhooks (Optional)

### GitHub Webhook
1. Go to your GitHub repo **Settings > Webhooks**
2. **Add webhook**:
   - Payload URL: `http://your-server:8080/github-webhook/`
   - Content type: application/json
   - Trigger: Push events

## Step 7: Environment Files

Create environment-specific files:

### .env.dev
```env
ENVIRONMENT=development
ALPHA_VANTAGE_API_KEY=your_dev_key
GEMINI_API_KEY=your_dev_key
DEBUG=true
```

### .env.staging
```env
ENVIRONMENT=staging
ALPHA_VANTAGE_API_KEY=your_staging_key
GEMINI_API_KEY=your_staging_key
DEBUG=false
```

### .env.prod
```env
ENVIRONMENT=production
ALPHA_VANTAGE_API_KEY=your_prod_key
GEMINI_API_KEY=your_prod_key
DEBUG=false
```

## Step 8: Test the Pipeline

1. **Build Now** in Jenkins
2. Monitor the **Blue Ocean** view
3. Check each stage completion
4. Verify deployment at http://localhost:8000

## Step 9: Set Up Notifications

### Email Configuration
1. **Manage Jenkins > Configure System**
2. **E-mail Notification**:
   - SMTP server: smtp.gmail.com
   - Port: 587
   - Use SMTP Authentication: ✓
   - Username: your-email@gmail.com
   - Password: your-app-password

## Monitoring and Maintenance

### Check Logs
```bash
# Jenkins logs
docker logs jenkins-server

# Application logs
docker logs trading-app-prod
```

### Backup Jenkins Configuration
```bash
# Backup Jenkins home
docker exec jenkins-server tar -czf /tmp/jenkins_backup.tar.gz /var/jenkins_home
docker cp jenkins-server:/tmp/jenkins_backup.tar.gz ./jenkins_backup.tar.gz
```

## Troubleshooting

### Common Issues
1. **Docker not found**: Ensure Docker is installed in Jenkins container
2. **Permission denied**: Check file permissions and user context
3. **Port conflicts**: Ensure ports 8080, 8000 are available
4. **Build failures**: Check Jenkinsfile syntax and dependencies

### Useful Commands
```bash
# Restart Jenkins
docker restart jenkins-server

# View Jenkins configuration
docker exec -it jenkins-server bash

# Clean up old builds
docker system prune -f
```
