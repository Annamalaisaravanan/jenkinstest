import os
import boto3
from io import BytesIO
import pandas as pd
import mlflow
from databricks.sdk import WorkspaceClient
from mlflow import MlflowClient

from mlflow.utils.rest_utils import http_request
import json
def client():
  return mlflow.tracking.client.MlflowClient()


host_url = os.environ.get('host')
host_token = os.environ.get('token')

print(host_url)

# s3 = boto3.resource("s3",aws_access_key_id=access_key, 
#                       aws_secret_access_key=secret_key, 
#                       region_name='ap-south-1')


# s3_object_key = 'preprocessed/y_test.csv'

# s3_object = s3.Object('mlflow-artifacts-anna', s3_object_key)

# print(s3_object)
                
# csv_content = s3_object.get()['Body'].read()

# df_input = pd.read_csv(BytesIO(csv_content))


w = WorkspaceClient(
  host  = host_url,
  token = host_token
)
 
host_creds = client()._tracking_client.store.get_host_creds()

def call_endpoint(endpoint, method, body='{}'):
  if method == 'GET':
      response = http_request(
          host_creds=host_creds, endpoint="{}".format(endpoint), method=method, params=json.loads(body))
  else:
      response = http_request( host_creds=host_creds,
          endpoint="{}".format(endpoint), method=method, 
          json=json.loads(body))
  return response.json()


job_git_config = {
  "name": "Table usage",
  "max_concurrent_runs": 1,
  "tasks": [
    {
      "task_key": "rest_api_key",
      "new_cluster": {
        "spark_version": "11.3.x-cpu-ml-scala2.12",
        "spark_conf": {
          "spark.databricks.delta.preview.enabled": "true"
        },
        "node_type_id": "m5d.large",
        "spark_env_vars": {
          "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
        },
        "enable_elastic_disk": True,
        "num_workers": 1
      },
      "spark_python_task": {
        "python_file": "demo_project/tasks/app.py",
        "source": "GIT",
      },
      "libraries": [
          {
         "pypi": {
            "package": "mlflow",
            "package": "databricks-sdk"
          },}
      ],
      "timeout_seconds": 0
    }
  ],
  "format": "SINGLE_TASK",
  "git_source": {
"git_url": "https://github.com/Annamalaisaravanan/pharma-pipeline.git",
"git_provider": "gitHub",
"git_branch": "feature-store",
},
}

job_git_response = call_endpoint(f'/api/2.1/jobs/runs/submit', 'POST',json.dumps(job_git_config))
print(job_git_response)