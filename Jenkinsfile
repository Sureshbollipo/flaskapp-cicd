/* This is a scripted pipeline in groovy */
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'bollisr/flask-app'
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
                    dockerImage = docker.build "${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                        dockerImage.push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['app-server-ssh-key']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${APP_SERVER} \
                        "docker pull ${DOCKER_IMAGE}:latest && \
                        docker stop flask-app || true && \
                        docker rm flask-app || true && \
                        docker run -d -p 5000:5000 --name flask-app ${DOCKER_IMAGE}:latest"
                    """
                }
            }
        }
    }
}