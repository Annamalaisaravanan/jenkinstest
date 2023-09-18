import os
import boto3
from io import BytesIO
import pandas as pd
import json
import requests
# import mlflow
# from databricks.sdk import WorkspaceClient
# from mlflow import MlflowClient

# from mlflow.utils.rest_utils import http_request
# import json
# def client():
#   return mlflow.tracking.client.MlflowClient()


host = os.environ.get('host')
host_token = os.environ.get('token')

import requests
import json



def make_databricks_api_request(host_url, method, json_data=None, headers=None, params=None):
   
    # Construct the full URL for the API request
    url = f"{host_url}"
    
    # Create the request headers (if provided)
    if headers is None:
        headers = {}
    
    # Create the request parameters (if provided)
    if params is None:
        params = {}
    
    # Perform the API request based on the HTTP method
    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, params=params, json=json.loads(json_data))
    elif method == 'PUT':
        headers['Content-Type'] = 'application/json'
        response = requests.put(url, headers=headers, params=params, json=json_data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, params=params)
    else:
        raise ValueError("Invalid HTTP method. Supported methods are GET, POST, PUT, and DELETE.")
    
    return response


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
        "python_file": "demo_one/tasks/data_preprocess.py",
        "source": "GIT",
      },
      "libraries": [
          {
         "pypi": {
            "package": "mlflow",
            "package": "databricks-sdk",
            "package": "mlflow",
            "package": "databricks-sdk",
            "package": "pyspark==3.2.1",
            "package": "boto3",
            "package": "delta-spark==1.1.0",
            "package": "scikit-learn==1.2.0",
            "package": "databricks-feature-store",
            "package": "evidently",
            "package": "pandas==1.5.3",
            "package": "mlflow",
            "package": "urllib3"
          },}
      ],
      "timeout_seconds": 0
    }
  ],
  "format": "SINGLE_TASK",
  "git_source": {
"git_url": "https://github.com/Annamalaisaravanan/jenkinstest.git",
"git_provider": "gitHub",
"git_branch": "main",
},
}

headers = {
    "Authorization": f"Bearer {host_token}"
}

# Make the API request
response = make_databricks_api_request('https://dbc-da2540cb-9415.cloud.databricks.com/api/2.1/jobs/runs/submit', "POST", json.dumps(job_git_config),headers)
print(response)





# w = WorkspaceClient(
#   host  = host_url,
#   token = host_token
# )
 
# host_creds = client()._tracking_client.store.get_host_creds()

# def call_endpoint(endpoint, method, body='{}'):
#   if method == 'GET':
#       response = http_request(
#           host_creds=host_creds, endpoint="{}".format(endpoint), method=method, params=json.loads(body))
#   else:
#       response = http_request( host_creds=host_creds,
#           endpoint="{}".format(endpoint), method=method, 
#           json=json.loads(body))
#   return response.json()



# job_git_response = call_endpoint(f'/api/2.1/jobs/runs/submit', 'POST',json.dumps(job_git_config))
# print(job_git_response)