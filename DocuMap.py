"""
filename : DocuMap.py
This script is the starting point for the execution of this project.

command to run : streamlit run DocuMap.py

This file holds the structure of entire project and
calls the necessary function as per requested page.
"""

import streamlit as st

from app.utils.utilities import header
from app.view.dashboard import display_stats
from app.view.map import map_input
from app.view.envelope import fill_envelope_details
from app.view.envelope_history import envelopes_information

# st.set_page_config(layout="wide")
header()

page = st.sidebar.selectbox("Select a page",
			["Dashboard", "Generate Map", "Send Envelope", "Envelope History"])

if page == "Dashboard":
    display_stats()

elif page == "Generate Map":
    map_input()

elif page == "Send Envelope":
    fill_envelope_details()

else:
    envelopes_information()
