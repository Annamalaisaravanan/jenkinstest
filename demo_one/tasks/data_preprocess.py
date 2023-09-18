import pandas as pd
import numpy as np
from sklearn import datasets
from demo_one.common import Task
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
import warnings
import os
import boto3
import yaml
import urllib
import pickle
from pyspark.sql import SparkSession
from io import BytesIO
from databricks.feature_store.online_store_spec import AmazonDynamoDBSpec
import uuid

from databricks import feature_store

from sklearn.model_selection import train_test_split

from databricks.feature_store import feature_table, FeatureLookup

import os
import datetime
from pyspark.dbutils import DBUtils

with open('config.yml', 'r') as file:
    configure = yaml.safe_load(file)


#warnings
warnings.filterwarnings('ignore')


class DataPrep(Task):

    def push_df_to_s3(self,df,access_key,secret_key):
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()

            s3 = boto3.resource("s3",aws_access_key_id=access_key, 
                      aws_secret_access_key=secret_key, 
                      region_name='ap-south-1')

            s3_object_key = configure['preprocessed']['preprocessed_df_path'] 
            s3.Object(configure['s3']['bucket_name'], s3_object_key).put(Body=csv_content)

            return {"df_push_status": 'success'}

    
    
    # def load_data(self, table_name, lookup_key, inference_data_df):
    #                 # In the FeatureLookup, if you do not provide the `feature_names` parameter, all features except primary keys are returned
    #                 model_feature_lookups = [FeatureLookup(table_name=table_name, lookup_key=lookup_key)]
                
    #                 # fs.create_training_set looks up features in model_feature_lookups that match the primary key from inference_data_df
    #                 training_set = fs.create_training_set(inference_data_df, model_feature_lookups, label="Heart_Disease_Yes",exclude_columns="PATIENT_ID")
    #                 training_pd = training_set.load_df().toPandas()
                
    #                 # Create train and test datasets
    #                 X = training_pd.drop("Heart_Disease_Yes", axis=1)
    #                 y = training_pd["Heart_Disease_Yes"]
    #                 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #                 X_train_pre, X_val, y_train_pre, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=43)
    #                 return X_train_pre, X_test, y_train_pre, y_test, X_val, y_val, training_set
    #
                    
  

    def _preprocess_data(self):
                
                spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()

                dbutils = DBUtils(spark)

                #aws_access_key = dbutils.secrets.get(scope="secrets-scope", key="aws-access-key")
                #aws_secret_key = dbutils.secrets.get(scope="secrets-scope", key="aws-secret-key")
                
                
                aws_access_key = 'AKIAUJKJ5ZIQGR4MF5V3' #aws_access_key 
                aws_secret_key = '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' #aws_secret_key

                access_key = aws_access_key
                secret_key = aws_secret_key

                print(f"Access key and secret key are {access_key} and {secret_key}")

                
                
                encoded_secret_key = urllib.parse.quote(secret_key,safe="")

                # bucket_name = configure['s3']['bucket_name']
                # mount_name = configure['dbfs']['mount_name']

                # url = 's3a://%s:%s@%s' %(access_key, encoded_secret_key, bucket_name)

                # try:
                #        dbutils.fs.unmount(mount_name)
                
                # except:
                #         print("no s3 is mounted....")

                # try:
                       
                #        dbutils.fs.mount(url,mount_name)
                #        print("try is executed")
                
                # except Exception as e: 
                #         print(f"the error is {e}")
                #         pass


                
                s3 = boto3.resource("s3",aws_access_key_id=aws_access_key, 
                      aws_secret_access_key=aws_secret_key, 
                      region_name='ap-south-1')
                
                bucket_name =  configure['s3']['bucket_name']
                csv_file_key = configure['s3']['file_path']

                s3_object = s3.Object(bucket_name, csv_file_key)
                
                csv_content = s3_object.get()['Body'].read()

                df_input = pd.read_csv(BytesIO(csv_content))

                # spark_data = spark.read.format('csv')\
                #   .option('header','true')\
                #   .option('inferschema','true')\
                #   .load(configure['dbfs']['file_name'])
                
                # df_input = spark_data.toPandas()

                df_input = df_input.reset_index()
        
                numerical_cols = configure['features']['numerical_cols']
                

                categorical_cols = configure['features']['categorical_cols']

                df_encoded = df_input.copy()
                for col in df_encoded.select_dtypes(include=['object']):
                    df_encoded[col] = df_encoded[col].astype('category').cat.codes

                ordinal_cols = configure['features']['ordinal_cols']

                # Columns for one-hot encoding
                onehot_cols = configure['features']['onehot_cols']
                
                ordinal_encoder = OrdinalEncoder()
                df_input[ordinal_cols] = ordinal_encoder.fit_transform(df_input[ordinal_cols])

                onehot_encoded_data = pd.get_dummies(df_input[onehot_cols], drop_first=True)


                df_input = pd.concat([df_input.drop(onehot_cols, axis=1), onehot_encoded_data], axis=1)

                encoders_dict = {
                        'ordinal_encoder': ordinal_encoder,
                        # Add more encoders as needed
                    }
                
                pickled_data = pickle.dumps(encoders_dict)
                pkl_path = configure['preprocessed']['encoders_path']
                #s3.Object(bucket_name, pkl_path).put(Body=pickled_data)
                # push_status = self.push_df_to_s3(df_input)
                # print(push_status)

                df_input.rename(columns = {'index':'PATIENT_ID','Height_(cm)':'Height','Weight_(kg)':'Weight',
                'Diabetes_No, pre-diabetes or borderline diabetes':'Diabetes_No_pre-diabetes_or_borderline_diabetes',
                'Diabetes_Yes, but female told only during pregnancy':'Diabetes_Yes_but_female_told_only_during_pregnancy'}, inplace = True)


                spark.sql(f"CREATE DATABASE IF NOT EXISTS {configure['feature-store']['table_name']}")
                # Create a unique table name for each run. This prevents errors if you run the notebook multiple times.
                table_name = configure['feature-store']['table_name']
                print(table_name)

                df_feature = df_input.drop(configure['features']['target'],axis=1)

                df_spark = spark.createDataFrame(df_feature)

                fs = feature_store.FeatureStoreClient()

                fs.create_table(
                        name=table_name,
                        primary_keys=[configure['feature-store']['lookup_key']],
                        df=df_spark,
                        schema=df_spark.schema,
                        description="health features"
                    )
                
                push_status = self.push_df_to_s3(df_input,access_key,secret_key)
                print(push_status)

                

                #df_input_spark = spark.createDataFrame(df_input)

                # #inference_data_df = df_input_spark.select("PATIENT_ID", "Heart_Disease_Yes")

                # X_train, X_test, y_train, y_test, X_val, y_val, training_set = self.load_data(table_name, "PATIENT_ID",inference_data_df)


                print("Feature Store is created")

                

                # online_store_spec = AmazonDynamoDBSpec(
                # region="us-west-2",
                # write_secret_prefix="feature-store-example-write/dynamo",
                # read_secret_prefix="feature-store-example-read/dynamo",
                # table_name = configure['feature-store']['online_table_name']
                # )
                
                # fs.publish_table(table_name, online_store_spec)

                   
             



                
  


    def launch(self):
         
         self._preprocess_data()

   

def entrypoint():  
    
    task = DataPrep()
    task.launch()


if __name__ == '__main__':
    entrypoint()