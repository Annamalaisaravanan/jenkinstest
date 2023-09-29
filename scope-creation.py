import os
import requests
import json

import yaml

with open('databricks-config.yml', 'r') as file:
    db_yml = yaml.safe_load(file)


host_token = os.environ.get('token')
aws_access = os.environ.get('aws_access_key')
aws_secret = os.environ.get('aws_secret_key')
c5_access  = os.environ.get('c5_access_key')
c5_secret  = os.environ.get('c5_secret_key')

def make_databricks_api_request(host_url, method, json_data='{}', headers=None, params=None):
   
    # Construct the full URL for the API requests
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


def add_secrets_to_scope(scope_name,scope_key,key_value):
            secret_config = {
            "scope": scope_name,
            "key": scope_key,
            "string_value": key_value,
            }

            secret_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/put", "POST", json.dumps(secret_config),headers)
            print('The scope response is',secret_response)


session = requests.Session()

scopes_list =  session.get(f"{db_yml['databricks_host']}/api/2.0/secrets/scopes/list",headers=headers)
print(db_yml['databricks_host'])
json_text = json.loads(scopes_list.text)
print(json_text)

scope_name = []
if not json_text or json_text['scopes'] :
    print("The dictionary is empty.")
    
else:
    print("The dictionary is not empty.")
    
    for scope in json_text['scopes']:
            scope_name.append(scope['name'])


            

def scope_check(scope_name,scope):
        if scope not in scope_name:         
                    secret_scope_config = {
                        "scope": scope,
                        "scope_backend_type": "DATABRICKS"
                        }
                    scope_response = make_databricks_api_request(f"{db_yml['databricks_host']}/api/2.0/secrets/scopes/create", "POST", json.dumps(secret_scope_config),headers)
                    print('The scope response is',scope_response)

        else:
                print(f"{scope} is already exist!! ")


scope_check(scope_name,'anna-scope')
scope_check(scope_name,'feature-store-example-read')
scope_check(scope_name,'feature-store-example-write')


add_secrets_to_scope('anna-scope',"databricks-token",host_token)
add_secrets_to_scope('anna-scope',"aws_access_key",aws_access)
add_secrets_to_scope('anna-scope','aws_secret_key',aws_secret)

add_secrets_to_scope('feature-store-example-read','dynamo-access-key-id',c5_access)
add_secrets_to_scope('feature-store-example-read','dynamo-secret-access-key',c5_secret)


add_secrets_to_scope('feature-store-example-write','dynamo-access-key-id',c5_access)
add_secrets_to_scope('feature-store-example-write','dynamo-secret-access-key',c5_secret)
