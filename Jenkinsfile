pipeline {
    agent { docker { image 'ubuntu-latest' } }
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
