pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('DATABRICKS_HOST')
    }
    triggers {
        githubPush()
    }
    stages {

        stage("Environment Screts check"){
            steps{
                 script {
                    def githubToken = env.GITHUB_TOKEN

                    sh "echo 'My GitHub Token: $githubToken'"
                 }
            }
        }
        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Python Script') {
            steps {
               sh 'python3 app.py'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
