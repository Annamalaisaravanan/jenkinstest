from demo_one.common import Task

import json
import pandas as pd
import requests
import zipfile
import io

from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils

# from evidently.pipeline.column_mapping import ColumnMapping
# from evidently.report import Report
# from evidently.metric_preset import DataDriftPreset

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from mlflow.utils.rest_utils import http_request
import json
def client():
  return mlflow.tracking.MlflowClient()
 
host_creds = client()._tracking_client.store.get_host_creds()


def mlflow_call_endpoint(endpoint, method, body='{}'):
  if method == 'GET':
      response = http_request(
          host_creds=host_creds, endpoint="/api/2.0/mlflow/{}".format(endpoint), method=method, params=json.loads(body))
  else:
      response = http_request(
          host_creds=host_creds, endpoint="/api/2.0/mlflow/{}".format(endpoint), method=method, 
          json=json.loads(body))
  return response.json()

class Datadrift(Task):


    def _data_drift(self):


        spark = SparkSession.builder.appName("CSV Loading Example").getOrCreate()

        dbutils = DBUtils(spark)

        aws_access_key = dbutils.secrets.get(scope="secrets-scope", key="aws-access-key")
        aws_secret_key = dbutils.secrets.get(scope="secrets-scope", key="aws-secret-key")
        db_host = dbutils.secrets.get(scope="secrets-scope", key="databricks-host")
        db_token = dbutils.secrets.get(scope="secrets-scope", key="databricks-token")

        lists = {
            "model_name":"pharma_model",
            "events": "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"
        }
        js_list_res = mlflow_call_endpoint('registry-webhooks/list', 'GET', json.dumps(lists))

        if js_list_res:
              print("Webhook is already created")

        else:
                diction = {
                                "job_spec": {
                                    "job_id": self.conf['deployment-pipeline']['job_id'],
                                    "access_token": db_token,
                                    "workspace_url": db_host
                                },
                                "events": [
                                    "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"
                                ],
                                "model_name": "pharma_model",
                                "description": "Webhook for Deployment Pipeline",
                                "status": "ACTIVE"
                                }

                job_json= json.dumps(diction)
                js_res = mlflow_call_endpoint('registry-webhooks/create', 'POST', job_json)
                print(js_res)

                print("Webhook Created for deployment job")

        # content = requests.get("https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip").content
        # with zipfile.ZipFile(io.BytesIO(content)) as arc:
        #     raw_data = pd.read_csv(arc.open("day.csv"), header=0, sep=',', parse_dates=['dteday'])

        # data_columns = ColumnMapping()
        # data_columns.datetime = 'dteday'
        # data_columns.numerical_features = ['weathersit', 'temp', 'atemp', 'hum', 'windspeed']
        # data_columns.categorical_features = ['holiday', 'workingday']

        # #set reference dates
        # reference_dates = ('2011-01-01 00:00:00','2011-01-28 23:00:00')

        # #set experiment batches dates
        # experiment_batches = [
        #     ('2011-01-01 00:00:00','2011-01-29 23:00:00'),
        #     ('2011-01-29 00:00:00','2011-02-07 23:00:00'),
        #     ('2011-02-07 00:00:00','2011-02-14 23:00:00'),
        #     ('2011-02-15 00:00:00','2011-02-21 23:00:00'),  
        # ]

        
        # #log into MLflow
        # client = MlflowClient()

        # #set experiment
        # mlflow.set_experiment(self.conf['Mlflow']['data_drift_exp_name'])

        # #start new run
        # for date in experiment_batches:
        #     with mlflow.start_run() as run: #inside brackets run_name='test'
                
        #         # Log parameters
        #         mlflow.log_param("begin", date[0])
        #         mlflow.log_param("end", date[1])

        #         # Log metrics
        #         metrics = self.eval_drift(raw_data.loc[raw_data.dteday.between(reference_dates[0], reference_dates[1])], 
        #                             raw_data.loc[raw_data.dteday.between(date[0], date[1])], 
        #                             column_mapping=data_columns)
        #         for feature in metrics:
        #             mlflow.log_metric(feature[0], round(feature[1], 3))

        #         print(run.info)


              
              

    def launch(self):
         
         self._data_drift()

    # def eval_drift(self, reference, production, column_mapping):
    #             """
    #             Returns a list with pairs (feature_name, drift_score)
    #             Drift Score depends on the selected statistical test or distance and the threshold
    #             """    
    #             data_drift_report = Report(metrics=[DataDriftPreset()])
    #             data_drift_report.run(reference_data=reference, current_data=production, column_mapping=column_mapping)
    #             report = data_drift_report.as_dict()

    #             drifts = []

    #             for feature in column_mapping.numerical_features + column_mapping.categorical_features:
    #                 drifts.append((feature, report["metrics"][1]["result"]["drift_by_columns"][feature]["drift_score"]))

    #             return drifts


def entrypoint():  
    
    task = Datadrift()
    task.launch()

if __name__ == '__main__':
    entrypoint()