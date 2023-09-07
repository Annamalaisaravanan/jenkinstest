pipeline {
    agent { docker { image 'python:3.7.2' } }
    triggers {
        githubPush()
    }
    stages {

        stage('Initialize'){

            steps{
                    def dockerHome = tool 'myDocker'
                    env.PATH = "${dockerHome}/bin:${env.PATH}"
                }

                }

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
