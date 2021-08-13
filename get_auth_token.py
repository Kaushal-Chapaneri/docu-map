"""
filename : get_auth_token.py

install requirements.txt in virtual environment.

command to run : python get_auth_token.py 

This script is responsible for generating auth token. \
	it has flask server to which docusing callbacks and sends token. \
		this script needs to run first time only when setting up this project.
"""

from docusign_esign import ApiClient
import uuid
import requests
import json
from flask import Flask
from flask import request
import base64
from datetime import datetime

# update your credetials in config.json before running this script.
with open('config.json') as f:
	config = json.load(f)
		
app = Flask(__name__)

api_client = ApiClient(oauth_host_name=config["authorization_server"])

url = api_client.get_authorization_uri(client_id=config["ds_client_id"], scopes=["signature"], redirect_uri="http://localhost:5000/ds/callback", response_type="code", state=uuid.uuid4().hex.upper())

#run this output URL in browser to get callback
print("Run this URL in browser : =========> ", url)


#here is the route callback to which docusing interacts
@app.route('/ds/callback')
def generate_token():
	
	# to get auth token
	url1 = "https://"+config["authorization_server"]+"/oauth/token"
	
	integrator_and_secret_key = "Basic " + base64.b64encode(str.encode("{}:{}".format(config["ds_client_id"], config["ds_client_secret"]))).decode("utf-8")
	
	headers = {
            "Authorization": integrator_and_secret_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
	post_params = {
		    "grant_type": "authorization_code",
		    "code": request.args.get("code")
		}
        
	response = requests.post(url1, headers=headers, params=post_params)

	auth_data = json.loads(response.text)
	
	auth_data['created_at'] = str( datetime.today())
	
	resource_path = '/oauth/userinfo'
	headers = {"Authorization": "Bearer " + auth_data['access_token']}
	
	# to get user information
	url2 = "https://"+config["authorization_server"]+"/oauth/userinfo"

	response = requests.get(url2, headers=headers)
	
	data = json.loads(response.text)
	
	auth_data['user_info'] = data
	
	with open("auth_data.json", "w") as outfile: 
		json.dump(auth_data, outfile)
	
	return data
if __name__ == '__main__':
	app.run()

