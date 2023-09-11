import os
import boto3
from io import BytesIO
import pandas as pd

access_key = os.environ.get('access_key')
secret_key = os.environ.get('secret_key')

s3 = boto3.resource("s3",aws_access_key_id='AKIAUJKJ5ZIQLZGYFST2', 
                      aws_secret_access_key='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', 
                      region_name='ap-south-1')


s3_object_key = 'CVD_cleaned.csv'

s3_object = s3.Object('mlflow-artifacts-anna', s3_object_key)

print(s3_object)
                
csv_content = s3_object.get()['Body'].read()

df_input = pd.read_csv(BytesIO(csv_content))

print(df_input.shape)