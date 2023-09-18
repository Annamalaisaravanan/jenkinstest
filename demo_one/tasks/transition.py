import pandas as pd
import numpy as np
from sklearn import datasets
from demo_one.common import Task
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import warnings
from sklearn.metrics import accuracy_score
from mlflow.models import infer_signature
from mlflow import MlflowClient
from pydantic import BaseModel
from typing import List
import pprint


#Example to change datatype
# class InputData(BaseModel):
#     features: List[float]


# def predict(data: InputData, logit):
#     # Assuming your model expects a list of features, pass them to the loaded_model
#     features = data
#     prediction = logit.predict([features])
#     return {"prediction": prediction[0]}

warnings.filterwarnings('ignore')


class Transition(Task):
    def _get_model(self):
            client = MlflowClient()
            nw_dict =dict()
            for mv in client.search_model_versions(f"name='{self.conf['register_model_name']}'"):
                dic = dict(mv)    
                run_data_dict = client.get_run(dic['run_id']).data.to_dictionary()
                print(run_data_dict['metrics']['accuracy score'])
                nw_dict[dic['run_id']] = run_data_dict['metrics']['accuracy score']

            max_key = max(nw_dict, key=nw_dict.get)

            # Print the max key.
            print(max_key)

            model_name = 'sk-learn-logistic-reg-model'

    
            for mv in client.search_model_versions(f"name='{self.conf['register_model_name']}'"):
                        mv = dict(mv)
                        if mv['run_id'] == max_key:
                                current__version = mv["version"]
                                logged_model = mv["source"]

                                try:
                                    client.transition_model_version_stage(name=model_name, version= current__version,stage="Production")

                                except: 
                                       pass 
                        else:
                                current__version = mv["version"]

                                try:
                                  client.transition_model_version_stage(name=model_name, version= current__version,stage="Staging")

                                except:
                                       pass

            print('Model Transition completed 1')

                        
                                
            


      
    def launch(self):
         self._get_model()

         



def entrypoint():  
        task = Transition()
        task.launch()


if __name__ == '__main__':
    entrypoint()