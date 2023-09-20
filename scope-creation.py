import os
import requests
import json

import yaml

with open('databricks-config.yml', 'r') as file:
    db_yml = yaml.safe_load(file)


host_token = os.environ.get('token')
aws_access = os.environ.get('aws_access_key')
aws_secret = os.environ.get('aws_secret_key')

def make_databricks_api_request(host_url, method, json_data='{}', headers=None, params=None):
   
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
        response = requests.get(url, headers=headers, params=json.loads(json_data))
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

headers = {
    "Authorization": f"Bearer {host_token}"
}


session = requests.Session()

scopes_list =  session.get(f"{db_yml['databricks_host']}/api/2.0/secrets/scopes/list",headers=headers)
print(db_yml['databricks_host'])
json_text = json.loads(scopes_list.text)
print(json_text)
scope_name = []
for scope in json_text['scopes']:
            scope_name.append(scope['name'])
            

if 'anna-scope' not in scope_name:         
            secret_scope_config = {
                "scope": "anna-scope",
                "scope_backend_type": "DATABRICKS"
                }
            scope_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/scopes/create", "POST", json.dumps(secret_scope_config),headers)
            print('The scope response is',scope_response)

else:
         print(" anna-scope is already exist!! ")

secret_config = {
  "scope": "anna-scope",
  "key": "databricks-token",
  "string_value": host_token,
}

secret_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/put", "POST", json.dumps(secret_config),headers)
print('The scope response is',secret_response)

aws_secret1_config = {
  "scope": "anna-scope",
  "key": "aws_access_key",
  "string_value": aws_access,
}

aws_access_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/put", "POST", json.dumps(aws_secret1_config),headers)
print('The access scope response is',aws_access_response)


aws_secret2_config = {
  "scope": "anna-scope",
  "key": "aws_secret_key",
  "string_value": aws_secret,
}



aws_secret_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/put", "POST", json.dumps(aws_secret2_config),headers)
print('The secret scope response is',aws_secret_response)
