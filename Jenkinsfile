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

    environment {
        DATABRICKS_HOST = credentials('DATABRICKS_HOST')
        DATABRICKS_TOKEN = credentials('DATABRICKS_TOKEN')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                }
            }
        }
        stage('Set up Python 3.9') {
            steps {
                tool name: 'Python 3.9', type: 'ToolType'
                script {
                    def pythonHome = tool name: 'Python 3.9', type: 'ToolType'
                    env.PATH = "${pythonHome}/bin:${env.PATH}"
                    sh 'python -m pip install --upgrade pip'
                }
            }
        }

        stage('Install dependencies and project in dev mode') {
            steps {
                script {
                    sh 'pip install -e ".[local,test]"'
                }
            }
        }

        stage('Workflow deployment (assets only upload)') {
            steps {
                script {
                    sh 'dbx deploy Hello-world --assets-only'
                }
            }
        }

        stage('Run the workflow in a jobless fashion') {
            steps {
                script {
                    sh 'dbx launch Hello-world --from-assets --trace'
                }
            }
        }
    }
}
