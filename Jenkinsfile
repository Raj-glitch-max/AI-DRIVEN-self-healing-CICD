pipeline {
    agent any

    environment {
        // Credentials must be added to Jenkins with these IDs
        OPENAI_API_KEY = credentials('openai-api-key')
        GITHUB_TOKEN = credentials('github-token')
        // Set your repository name here
        GITHUB_REPOSITORY = 'Raj-glitch-max/AI-DRIVEN-self-healing-CICD'
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                // Configure git for the agent
                sh 'git config --global user.email "jenkins-bot@example.com"'
                sh 'git config --global user.name "Jenkins Bot"'
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    // Run tests and catch failure so we can proceed to healing
                    // We redirect output to a file for the agent to read
                    def result = sh(script: 'pytest tests/ > test_output.log 2>&1', returnStatus: true)
                    if (result != 0) {
                        currentBuild.result = 'FAILURE'
                        error("Tests failed, triggering self-healing...")
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Build failed. Initiating AI Healer..."
                // Run the healer agent
                sh 'python healer/agent.py test_output.log'
            }
        }
    }
}
