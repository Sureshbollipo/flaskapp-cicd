/* This is a scripted pipeline in groovy */
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'bollisr/flask-app'
        APP_SERVER = 'ubuntu@54.81.106.126'
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