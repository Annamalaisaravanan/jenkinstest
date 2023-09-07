pipeline {
    agent { docker { image 'python' } }
    triggers {
        githubPush()
    }
    stages {

        stage('Dependencies') {
            steps {
              
                sh 'docker ps'
            }
        }
        stage('Python Script') {
            steps {

               sh 'pip --version'
               sh 'python3 app.py'
            }
        }
       
    }
}
