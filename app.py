import os
import boto3
from io import BytesIO
import pandas as pd

access_key = os.environ.get('access_key')
secret_key = os.environ.get('secret_key')

print(access_key,secret_key)

# s3 = boto3.resource("s3",aws_access_key_id=access_key, 
#                       aws_secret_access_key=secret_key, 
#                       region_name='ap-south-1')


# s3_object_key = 'CVD_cleaned.csv'

# s3_object = s3.Object('mlflow-artifacts-anna', s3_object_key)

# print(s3_object)
                
# csv_content = s3_object.get()['Body'].read()

# df_input = pd.read_csv(BytesIO(csv_content))

# print(df_input.shape)