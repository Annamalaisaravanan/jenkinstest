
from pathlib import Path

from demo_one.utils import preprocess, push_df_to_s3, read_data_from_s3,random_string
from demo_one.utils import read_secrets
import pandas as pd
import yaml
import os
import boto3
from conftest import DBUtilsFixture
import pytest






aws_access_key = os.environ.get('aws_access_key')
aws_secret_key = os.environ.get('aws_secret_key')

with open('demo_one/tasks/config.yml', 'r') as file:
    configure = yaml.safe_load(file)

input_data = pd.read_csv('tests/test_df.csv')

s3 = boto3.resource("s3",aws_access_key_id=aws_access_key, 
                aws_secret_access_key=aws_secret_key, 
                region_name='ap-south-1')



def test_preprocess(spark, tmp_path):
    

    # Call the preprocess function
    df_feature_pandas, df_input_pandas = preprocess(spark, configure, input_data)

    if 'Unnamed: 0' in df_input_pandas.columns:
         df_input_pandas = df_input_pandas.drop('Unnamed: 0', axis=1)

    # Remove the 'Unnamed: 0' column from df2
    if 'Unnamed: 0' in df_feature_pandas.columns:
        df_feature_pandas = df_feature_pandas.drop('Unnamed: 0', axis=1)


    # Check if the number of rows in the output matches the input
    assert len(df_input_pandas) == len(input_data)
    assert len(df_feature_pandas) == len(input_data)

    for column_name in df_input_pandas:
        assert ' ' not in column_name, f"Column name '{column_name}' contains spaces."


def test_push_df_to_s3():
         
         status = push_df_to_s3(input_data,configure['Unittest']['s3']['bucket_name'],configure['Unittest']['s3']['object_key'],s3)

         session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

            #Then use the session to get the resource
         s3_sess = session.resource('s3')

         my_bucket = s3_sess.Bucket(configure['Unittest']['s3']['bucket_name'])

         key_list = list()
         for m in my_bucket.objects.all():
                    key_list.append(m.key)

         assert configure['Unittest']['s3']['object_key'] in key_list, f"File {configure['Unittest']['s3']['object_key']} not present in S3 bucket."
                

def test_read_data_from_s3():
                
        df = read_data_from_s3(s3,configure['Unittest']['s3']['bucket_name'], configure['Unittest']['s3']['object_key'])

        assert isinstance(df, pd.DataFrame), f"Expected a Pandas DataFrame, but got {type(df)} instead."


def test_random_string():
         
          exp_run_name = random_string(configure['Unittest']['run_name'])

          assert exp_run_name.isalnum(), f"'{exp_run_name}' is not alphanumeric."

def test_read_secrets():
      
    
    dbutils = DBUtilsFixture()

    dbutils.store_secret('test-scope','aws-access-key','JHAVUEFTVCHJACEY')
    dbutils.store_secret('test-scope','aws-secret-key','36GFUY23GF4VR3YFVECDZRTFFFYG')

    print(dbutils.secrets1)

    access, secret = read_secrets(dbutils,'test-scope',['aws-access-key','aws-secret-key'])
    
    assert access, "Access key is empty."
    assert secret, "Secret key is empty."

if __name__ == '__main__':
    test_preprocess()
    test_push_df_to_s3()
    test_read_data_from_s3()
    test_random_string()