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

//                sh 'pip --version'
//                sh 'python3 app.py'
//             }
//         }
       
//     }
// }

pipeline {
    agent any

    stages {
         stage('Print Root Directory') {
            steps {
                script {
                    def rootDirectory = pwd()
                    echo "Root Directory: ${Home}"
                }
            }
        }
        stage('Activate venv and run Databricks job') {
            steps {
                script {
                    
                    // sh "sudo chmod -R 777"
                    sh "cd /home/ubuntu/sample/myenv"
                

                    // sh '''#!/bin/bash
                    //       source activate                  
                    //     '''

                    // Run your Databricks job command here
                    // sh "pip install plotly"
                    
                    // Deactivate the virtual environment
                    // sh "deactivate"
                }
            }
        }
    }
}
