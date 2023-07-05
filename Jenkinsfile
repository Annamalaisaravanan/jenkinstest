pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'echo "Hello World"'
            }
        }
        stage('Upload to AWS') {
            steps {
                withAWS(region: 'ap-south-1', credentials: 'Annamalai') {
                    sh 'echo "Uploading content with AWS creds"'
                    dir('https://github.com/Annamalaisaravanan/jenkinstest') {
                        script {
                            def s3Bucket = 'anna-jenkinsupload'
                            def gitRepoUrl = 'https://github.com/Annamalaisaravanan/jenkinstest.git'
                            def tempFolder = checkout scm
                            sh "aws s3 sync ${tempFolder} s3://${s3Bucket}"
                        }
                    }
                }
            }
        }
    }
}
