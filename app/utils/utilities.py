"""
filename : utilities.py

This file contains common functions which are being called throught the app.
"""

import json
import streamlit as st
from dateutil.parser import parse
from datetime import datetime
import uuid
import requests
import base64
import re

def header():
    """function to display header on every page"""

    st.sidebar.markdown("""<h1 style='text-align: center; color: black;'><u>DocuMap</u></h1>""", unsafe_allow_html=True)
    st.markdown("""<h1 style='text-align: center; color: black;'><u>DocuMap</u></h1>""", unsafe_allow_html=True)

def page_title(page):
	"""function to display page title on every page"""

	st.markdown("""<h2 style='text-align: left; color: black;'>{0}</h2>""".format(page), unsafe_allow_html=True)
	st.write("")

@st.cache
def load_config():
	"""
    Function for loading necessary credentials such as \
		Docusign client_id, Docusing client_secret and arcgis key

    input ::

    output :: json object of all the credentials
    """
	with open('config.json') as f:
		return json.load(f)

def load_auth_data():
	"""
    Function for loading docusign auth token or to refresh token in case of \
		auth token has expred. it has auth token, refresh token, account_id, \
			base_uri etc. 

    input ::

    output :: json object of authentication information
    """
	with open('auth_data.json') as f:
		return json.load(f)

@st.cache
def verify_auth_token(auth_data):
	"""
    Function checks whether current token is expired.

    input :: auth_data json containing token informatino.

    output :: boolean flag, token expired or not 
    """
	last_date = auth_data['created_at']
	now = datetime.today()

	diff = now - parse(last_date)
	seconds_in_day = 24 * 60 * 60
	total_sec_passed = diff.days * seconds_in_day + diff.seconds

	if total_sec_passed > auth_data['expires_in']:
		return True
	else:
		return False

def get_refresh_token(config, refresh_token):
	"""
    Function for getting new token using refresh token 

    input :: config - docusing credentials
			 refresh_token - token to get new auth token

    output :: new authentication information.
    """

	url = "https://"+config['authorization_server']+"/oauth/token"
	integrator_and_secret_key = "Basic " + base64.b64encode(str.encode("{}:{}".format(config['ds_client_id'], config['ds_client_secret']))).decode("utf-8")

	headers = {
			"Authorization": integrator_and_secret_key
		}

	post_params = {
			"grant_type": "refresh_token",
			"refresh_token": refresh_token
		}
		
	response = requests.post(url, headers=headers, params=post_params)
	auth_data = json.loads(response.text)
	auth_data['created_at'] = str(datetime.today())
		
	url2 = "https://"+config['authorization_server']+'/oauth/userinfo'
	headers = {"Authorization": "Bearer " + auth_data['access_token']}
	response = requests.get(url2, headers=headers)
	data = json.loads(response.text)

	auth_data['user_info'] = data

	with open("auth_data.json", "w") as outfile: 
		json.dump(auth_data, outfile)

	return auth_data

def update_args(args):
	"""
    Function for preparing json object to pass throught the app containing auth data

    input :: args - empty json

    output :: json object of authentication information
    """

	auth_data = load_auth_data()

	do_refresh = verify_auth_token(auth_data)

	if do_refresh:

		config = load_config()
		auth_data = get_refresh_token(config, auth_data['refresh_token'])

	args['access_token'] = auth_data['access_token']
	args['account_id'] = auth_data['user_info']['accounts'][0]['account_id']
	args['base_path'] = auth_data['user_info']['accounts'][0]['base_uri']+'/restapi'

	return args

@st.cache
def download_file(path, name):
	"""
    Function for downloading envelope documents. 

    input :: path - file path to download
			 name - name to give to downloaded file

    output :: html code along with base64 encoded document to download
    """
	with open(path, 'rb') as f:
		bytes = f.read()
		b64 = base64.b64encode(bytes).decode()

	button_text = 'Download Document'
	button_uuid = str(uuid.uuid4()).replace('-', '')
	button_id = re.sub('\d+', '', button_uuid)

	custom_css = f""" 
		<style>
			#{button_id} {{
				background-color: rgb(255, 255, 255);
				color: rgb(38, 39, 48);
				padding: 0.25em 0.38em;
				position: relative;
				text-decoration: none;
				border-radius: 4px;
				border-width: 1px;
				border-style: solid;
				border-color: rgb(230, 234, 241);
				border-image: initial;
			}} 
			#{button_id}:hover {{
				border-color: rgb(246, 51, 102);
				color: rgb(246, 51, 102);
			}}
			#{button_id}:active {{
				box-shadow: none;
				background-color: rgb(246, 51, 102);
				color: white;
				}}
		</style> """
		
	dl_link = custom_css + f'<a download="{name}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

	return dl_link

@st.cache
def load_arcgis_js():
	"""
    Function for generating Arcgis map, and loading arcgis javascript library in python. \
		run time polygons from shapefile are plotted on map and arcgis key and other \
			necessary details are feeded in this javascript code.

    input ::

    output :: javascript code to generate map
    """
	html_file = open('asset/html/basic_map.html', 'r', encoding='utf-8')
	html_code = html_file.read()

	return html_code