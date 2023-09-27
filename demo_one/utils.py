import random
import string
from io import BytesIO

from sklearn.preprocessing import OrdinalEncoder
import pandas as pd
import json
import pickle
from mlflow.utils.rest_utils import http_request

from pyspark.sql import SparkSession
#from pyspark.dbutils import DBUtils


def random_string(base_string):
        # Generate a random number (assuming you want a 6-digit number)
        random_number = ''.join(random.choices(string.digits, k=6))

        result_string = base_string + random_number

        return result_string


def push_df_to_s3(df,bucket_name,object_key,s3):
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            s3.Object(bucket_name, object_key).put(Body=csv_content)

            return {"df_push_status": 'successs'}


def mlflow_call_endpoint(host_cred, endpoint, method, body='{}'):
                if method == 'GET':
                    response = http_request(
                        host_creds=host_cred, endpoint="/api/2.0/mlflow/{}".format(endpoint), method=method, params=json.loads(body))
                else:
                    response = http_request(
                        host_creds=host_cred, endpoint="/api/2.0/mlflow/{}".format(endpoint), method=method, 
                        json=json.loads(body))
                return response.json()

def read_data_from_s3(s3,bucket_name, csv_file_key):
        
        s3_object = s3.Object(bucket_name, csv_file_key)

        csv_content = s3_object.get()['Body'].read()

        df_input = pd.read_csv(BytesIO(csv_content))

        return df_input  


def read_secrets(dbutils,scope,keys):
        
        h=tuple()
        for key in keys:
             j = dbutils.secrets.get(scope=scope, key=key)
             h = h+ (j,)
        return h


def feature_store_create(fs,table_name,configure,df_spark):
            
            # spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()
            # dbutils = DBUtils(spark)

            fs.create_table(
                        name=table_name,
                        primary_keys=[configure['feature-store']['lookup_key']],
                        df=df_spark,
                        schema=df_spark.schema,
                        description="health features"
                    )
                
            print("Feature Store is created")

            
            return True

def preprocess(spark,configure,df_input):
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
                
                # pickled_data = pickle.dumps(encoders_dict)
                # pkl_path = configure['preprocessed']['encoders_path']
                
                df_input.rename(columns = {'index':'PATIENT_ID','Height_(cm)':'Height','Weight_(kg)':'Weight',
                'Diabetes_No, pre-diabetes or borderline diabetes':'Diabetes_No_pre-diabetes_or_borderline_diabetes',
                'Diabetes_Yes, but female told only during pregnancy':'Diabetes_Yes_but_female_told_only_during_pregnancy'}, inplace = True)


                spark.sql(f"CREATE DATABASE IF NOT EXISTS {configure['feature-store']['DB']}")
                print('pharma db created')
                # Create a unique table name for each run. This prevents errors if you run the notebook multiple times.
                table_name = configure['feature-store']['table_name']
                print(table_name)

                df_feature = df_input.drop(configure['features']['target'],axis=1)

                return df_feature, df_input