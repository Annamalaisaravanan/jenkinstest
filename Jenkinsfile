pipeline {
    agent {
        docker { image 'python:3' }
    }
    
    triggers {
        githubPush()
    }
    stages {

        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Python Script') {
            steps {

               sh 'pip --version'
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
