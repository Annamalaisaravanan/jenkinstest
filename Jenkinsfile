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



// pipeline {
//     agent any
//     stages {

//         stage('Install Requirements'){
//                   steps{
//                         script{
//                             sh "pip install -r requirements.txt"

//                             sh "pip install -U pyopenssl cryptography"
//                         }
//                   }
//         }
//         stage('Python script'){
//               environment {
//                 access_key = credentials('AWS_ACCESS_KEY')
//                 secret_key = credentials('AWS_SECRET_KEY')
//               }
//               steps{
//                 sh "python3 app.py"
//               }
//         }
// }


// }

pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_KEY')
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Use this stage to checkout your code from version control (e.g., Git)
                // Replace this with the appropriate checkout step for your project.
                // For example, you can use 'checkout scm' for a basic Git checkout.
                // Example:
                // checkout scm
            }
        }

        stage('Execute Python Script') {
            steps {
                script {
                    def awsAccessKey = sh(script: 'echo $AWS_ACCESS_KEY_ID', returnStdout: true).trim()
                    def awsSecretKey = sh(script: 'echo $AWS_SECRET_ACCESS_KEY', returnStdout: true).trim()

                    // Execute the Python script with the environment variables set
                    sh """
                    python - <<EOF
                    import os
                    import boto3
                    from io import BytesIO
                    import pandas as pd

                    access_key = '${awsAccessKey}'
                    secret_key = '${awsSecretKey}'

                    print(access_key, secret_key)

                    s3 = boto3.resource("s3", aws_access_key_id=access_key, 
                                          aws_secret_access_key=secret_key, 
                                          region_name='ap-south-1')

                    s3_object_key = 'CVD_cleaned.csv'
                    s3_object = s3.Object('mlflow-artifacts-anna', s3_object_key)

                    print(s3_object)

                    csv_content = s3_object.get()['Body'].read()
                    df_input = pd.read_csv(BytesIO(csv_content))

                    print(df_input.shape)
                    EOF
                    """
                }
            }
        }
    }
}
