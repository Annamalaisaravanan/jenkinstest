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
        stage('Activate venv and run Databricks job') {
            steps {
                script {
                    // Set the path to your virtual environment
                    

                

                    sh '''#!/bin/bash
                          source sample/myenv/bin/activate
                                            
                        '''

                    // Run your Databricks job command here
                    sh "pip install plotly"
                    
                    // Deactivate the virtual environment
                    sh "deactivate"
                }
            }
        }
    }
}