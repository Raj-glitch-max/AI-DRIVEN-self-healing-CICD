pipeline {
    agent any

    environment {
        // Credentials must be added to Jenkins with these IDs
        OPENAI_API_KEY = credentials('openai-api-key')
        GITHUB_TOKEN = credentials('github-token')
        // Set your repository name here (format: owner/repo)
        GITHUB_REPOSITORY = 'Raj-glitch-max/AI-DRIVEN-self-healing-CICD'
        GITHUB_BASE_BRANCH = 'main'
        
        // Healer configuration
        MAX_RETRY_ATTEMPTS = '3'
        HEALING_TIMEOUT = '300'
        LOG_LEVEL = 'INFO'
    }

    options {
        // Keep builds for 30 days
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '50'))
        // Timeout the entire pipeline after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Add timestamps to console output
        timestamps()
    }

    stages {
        stage('Environment Setup') {
            steps {
                script {
                    echo "🚀 AI-Driven Self-Healing CI/CD Pipeline"
                    echo "Repository: ${env.GITHUB_REPOSITORY}"
                    echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                    
                    // Validate required environment variables
                    def requiredVars = ['OPENAI_API_KEY', 'GITHUB_TOKEN', 'GITHUB_REPOSITORY']
                    def missingVars = []
                    
                    requiredVars.each { var ->
                        if (!env."${var}") {
                            missingVars.add(var)
                        }
                    }
                    
                    if (missingVars) {
                        error("❌ Missing required environment variables: ${missingVars.join(', ')}")
                    }
                    
                    echo "✅ Environment validation passed"
                }
            }
        }

        stage('Dependencies Installation') {
            steps {
                script {
                    echo "📦 Installing Python dependencies..."
                    
                    // Check if Python is available
                    sh 'python3 --version || python --version'
                    
                    // Install dependencies with error handling
                    def installResult = sh(
                        script: 'pip3 install -r requirements.txt || pip install -r requirements.txt',
                        returnStatus: true
                    )
                    
                    if (installResult != 0) {
                        error("❌ Failed to install dependencies")
                    }
                    
                    echo "✅ Dependencies installed successfully"
                }
            }
        }

        stage('Git Configuration') {
            steps {
                script {
                    echo "🔧 Configuring Git for AI Healer..."
                    
                    // Configure git for the healer agent
                    sh '''
                        git config --global user.email "ai-healer@cicd.bot"
                        git config --global user.name "AI Healer Bot"
                        git config --global init.defaultBranch main
                    '''
                    
                    // Verify git configuration
                    sh 'git config --list | grep user'
                    
                    echo "✅ Git configuration completed"
                }
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    echo "🧪 Running tests..."
                    
                    // Clean previous test outputs
                    sh 'rm -f test_output.log healer.log'
                    
                    // Run tests and capture output
                    def testResult = sh(
                        script: '''
                            set -o pipefail
                            python -m pytest tests/ -v --tb=short 2>&1 | tee test_output.log
                        ''',
                        returnStatus: true
                    )
                    
                    // Archive test results regardless of outcome
                    archiveArtifacts artifacts: 'test_output.log', allowEmptyArchive: true
                    
                    if (testResult == 0) {
                        echo "✅ All tests passed!"
                        currentBuild.result = 'SUCCESS'
                    } else {
                        echo "❌ Tests failed, triggering self-healing..."
                        currentBuild.result = 'FAILURE'
                        
                        // Verify log file exists and has content
                        def logExists = sh(
                            script: 'test -s test_output.log',
                            returnStatus: true
                        )
                        
                        if (logExists != 0) {
                            error("❌ Test output log is missing or empty")
                        }
                        
                        error("Tests failed - proceeding to healing stage")
                    }
                }
            }
        }

        stage('Application Health Check') {
            when {
                expression { currentBuild.result != 'FAILURE' }
            }
            steps {
                script {
                    echo "🏥 Running application health checks..."
                    
                    // Start the Flask app in background
                    sh '''
                        export FLASK_DEBUG=false
                        python app/main.py &
                        APP_PID=$!
                        echo $APP_PID > app.pid
                        
                        # Wait for app to start
                        sleep 5
                        
                        # Test health endpoint
                        curl -f http://localhost:5000/health || exit 1
                        
                        # Test main endpoint
                        curl -f http://localhost:5000/ || exit 1
                        
                        # Test API endpoints
                        curl -f http://localhost:5000/api/add/2/3 || exit 1
                        
                        # Stop the app
                        kill $APP_PID || true
                        rm -f app.pid
                    '''
                    
                    echo "✅ Application health checks passed"
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "🤖 Build failed - Initiating AI Healer Agent..."
                
                try {
                    // Verify healer prerequisites
                    sh '''
                        echo "Verifying healer prerequisites..."
                        test -f test_output.log || { echo "❌ Test output log missing"; exit 1; }
                        test -s test_output.log || { echo "❌ Test output log is empty"; exit 1; }
                        test -f healer/agent.py || { echo "❌ Healer agent missing"; exit 1; }
                        echo "✅ Prerequisites verified"
                    '''
                    
                    // Run the healer agent with timeout
                    timeout(time: 5, unit: 'MINUTES') {
                        sh '''
                            echo "🔧 Running AI Healer Agent..."
                            cd ${WORKSPACE}
                            python healer/agent.py test_output.log
                        '''
                    }
                    
                    echo "✅ AI Healer completed successfully"
                    
                    // Update build description
                    currentBuild.description = "🤖 AI Healer activated - Check for new PR"
                    
                } catch (Exception e) {
                    echo "❌ AI Healer failed: ${e.getMessage()}"
                    currentBuild.description = "❌ AI Healer failed: ${e.getMessage()}"
                    
                    // Archive healer logs for debugging
                    archiveArtifacts artifacts: 'healer.log', allowEmptyArchive: true
                }
            }
        }
        
        success {
            script {
                echo "🎉 Pipeline completed successfully!"
                currentBuild.description = "✅ All tests passed"
            }
        }
        
        always {
            script {
                // Clean up any background processes
                sh '''
                    if [ -f app.pid ]; then
                        kill $(cat app.pid) || true
                        rm -f app.pid
                    fi
                '''
                
                // Archive important artifacts
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                
                // Clean up temporary files
                sh 'rm -f *.pid'
                
                echo "🧹 Cleanup completed"
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings"
                currentBuild.description = "⚠️ Completed with warnings"
            }
        }
    }
}
