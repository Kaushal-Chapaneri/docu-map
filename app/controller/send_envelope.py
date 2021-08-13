"""
filename : send_envelope.py

This script is responsible for sending envelopes.
"""
import base64
from os import path
import json
import streamlit as st

from docusign_esign import EnvelopesApi, Document, Signer, EnvelopeDefinition, Recipients, \
    BulkEnvelopesApi, TextCustomField, CustomFields, SignHere, Tabs, ApiClient, \
		BulkSendingCopyTab, Text, Radio, RadioGroup, SignerAttachment, Draw
from docusign_esign.models import BulkSendingCopy, BulkSendingList, BulkSendingCopyRecipient, BulkSendRequest, BulkSendBatchStatus

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

def create_bulk_sending_list(args):

    bulk_copies = []
    
    for signer in args:
        recipient = BulkSendingCopyRecipient(
            role_name="signer",
            tabs=[],
            name=signer["signer_name"],
            email=signer["signer_email"]
        )

        bulk_copy = BulkSendingCopy(
            recipients=[recipient],
            custom_fields=[]
        )

        bulk_copies.append(bulk_copy)

    bulk_sending_list = BulkSendingList(
        name="sample",
        bulk_copies=bulk_copies
    )
	
    return bulk_sending_list

def create_document1(args):
    """ Creates document 1 -- an html document"""

    return f"""
    <!DOCTYPE html>
	<html>
		<head>
		  <meta charset="UTF-8">
		</head>
		<body style="font-family:sans-serif;margin-left:2em;">
		<table>
		  <tbody style="border-collapse: collapse;border: 10px solid #d9d7ce; display: inline-block;padding: 6px 12px;line-height:50px;text-align: left;vertical-align: bottom;">
			<tr>
			  <td colspan="2"><h1 style='text-align: left; color: black;'><u>DocuMap</u></h1></td>
			</tr>
			<tr>
			  <td colspan="2"><h2 style='text-align: left; color: black;'>{args["env_subject"]}</h2></td>
			</tr>
			<tr>
			  <td colspan="2" style="text-align: justify;"><pre><h3>{args["env_description"]}</h3></pre></td>
			</tr>
			<tr>
			  <td><b>Map URL: </b></td>
			  <td><h3 style="color:white;">**map_url**/</h3></td>
			</tr>
			<tr>
			  <td><b>Version: </b></td>
			  <td><span style="color:black;">{args["env_version"]}</span></td>
			</tr>
			<tr>
			  <td><b>Feedback: </b></td>
			  <td><span style="color:white;">**feedback**/</span></td>
			</tr>
			<tr style="line-height:80px;">
			  <td><b>Revision required ? : </b></td>
			  <td> Yes<span style="color:white;">**r1**/</span> No<span style="color:white;">**r2**/</span></td>
			</tr>
			<tr>
			  <td style="line-height:80px;"><b>Attach document: </b></td>
			  <td><span style="color:white;">**signer_attachment**/</span></td>
			</tr>
			<tr style="line-height:120px;">
			  <td><b>Agreed: </b></td>
			  <td><span style="color:white;">**signature_1**/</span></td>
			</tr>
		  </tbody>
		</table>
		</body>
	</html>
  """

def make_draft_envelope(args):

	base64_file_content = base64.b64encode(bytes(create_document1(args), "utf-8")).decode("ascii")

	all_documents = []

	counter = 1

	document1 = Document(
		document_base64=base64_file_content,
		name=args['env_subject'],
		file_extension="html",
		document_id=str(counter)
	)

	counter += 1

	all_documents.append(document1)

	if not args["enable_version"]:

		doc2 = args["inline_image"]
		with open('asset/images/'+doc2, "rb") as image:
			f = image.read()
			image_bytes = bytearray(f)
			content_bytes = base64.b64encode(image_bytes).decode("ascii")
			
		doc2_html = f"""
			<!DOCTYPE html>
			<html>
				<body>
					<span style="color:white;">**draw**/</span>
					<img src="data:image/png;base64,{content_bytes}"/>
				</body>
			</html>"""

		base64_file_content = base64.b64encode(bytes(doc2_html, "utf-8")).decode("ascii")

		document2 = Document(
				document_base64=base64_file_content,
				name="attachment_1",
				file_extension="html",
				document_id=str(counter)
			)

		all_documents.append(document2)
		counter += 1

	if len(args["documents"])>0:
		for doc in args["documents"]:
			content_bytes = doc.read()
			base64_file_content = base64.b64encode(content_bytes).decode("ascii")
			document_n = Document(
				document_base64=base64_file_content,
				name=args["revision_titles"][counter-2],
				file_extension="pdf",
				document_id=str(counter)
			)

			counter += 1
			all_documents.append(document_n)

	envelope_definition = EnvelopeDefinition(
		email_subject=args['env_subject']
	)
	
	envelope_definition.documents = all_documents
	
	signer = Signer(
		name="Multi Bulk Recipient::signer",
		email="multiBulkRecipients-signer@docusign.com",
		role_name="signer",
		note="",
		routing_order="1",
		delivery_method="email",
		recipient_id="1",
		recipient_type="signer"
	)

	sign_here1 = SignHere(
		    anchor_string="**signature_1**",
		    anchor_units="pixels",
		    anchor_y_offset="10",
		    anchor_x_offset="20",
			optional="true"
		)

	signer_attachment = SignerAttachment(
			anchor_string="**signer_attachment**",
			optional="true"
	)

	feedback = Text(
				anchor_string="**feedback**", anchor_units="pixels",
				font="helvetica", font_size="size11",
				bold="false",
				locked="false", tab_id="feedback",
				tab_label="feedback", required="false",height="35",width="200")

	map_url = Text(
				anchor_string="**map_url**", anchor_units="pixels",
				font="helvetica", font_size="size11",
				bold="false",
				locked="true", tab_id="map_url",
				tab_label="map_url", required="false",height="35",width="200",value=args["env_map_url"])

	radio_group = RadioGroup(
            group_name="radio1",
            radios=[Radio(value="Yes", selected="true",anchor_string="**r1**"),
			Radio(value="No", selected="false", anchor_string="**r2**")]
        )
	
	drwa_field = Draw(
		anchor_string="**draw**",required="false",document_id="2",
		anchor_units="pixels",height=540,width=535
	)
			
	signer.tabs = Tabs(sign_here_tabs=[sign_here1], text_tabs=[feedback, map_url], 
	radio_group_tabs=[radio_group], signer_attachment_tabs=[signer_attachment], draw_tabs=[drwa_field])
	
	recipients = Recipients(signers=[signer])
	envelope_definition.recipients = recipients


	return envelope_definition

def worker(args):
	"""
    Driver Function for sending envelops

    input ::
        - args : envelope informations

    output :: send envelope
    """

	args = update_args(args)

	api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])

	bulk_envelopes_api = BulkEnvelopesApi(api_client)
	bulk_sending_list = create_bulk_sending_list(args["signers"])

	bulk_list = bulk_envelopes_api.create_bulk_send_list(
            account_id=args["account_id"],
            bulk_sending_list=bulk_sending_list
        )

	bulk_list_id = bulk_list.list_id

	envelope_api = EnvelopesApi(api_client)

	envelope_definition = make_draft_envelope(args)

	envelope = envelope_api.create_envelope(account_id=args["account_id"], envelope_definition=envelope_definition)
	envelope_id = envelope.envelope_id

	text_custom_fields = TextCustomField(name="mailingListId", required="false", show="false", value=bulk_list_id)
	custom_fields = CustomFields(list_custom_fields=[], text_custom_fields=[text_custom_fields])
	
	envelope_api.create_custom_fields(
		account_id=args["account_id"],
		envelope_id=envelope_id,
		custom_fields=custom_fields
	)

	bulk_send_request = BulkSendRequest(envelope_or_template_id=envelope_id)

	batch = bulk_envelopes_api.create_bulk_send_request(
		account_id=args["account_id"],
		bulk_send_list_id=bulk_list_id,
		bulk_send_request=bulk_send_request
	)
	batch_id = batch.batch_id

	response = bulk_envelopes_api.get_bulk_send_batch_status(account_id=args["account_id"], bulk_send_batch_id=batch_id)

	st.success("Envelope has been Sent.")
