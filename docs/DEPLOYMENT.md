# 🚀 Deployment Guide

This guide covers different deployment scenarios for the AI-Driven Self-Healing CI/CD Platform.

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- OpenAI API Key
- GitHub Personal Access Token

## 🏠 Local Development Setup

### 1. Quick Setup
```bash
# Clone the repository
git clone https://github.com/Raj-glitch-max/AI-DRIVEN-self-healing-CICD.git
cd AI-DRIVEN-self-healing-CICD

# Run the setup script
python setup.py
```

### 2. Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### 3. Configuration
Edit `.env` file with your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_REPOSITORY=your_username/your_repo_name
```

## 🐳 Docker Deployment

### Local Docker
```bash
# Build the image
docker build -t ai-healer-cicd .

# Run the container
docker run -p 5000:5000 --env-file .env ai-healer-cicd
```

### Docker Compose (Recommended)
```bash
# Start Jenkins and related services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f jenkins
```

## 🏗️ Jenkins Setup

### 1. Access Jenkins
- URL: http://localhost:8080
- Get initial admin password: `docker-compose logs jenkins | grep -A 2 -B 2 password`

### 2. Install Required Plugins
- Git Plugin
- Pipeline Plugin
- Credentials Plugin
- GitHub Plugin

### 3. Configure Credentials
Go to **Manage Jenkins > Credentials > Global**:

1. **OpenAI API Key**
   - Kind: Secret text
   - ID: `openai-api-key`
   - Secret: Your OpenAI API key

2. **GitHub Token**
   - Kind: Secret text
   - ID: `github-token`
   - Secret: Your GitHub personal access token

### 4. Create Pipeline Job
1. New Item → Pipeline
2. Pipeline Definition: Pipeline script from SCM
3. SCM: Git
4. Repository URL: Your GitHub repository
5. Branch: `*/main`
6. Script Path: `Jenkinsfile`

## ☁️ Cloud Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y docker git python3 python3-pip

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Deploy Application
```bash
# Clone repository
git clone https://github.com/Raj-glitch-max/AI-DRIVEN-self-healing-CICD.git
cd AI-DRIVEN-self-healing-CICD

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d
```

#### 3. Security Group Configuration
- Port 8080: Jenkins UI
- Port 5000: Flask Application
- Port 22: SSH access

### Google Cloud Platform

#### 1. Create VM Instance
```bash
# Create instance
gcloud compute instances create ai-healer-vm \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a

# SSH into instance
gcloud compute ssh ai-healer-vm --zone=us-central1-a
```

#### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Azure Container Instances

#### 1. Create Resource Group
```bash
az group create --name ai-healer-rg --location eastus
```

#### 2. Deploy Container
```bash
az container create \
    --resource-group ai-healer-rg \
    --name ai-healer-app \
    --image your-registry/ai-healer-cicd:latest \
    --ports 5000 \
    --environment-variables \
        OPENAI_API_KEY=your_key \
        GITHUB_TOKEN=your_token \
        GITHUB_REPOSITORY=your_repo
```

## 🔧 Production Considerations

### Security
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Enable HTTPS with SSL certificates
- Implement proper authentication and authorization
- Regular security updates

### Monitoring
- Set up application monitoring (Prometheus, Grafana)
- Configure log aggregation (ELK stack)
- Implement health checks and alerting

### Scaling
- Use container orchestration (Kubernetes)
- Implement load balancing
- Auto-scaling based on demand

### Backup & Recovery
- Regular database backups
- Git repository backups
- Configuration backups

## 🚨 Troubleshooting

### Common Issues

#### Jenkins Won't Start
```bash
# Check logs
docker-compose logs jenkins

# Check permissions
sudo chown -R 1000:1000 jenkins_home/

# Restart service
docker-compose restart jenkins
```

#### Healer Agent Fails
```bash
# Check environment variables
env | grep -E "(OPENAI|GITHUB)"

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check logs
tail -f healer.log
```

#### Git Operations Fail
```bash
# Verify git configuration
git config --list

# Test GitHub connectivity
ssh -T git@github.com

# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### Performance Optimization

#### Jenkins
- Increase heap size: `-Xmx2g`
- Use SSD storage
- Optimize build agents

#### Application
- Use gunicorn with multiple workers
- Implement caching
- Optimize database queries

## 📊 Monitoring & Metrics

### Key Metrics to Track
- Healing success rate
- Time to resolution (MTTR)
- Build failure frequency
- API response times
- Resource utilization

### Alerting
Set up alerts for:
- Healing failures
- API rate limits
- High error rates
- Resource exhaustion

## 🔄 Maintenance

### Regular Tasks
- Update dependencies
- Rotate API keys
- Clean up old branches
- Review and optimize prompts
- Monitor costs

### Updates
```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Update dependencies
pip install -r requirements.txt --upgrade
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Create an issue on GitHub
4. Contact the development team

---

**Note**: This platform is designed for demonstration and educational purposes. For production use, implement additional security measures and thorough testing.