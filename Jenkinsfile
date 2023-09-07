pipeline {
    agent { docker { image 'python' } }
    triggers {
        githubPush()
    }
    stages {

        stage('Dependencies') {
            steps {
              
                sh 'sudo -H pip3 install numpy'
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
