pipeline {
    agent { docker { image 'python' } }
    triggers {
        githubPush()
    }
    stages {

        // stage('Dependencies') {
        //     steps {
        //         sh "chmod 777"
        //         sh 'pip install pandas'
        //     }
        // }
        stage('Python Script') {
            steps {

               sh 'pip --version'
               sh 'python3 app.py'
            }
        }
       
    }
}
