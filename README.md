<h1 align="center">DocuMap</h1>


DocuMap is an interactive Web-Application developed for the <b><a style='text-decoration:none' target=_blank href=https://www.janegoodall.org/>Jane Goodall Institute</a></b> to streamline their conservation science and mapping lifecycle to support faster participatory agreements and collaborative decision-making process using DocuSign.

This app is developed as part of the submission for <b><a style='text-decoration:none' target=_blank href=https://docusign2021.devpost.com//>DocuSign Good Code Hackathon</a></b>.

## APIs Integrated

This Application uses following DocuSign APIs :

- List Envelopes
- Send Bulk Envelopes
- List Envelope Recipients
- List Envelope Documents
- Get Envelope Documents
- Get Envelope Tab Values


## Features

- Interactive Frontend developed with Streamlit along with Plotly for visualization of plots.
- Integration of various DocuSign APIs to send and list envelopes details.
- Integrated ArcGIS Javascript library for generating maps.


## System Configurations

- This Project is developed and Tested with below mentioned system configurations.

```
- Operating System : Ubuntu 18.04 64 bit
- RAM : 4 GB
- Python version : 3.8.7
```

## Project setup

- Create a Developer account on [DocuSign](https://developers.docusign.com/) and [ArcGIS](https://developers.arcgis.com/).

```
- Update config.json file with credentials received from both DocuSign and ArcGIS.
- Create a virtual environment with python 3.8.7 and Install requirements.txt in it.
- Run script get_auth_token.py to get authentication token from DocuSign. (run this for the first time only)
- verify generated auth_data.json file.
```

## Run project

```bash
streamlit run DocuMap.py
```

## Ideal flow

- Step 0 : Get Overview of the sent envelope's status in the "Dashboard" page.
- Step 1 : Create a map from the "Generate Map'' page.
- Step 2 : Use generated map to send in envelope to multiple stakeholders from "Send Envelope" page.(without selecting Enable versioning)
- Step 3 : Visit page "Envelope History" and see the Envelope response of Recipients.
- Step 4 : If revision required then download envelope documents by clicking the "Download Document" button in envelope expander.
- Step 5 : Go to page "Send Envelopes", select "Enable Versioning" checkbox, set number of documents and upload docs and send envelope.
- Step 6 : Visit page "Envelope History" and see the Envelope response of Recipients.
- Step 7 : if all stakeholders approved then goto step 8 else go to step 4.
- Step 8 : Download signed documents by clicking the "Download Document" button in the envelope expander.
- Step 9 : Send final Envelope, Go to page "Send Envelopes", select "Enable Versioning" checkbox, set number of documents and upload docs.

## Demo
- Watch demo of this application on [YouTube](https://youtu.be/gLbBKQbwKd4).
