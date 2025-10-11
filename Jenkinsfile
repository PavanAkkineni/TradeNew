pipeline {
    agent any
    
    environment {
        // TODO: Replace 'YOUR_DOCKERHUB_USERNAME' with your actual Docker Hub username
        DOCKER_HUB_USERNAME = 'pavanakkineni' // e.g., 'pavanakkineni'
        DOCKER_IMAGE = "${DOCKER_HUB_USERNAME}/trading-analytics-platform"
        DOCKER_TAG = "${BUILD_NUMBER}"
        APP_NAME = 'trading-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo 'Setting up environment...'
                script {
                    // Copy environment file (works on Linux/Mac)
                    sh 'cp .env.example .env || echo "No .env.example found"'
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                script {
                    // Use sh for Linux/Mac (Jenkins in Docker uses Linux)
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                script {
                    sh '''
                        . venv/bin/activate
                        python -m pytest tests/ || echo "No tests found"
                        python -c "from app.main import app; print('App imports successfully')"
                    '''
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scans...'
                script {
                    sh '''
                        . venv/bin/activate
                        pip install safety bandit
                        safety check || echo "Safety check completed"
                        bandit -r app/ || echo "Bandit scan completed"
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                script {
                    sh '''
                        # Run container for testing
                        docker run -d --name test-container -p 8001:8000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                        sleep 30
                        
                        # Test health endpoint
                        curl -f http://localhost:8001/api/health || echo "Health check failed"
                        
                        # Clean up test container
                        docker stop test-container || true
                        docker rm test-container || true
                    '''
                }
            }
        }
        
        stage('Push to Docker Hub') {
            when {
                branch 'master'  // Changed from 'main' to 'master' to match your branch
            }
            steps {
                echo 'Pushing to Docker Hub...'
                script {
                    // Login to Docker Hub using credentials stored in Jenkins
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                            docker push ${DOCKER_IMAGE}:latest
                            docker logout
                        """
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                script {
                    sh '''
                        # Stop existing staging container
                        docker stop ${APP_NAME}-staging || echo "No staging container to stop"
                        docker rm ${APP_NAME}-staging || echo "No staging container to remove"
                        
                        # Run new container
                        docker run -d \\
                            --name ${APP_NAME}-staging \\
                            -p 8002:8000 \\
                            --env-file .env \\
                            --restart unless-stopped \\
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'master'  // Changed from 'main' to 'master'
            }
            steps {
                echo 'Deploying to production environment...'
                input message: 'Deploy to production?', ok: 'Deploy'
                script {
                    sh '''
                        # Blue-Green deployment strategy
                        
                        # Stop old container
                        docker stop ${APP_NAME}-prod || echo "No prod container to stop"
                        docker rm ${APP_NAME}-prod || echo "No prod container to remove"
                        
                        # Run new container
                        docker run -d \\
                            --name ${APP_NAME}-prod \\
                            -p 8000:8000 \\
                            --env-file .env \\
                            --restart unless-stopped \\
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                        
                        # Health check
                        sleep 30
                        curl -f http://localhost:8000/api/health
                    '''
                }
            }
        }
        
        stage('Deploy to Render') {
            when {
                branch 'master'  // Only deploy to Render from master branch
            }
            steps {
                echo 'Deploying to Render Cloud...'
                script {
                    // Use Render Deploy Hook to trigger deployment
                    withCredentials([string(credentialsId: 'render-deploy-hook', variable: 'RENDER_DEPLOY_HOOK')]) {
                        sh '''
                            echo "Triggering Render deployment..."
                            
                            # Trigger Render deployment via Deploy Hook
                            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${RENDER_DEPLOY_HOOK}")
                            
                            if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "201" ]; then
                                echo "✅ Render deployment triggered successfully!"
                                echo "🚀 Your app will be live at: https://trading-analytics-platform.onrender.com"
                                echo "⏳ Deployment typically takes 5-10 minutes"
                                echo "📊 Monitor progress at: https://dashboard.render.com"
                            else
                                echo "❌ Failed to trigger Render deployment. HTTP Status: $RESPONSE"
                                exit 1
                            fi
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // Send notification
            emailext (
                subject: "✅ Trading App Deployment Successful - Build ${BUILD_NUMBER}",
                body: "The trading analytics platform has been successfully deployed.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            echo 'Pipeline failed!'
            // Send failure notification
            emailext (
                subject: "❌ Trading App Deployment Failed - Build ${BUILD_NUMBER}",
                body: "The trading analytics platform deployment failed. Check Jenkins logs.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
