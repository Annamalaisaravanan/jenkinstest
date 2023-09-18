import os
import requests
import json


host_token = os.environ.get('token')

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

headers = {
    "Authorization": f"Bearer {host_token}"
}

secret_scope_config = {
            "scope": "anna-scope",
            "initial_manage_principal": "MANAGE",
            "scope_backend_type": "DATABRICKS"
            }



scope_response = make_databricks_api_request('https://dbc-da2540cb-9415.cloud.databricks.com/api/2.0/secrets/scopes/create', "POST", json.dumps(secret_scope_config),headers)
print('The scope response is',scope_response)

secret_config = {
  "scope": "anna-scope",
  "key": "databricks-token",
  "string_value": host_token,
}

secret_response = make_databricks_api_request('https://dbc-da2540cb-9415.cloud.databricks.com/api/2.0/secrets/put', "POST", json.dumps(secret_config),headers)
print('The scope response is',secret_response)
