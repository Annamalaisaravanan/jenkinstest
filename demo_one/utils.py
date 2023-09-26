import random
import string
from io import BytesIO
import boto3
import pandas as pd
import json
from databricks.feature_store.online_store_spec import AmazonDynamoDBSpec
from mlflow.utils.rest_utils import http_request

from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils


def random_string(base_string):
        # Generate a random number (assuming you want a 6-digit number)
        random_number = ''.join(random.choices(string.digits, k=6))

        result_string = base_string + "_" + random_number

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


def feature_store_createAndPublish(fs,table_name,configure,df_spark):
            
            spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()
            dbutils = DBUtils(spark)

            fs.create_table(
                        name=table_name,
                        primary_keys=[configure['feature-store']['lookup_key']],
                        df=df_spark,
                        schema=df_spark.schema,
                        description="health features"
                    )
                
            print("Feature Store is created")

            online_store_spec = AmazonDynamoDBSpec(
            region="us-west-2",
            write_secret_prefix="feature-store-example-write/dynamo",
            read_secret_prefix="feature-store-example-read/dynamo",
            table_name = configure['feature-store']['online_table_name']
            )
            
            fs.publish_table(table_name, online_store_spec)

            print("Feature store published")
            return True