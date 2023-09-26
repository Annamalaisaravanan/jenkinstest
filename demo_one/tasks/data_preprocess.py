import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
import boto3
import yaml
import pickle
from pyspark.sql import SparkSession
from databricks import feature_store
from mlflow.tracking.client import MlflowClient
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from databricks.feature_store import feature_table, FeatureLookup
from databricks.feature_store.online_store_spec import AmazonDynamoDBSpec
from pyspark.dbutils import DBUtils
import mlflow
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, auc, roc_curve
import json


from demo_one.utils import random_string, feature_store_create, preprocess
from demo_one.utils import push_df_to_s3, mlflow_call_endpoint, read_data_from_s3, read_secrets

import warnings
warnings.filterwarnings('ignore')


with open('config.yml', 'r') as file:
    configure = yaml.safe_load(file)



def Client():
  return mlflow.tracking.MlflowClient()
host_creds = Client()._tracking_client.store.get_host_creds()


fs = feature_store.FeatureStoreClient()

spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()
dbutils = DBUtils(spark)

aws_access_key, aws_secret_key, db_token = read_secrets(dbutils,'anna-scope',['aws_access_key','aws_secret_key','databricks-token'])


class DataPrep():
    
    def load_data(self, table_name, lookup_key,target, inference_data_df):
                    
                    model_feature_lookups = [FeatureLookup(table_name=table_name, lookup_key=lookup_key)]
                
                    # fs.create_training_set looks up features in model_feature_lookups that match the primary key from inference_data_d
                    training_set = fs.create_training_set(inference_data_df, model_feature_lookups, label=target,exclude_columns=lookup_key)
                    training_pd = training_set.load_df().toPandas()
                
                    # Create train and test datasets
                    X = training_pd.drop(target, axis=1)
                    y = training_pd[target]
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=configure['ModelTraining']['test_split'], random_state=42)

                    X_train_pre, X_val, y_train_pre, y_val = train_test_split(X_train, y_train, test_size=configure['ModelTraining']['validation_split'], random_state=43)
                    return X_train_pre, X_test, y_train_pre, y_test, X_val, y_val, training_set

    def train_model(self, X_train, X_test, y_train, y_test, training_set, fs,client):
                        
                        exp_run_name = random_string(configure['Mlflow']['run_name'])

                        
                        mlflow.set_experiment(configure['Mlflow']['experiment_name'])
                        with mlflow.start_run(run_name= exp_run_name) as run:
                        
                                LR_Classifier = LogisticRegression(
                                                        C=configure['LogisticReg']['C'],
                                                        penalty=configure['LogisticReg']['penalty'],
                                                        solver=configure['LogisticReg']['solver'],
                                                        class_weight=configure['LogisticReg']['class_weight']
                                                        )
                                LR_Classifier.fit(X_train, y_train)
                                y_pred = LR_Classifier.predict(X_test)
                        
                                fpr, tpr, threshold = roc_curve(y_test,y_pred)
                                roc_auc = auc(fpr, tpr)
                                f1_train = f1_score(y_test,y_pred)
                                mlflow.log_metric("train_f1score",f1_train)
                                mlflow.log_metric("roc_auc",roc_auc)
                        
                                fs.log_model(
                                model=LR_Classifier,
                                artifact_path="health_prediction",
                                flavor=mlflow.sklearn,
                                training_set=training_set,
                                registered_model_name=configure['Model_registry_name'],
                                )
    
    def Model(self,df_input):
                
                df_input_spark = spark.createDataFrame(df_input)

                inference_data_df = df_input_spark.select(configure['feature-store']['lookup_key'], configure['features']['target'])

                X_train, X_test, y_train, y_test, X_val, y_val, training_set = self.load_data(configure['feature-store']['table_name'], configure['feature-store']['lookup_key'],configure['features']['target'],inference_data_df)
        
                client = MlflowClient()
               
                self.train_model(X_train, X_val, y_train, y_val, training_set, fs,client)

                rows = X_test.count()[0]
                random_patient_ids = np.random.randint(10000, 99999, size=rows)

                X_test['PATIENT_ID'] = random_patient_ids

                spark_test = spark.createDataFrame(X_test)

                test_pred = fs.score_batch("models:/pharma_model/latest", spark_test)

                ans_test = test_pred.toPandas()

                y_test = y_test.reset_index()

                y_test.drop('index',axis=1,inplace=True)

                ans_test['actual'] = y_test

                output_df = ans_test[['prediction','actual']]

                print(confusion_matrix(output_df['prediction'],output_df['actual']))

                print(accuracy_score(output_df['prediction'],output_df['actual'])*100)

                print("Model training is done")

    def webhook(self):

        lists = {
            "model_name":"pharma_model",
            "events": "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"
        }
        js_list_res = mlflow_call_endpoint(host_creds,'registry-webhooks/list', 'GET', json.dumps(lists))

        print(js_list_res)
        if js_list_res:
              print("Webhook is already created")

        else:
                diction = {
                                "job_spec": {
                                    "job_id": configure['deployment-pipeline']['job_id'],
                                    "access_token": db_token,
                                    "workspace_url": configure['databricks-url']
                                },
                                "events": [
                                    "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"
                                ],
                                "model_name": "pharma_model",
                                "description": "Webhook for Deployment Pipeline",
                                "status": "ACTIVE"
                                }

                job_json= json.dumps(diction)
                js_res = mlflow_call_endpoint(host_creds,'registry-webhooks/create', 'POST', job_json)
                print(js_res)

                print("Webhook Created for deployment job")

    

    def _preprocess_data(self):

        s3 = boto3.resource("s3",aws_access_key_id=aws_access_key, 
                aws_secret_access_key=aws_secret_key, 
                region_name='ap-south-1')
        try:
                
                new_df = fs.read_table(configure['feature-store']['table_name'])

                df_input = read_data_from_s3(s3,configure['s3']['bucket_name'],configure['preprocessed']['preprocessed_df_path'])

                return df_input 
        except:

                df_input = read_data_from_s3(s3,configure['s3']['bucket_name'],configure['s3']['file_path'])
            
                df_input = df_input.reset_index()
        
                # numerical_cols = configure['features']['numerical_cols']
                
                # categorical_cols = configure['features']['categorical_cols']

                # df_encoded = df_input.copy()
                # for col in df_encoded.select_dtypes(include=['object']):
                #     df_encoded[col] = df_encoded[col].astype('category').cat.codes

                # ordinal_cols = configure['features']['ordinal_cols']

                # # Columns for one-hot encoding
                # onehot_cols = configure['features']['onehot_cols']
                
                # ordinal_encoder = OrdinalEncoder()
                # df_input[ordinal_cols] = ordinal_encoder.fit_transform(df_input[ordinal_cols])

                # onehot_encoded_data = pd.get_dummies(df_input[onehot_cols], drop_first=True)


                # df_input = pd.concat([df_input.drop(onehot_cols, axis=1), onehot_encoded_data], axis=1)

                # encoders_dict = {
                #         'ordinal_encoder': ordinal_encoder,
                #         # Add more encoders as needed
                #     }
                
                # pickled_data = pickle.dumps(encoders_dict)
                # pkl_path = configure['preprocessed']['encoders_path']
                
                # df_input.rename(columns = {'index':'PATIENT_ID','Height_(cm)':'Height','Weight_(kg)':'Weight',
                # 'Diabetes_No, pre-diabetes or borderline diabetes':'Diabetes_No_pre-diabetes_or_borderline_diabetes',
                # 'Diabetes_Yes, but female told only during pregnancy':'Diabetes_Yes_but_female_told_only_during_pregnancy'}, inplace = True)


                # spark.sql(f"CREATE DATABASE IF NOT EXISTS {configure['feature-store']['DB']}")
                # print('pharma db created')
                # # Create a unique table name for each run. This prevents errors if you run the notebook multiple times.
                # table_name = configure['feature-store']['table_name']
                # print(table_name)

                # df_feature = df_input.drop(configure['features']['target'],axis=1)

                df_feature, df_input = preprocess(spark,configure,df_input)

            
                push_status = push_df_to_s3(df_input,configure['s3']['bucket_name'],configure['preprocessed']['preprocessed_df_path'],s3)
                print(push_status)


                #feature store function

                df_spark = spark.createDataFrame(df_feature)

                fs_status = feature_store_create(fs,configure['feature-store']['table_name'],configure,df_spark)
                print(f"The Feature store status: {fs_status}")

                online_store_spec = AmazonDynamoDBSpec(
                    region="us-west-2",
                    write_secret_prefix="feature-store-example-write/dynamo",
                    read_secret_prefix="feature-store-example-read/dynamo",
                    table_name = configure['feature-store']['online_table_name']
                    )
                    
                fs.publish_table(configure['feature-store']['table_name'], online_store_spec)

                print("Feature store published")
                
                return df_input
                

            

    def launch(self):
         
        processed_data =  self._preprocess_data()
        self.Model(processed_data)
        self.webhook()

   

def entrypoint():  
    
    task = DataPrep()
    task.launch()


if __name__ == '__main__':
    entrypoint()