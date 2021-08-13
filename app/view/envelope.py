"""
filename : envelope.py

Page : Send Envelope

This script is responsible for sending envelopes (normal and revision).
"""

import streamlit as st
import re
import os

from app.controller.send_envelope import worker
from app.utils.utilities import page_title

def fill_envelope_details():
	"""
    Function for Send Envelope page, takes necessary inputs for sending \
		envelope and applying revisions.

    input ::

    output :: send envelope to recipient
    """

	page_title("Send Envelope")
	st.sidebar.write('')
	
	no_of_recipient = st.sidebar.number_input(
		label="Number of recipient",
		min_value=1,
		value=2,
		step=1
	)
	
	st.sidebar.write('')
	
	enable_version = st.sidebar.checkbox("Enable Versioning", False)
	
	st.sidebar.write('')
	
	if enable_version:
	
		no_of_revisions = st.sidebar.number_input(
			label="Number of Documents",
			min_value=1,
			value=1,
			step=1
		)
	all_docs = []
	
	response_args = dict()

	images_path = 'asset/images'
	images = os.listdir(images_path)

	with st.form(key='send_envelope'):
		env_subject = st.text_input('Subject')
		env_description = st.text_input('Description')

		if not enable_version:
			image = st.selectbox("Select an image",images)
			response_args['inline_image'] = image
		
		recipient_cols = st.columns(int(no_of_recipient))
		
		signers = []
		
		for i, col in enumerate(recipient_cols):
			signer = dict()
			name = col.text_input('Recipient Name '+str(i+1), key='Name'+str(i+1))
			email = col.text_input('Recipient Email '+str(i+1), key='Email'+str(i+1))
			signer['signer_name'] = name
			signer['signer_email'] = email
			signers.append(signer)
			
		env_map_url = st.text_input('Map URL')
		
		env_version = st.text_input('Version')
		
		if enable_version:
		
			revision_cols = st.columns(int(no_of_revisions))
			revision_titles = []
			
			for i, col in enumerate(revision_cols):
				revision_doc = col.file_uploader("Choose file "+str(i+1), key='upload'+str(i+1), type="pdf")
				revision_title = col.text_input("Document name "+str(i+1), key='title'+str(i+1))
				all_docs.append(revision_doc)
				revision_titles.append(revision_title)
				
			response_args['revision_titles'] = revision_titles

		submit = st.form_submit_button('Submit')
		
	if submit:
	
		response_args['env_subject'] = env_subject
		response_args['env_description'] = env_description
		response_args['no_of_recipient'] = no_of_recipient
		response_args['signers'] = signers
		response_args['env_map_url'] = env_map_url
		response_args['env_version'] = env_version
		response_args['enable_version'] = enable_version
		response_args['documents'] = all_docs

		if any(value=='' for value in response_args.values()):
			st.error('Looks like there is some empty input fields...')
		
		elif sum([True for signer in response_args['signers'] if signer['signer_name'] and re.search(r'[\w.-]+@[\w.-]+.\w+', signer['signer_email'])]) == 0:
			st.error('Invalid Recipient details...')
		
		else:
			try:
				worker(response_args)
			except Exception as e:
				print('envelope error ',str(e))
				st.error('Something went wrong... ')
