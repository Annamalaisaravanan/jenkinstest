// pipeline {
//     agent { docker { image 'python' } }
//     triggers {
//         githubPush()
//     }
//     stages {

//         stage('Dependencies') {
//             steps {
              
//                 sh 'docker ps'
//             }
//         }
//         stage('Python Script') {
//             steps {

//                sh 'python3 app.py'
//             }
//         }
       
//     }
// }
//
// pipeline {
//     agent any

//     stages {
//          stage('Print Root Directory') {
//             steps {
//                 script {
//                     def rootDirectory = pwd()
//                     echo "Root Directory: ${Home}"
//                 }
//             }
//         }
//         stage('Activate venv and run Databricks job') {
//             steps {
//                 script {
                    
//                     // sh add
//                     sh "source /home/ubuntu/sample/myenv/bin/activate"
                

//                     // Run your Databricks job command here
//                     // sh "pip install -r requirements.txt"

//                     sh "pip list"

//                     sh "python3 app.py"
                  
//                 }
//             }
//         }
//     }
// }



pipeline {
    agent any
    stages {

        stage('Install Dependencies'){
                  steps{
                        script{
                            sh "pip install -r requirements.txt"

                            sh "pip install -U pyopenssl cryptography"
                        }
                  }
        }

      //   stage('Unit Testing'){

      //       steps{
      //              withPythonEnv('/usr/bin/python3.10'){
      //                   sh "pip install -r requirements.txt"
      //                   sh "pytest tests/unit --cov"
      //              }
                  
      //       }
      //   }
        

        stage('Databricks scope creation check'){
             environment {
                  //  host = credentials('DATABRICKS_HOST')
                  //  token = credentials('DATABRICKS_TOKEN')
                  //  aws_access_key= credentials('MY_AWS_ACCESS_KEY')
                  //  aws_secret_key= credentials('MY_AWS_SECRET_KEY')
                  //  c5_access_key = credentials('C5_ACCESS_KEY')
                  //  c5_secret_key = credentials('C5_SECRET_KEY')

                   host = credentials('DATABRICKS_HOST')
                   
                   aws_secret_key= credentials('MY_AWS_SECRET_KEY')
                   
                   c5_secret_key = credentials('C5_SECRET_KEY')
             }

             steps{
              sh 'python3 scope-creation.py'
             }
        }
        stage('Databricks Pipeline'){
              environment {
                host = credentials('DATABRICKS_HOST')
                token = credentials('DATABRICKS_TOKEN')
              }
              steps{
                sh "python3 app.py"
              }
        }
}

// post{
//      failure{
//              sh "python3 remove-scope.py"
//      }
     
// }


}


