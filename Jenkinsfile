pipeline {
    agent any
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
