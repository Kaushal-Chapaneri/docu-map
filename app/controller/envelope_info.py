"""
filename : envelope_info.py

This script is responsible for fetching envelope informations from docusign.
"""

from docusign_esign import EnvelopesApi, ApiClient
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import subprocess
from PyPDF2 import PdfFileMerger

from app.utils.utilities import update_args

def create_api_client(base_path, access_token):
    """
    Function for creating api clinet, to interact with docusign.

    input ::
        - base_path : base path uri
        - access_token : auth token received from docusign

    output :: api_client object
    """
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {access_token}")

    return api_client

def list_envelopes():
    """
    Function for getting list of all envelopes.

    input ::

    output :: pandas dataframe containing envelope informations.
    """

    args = dict()
    args = update_args(args)
    api_client = create_api_client(args['base_path'], args['access_token'])

    envelope_api = EnvelopesApi(api_client)

    from_date = (datetime.utcnow() - timedelta(days=10)).isoformat()

    results = envelope_api.list_status_changes(args['account_id'], from_date = from_date, include='recipients')

    df = pd.DataFrame(results.to_dict()['envelopes'], 
            columns=["completed_date_time", "created_date_time", "email_subject", 
                    "envelope_attachments","envelope_documents","envelope_id", "status"])

    return df

@st.cache(show_spinner=False)
def list_envelope_recipient(envelope_id):
    """
    Function for listing envelope recipients

    input ::
        - envelope_id : envelope_id to get it's recipients 

    output :: recipients details
    """

    args = dict()
    args = update_args(args)
    api_client = create_api_client(args['base_path'], args['access_token'])

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.list_recipients(args['account_id'], envelope_id)
    results = results.to_dict()['signers'][0]

    return results['name'], results['email'], results['status']

@st.cache(show_spinner=False)
def list_envelope_document(envelope_id):
    """
    Function for listing envelope documents

    input ::
        - envelope_id : envelope_id to list it's documents 

    output :: documents details
    """

    args = dict()
    args = update_args(args)
    api_client = create_api_client(args['base_path'], args['access_token'])

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.list_documents(account_id=args["account_id"], envelope_id=envelope_id)

    envelope_doc_items = list(map(lambda doc:
                                        ({"document_id": None})
                                        if (doc.document_id == "certificate") else
                                        ({"document_id": doc.document_id, "name": doc.name, "type": doc.type}),
                                        results.envelope_documents))
    
    return envelope_doc_items

@st.cache(show_spinner=False)
def get_envelope_document(envelope_id):
    """
    Function for getting envelope documents

    input ::
        - envelope_id : envelope_id to get it's documents 

    output :: downloaded document's path
    """

    args = dict()
    args = update_args(args)
    api_client = create_api_client(args['base_path'], args['access_token'])

    envelope_doc_items = list_envelope_document(envelope_id)

    envelope_api = EnvelopesApi(api_client)

    all_docs = []

    for doc in envelope_doc_items:
        if doc['document_id']:
            file_path = envelope_api.get_document(
                    account_id=args["account_id"],
                    document_id=doc['document_id'],
                    envelope_id=envelope_id
                )
            all_docs.append(file_path)

    merger = PdfFileMerger()
    for pdf in all_docs:
        merger.append(pdf)
    
    merged_file = "/tmp/"+str(envelope_id)+".pdf"
    merger.write(merged_file)
    merger.close()
    
    # docs_string = " ".join(all_docs)
    # docs_string = "pdfunite "+docs_string
    # merged_file = "/tmp/"+str(envelope_id)+".pdf"
    # docs_string = docs_string+" "+merged_file
    # subprocess.call([docs_string],shell=True)

    return merged_file

@st.cache(show_spinner=False)
def get_envelope_tabs_value(envelope_id):
    """
    Function for getting envelope tab(input fields) values.

    input ::
        - envelope_id : envelope_id to get it's tab 

    output :: tab details
    """

    args = dict()
    args = update_args(args)
    api_client = create_api_client(args['base_path'], args['access_token'])
    
    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.get_form_data(account_id=args["account_id"], envelope_id=envelope_id)
    results = results.to_dict()['form_data']

    tabs = dict()

    for tab in results:
        tabs[tab['name']] = tab['value']

    return tabs