import os
import requests
import json

import yaml

with open('databricks-config.yml', 'r') as file:
    db_yml = yaml.safe_load(file)


host_token = os.environ.get('token')

headers = {
    "Authorization": f"Bearer {host_token}"
}

session = requests.Session()

del_config = {
    'scope': 'anna-scope'
}

scopes_del =  session.delete(f"{db_yml['databricks_host']}/api/2.0/secrets/scopes/delete",headers=headers,params=json.loads(del_config))
print(scopes_del.status_code,scopes_del.text)