import os
import requests
import json


host_token = os.environ.get('token')

headers = {
    "Authorization": f"Bearer {host_token}"
}

session = requests.Session()

del_config = {
    'scope': 'anna-scope'
}

scopes_del =  session.delete('https://dbc-da2540cb-9415.cloud.databricks.com/api/2.0/secrets/scopes/delete',headers=headers,params=json.loads(del_config))
print(scopes_del.status_code,scopes_del.text)