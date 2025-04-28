# flaskapp-cicd

### 1. Develop the Flask Application
**Create project structure:**
```bash
mkdir flask-app && cd flask-app
touch app.py requirements.txt Dockerfile Jenkinsfile
```

**app.py**
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! CI/CD Pipeline Working!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**requirements.txt**
```
flask==2.0.1
```

### 2. Containerize with Docker
**Dockerfile**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

**Build and test locally:**
```bash
docker build -t flask-app .
docker run -p 5000:5000 flask-app
```

### 3. AWS EC2 Infrastructure Setup
**Create two EC2 instances:**
1. **Jenkins Server** (t2.medium, Ubuntu 22.04 LTS)
   - Security Group: Allow SSH(22), HTTP(8080), Custom TCP(5000)
2. **Application Server** (t2.micro, Ubuntu 22.04 LTS)
   - Security Group: Allow SSH(22), HTTP(5000)

**Install Docker on both instances:**
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER # Log out and back in
```

### 4. Jenkins Server Setup
**Install Java & Jenkins:**
```bash
sudo apt update
sudo apt install fontconfig openjdk-21-jre -y
java -version
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc]" \
https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
/etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins -y
sudo systemctl start jenkins
sudo usermod -aG docker jenkins
```

**Initial Jenkins Setup:**
1. Access via `http://<JENKINS_IP>:8080`
2. Get admin password: `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`
3. Install suggested plugins
4. Create admin user

**Install Required Plugins:**
- Docker Pipeline
- GitHub Integration
- SSH Pipeline Steps

### 5. Configure Jenkins Credentials
1. **Docker Hub Credentials:**
   - Add username/password in Jenkins > Credentials > System > Global credentials
   - ID: `dockerhub-creds`

2. **SSH Key for Application Server:**
   - Generate SSH key on Jenkins server: `ssh-keygen -t rsa`
   - Copy public key to App Server: `ssh-copy-id ubuntu@<APP_SERVER_IP>`
   - Add private key to Jenkins credentials (SSH Username with private key)

### 6. Configure GitHub Webhook
1. In GitHub repo > Settings > Webhooks:
   - Payload URL: `http://<JENKINS_IP>:8080/github-webhook/`
   - Content type: application/json
   - Trigger: Just the push event

### 7. Create Jenkins Pipeline
**Jenkinsfile**
```groovy
/* This is a scripted pipeline in groovy */
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'bollisr/flask-app'
        APP_SERVER = 'ubuntu@54.204.179.21'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/Sureshbollipo/flaskapp-cicd.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build "${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['app-server-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${APP_SERVER} \
                        "docker pull ${IMAGE_NAME}:latest && \
                        docker stop flask-app || true && \
                        docker rm flask-app || true && \
                        docker run -d -p 5000:5000 --name flask-app ${IMAGE_NAME}:latest"
                    """
                }
            }
        }
    }
}
```

### 8. Create Jenkins Pipeline Job
1. New Item > Pipeline
2. Pipeline Definition: Pipeline script from SCM
3. Repository URL: Your GitHub repo
4. Script Path: Jenkinsfile
5. Save and run initial build

### 9. Verify Deployment
1. Access application: `http://<APP_SERVER_IP>:5000`
2. Make code change and push to GitHub
3. Jenkins should automatically trigger new build
4. Verify updated application after deployment

### Troubleshooting Tips:
1. Check Jenkins build console output
2. Verify Docker images on both servers: `docker images`
3. Check running containers: `docker ps`
4. Test SSH connection between servers
5. Verify security group rules
6. Check Docker Hub repository for pushed images