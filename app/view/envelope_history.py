"""
filename : envelope_history.py

Page : Envelope History

This script is responsible for fetching all envelopes informations.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.controller.envelope_info import list_envelopes
from app.controller.envelope_info import list_envelope_recipient
from app.controller.envelope_info import get_envelope_document
from app.controller.envelope_info import get_envelope_tabs_value

from app.utils.utilities import download_file
from app.utils.utilities import page_title

def envelopes_information():
    """
    Function for fetching enelopes information like \
    recipients, envelope's tab values, lists documents and download documents.

    input ::

    output :: donut plot for day wise sent envelope status, envelope expander with details.
    """

    page_title("Envelope History")
    with st.spinner('Did you know.. Docusign has saved over 2.5 billion gallons of water needed to make 20 billion sheets of paper?'):
	    envelopes_df = list_envelopes()

    dates = envelopes_df['created_date_time']
    dates = dates.apply(lambda x : x.split("T")[0])

    envelopes_df['formatted_date'] = pd.Series(dates)

    envelopes_df['created_date_time'] = envelopes_df['created_date_time'].apply(lambda x : " ".join(x.split(".")[0].split("T")))

    labels = sorted(dates.value_counts().index.tolist(), reverse=True)
    
    selected_dates = st.sidebar.multiselect('Select a date', labels, default=labels[0])

    selected_envelopes = envelopes_df[envelopes_df['formatted_date'].isin(selected_dates)]

    selected_envelopes.reset_index(inplace=True, drop=True)

    r_name = []
    r_email = []
    r_status = []

    for i in range(len(selected_envelopes)):

        name, email, status = list_envelope_recipient(selected_envelopes['envelope_id'][i])

        r_name.append(name)
        r_email.append(email)
        r_status.append(status)

    selected_envelopes[['r_email','r_name','r_status']] = pd.Series([r_email,r_name,r_status])

    selected_envelopes = selected_envelopes.iloc[::-1]

    selected_envelopes.reset_index(inplace=True, drop=True)

     # code for donut plot
    labels = selected_envelopes['status'].value_counts().index.tolist()
    values = selected_envelopes['status'].value_counts().values.tolist()

    l = [0] * len(values)
    maxpos = values.index(max(values))
    l[maxpos] = 0.1

    fig = go.Figure(data=[go.Pie(labels=labels, values=values,
                    pull=l, hole=.3)])
    fig.update_layout(title_text='Envelope status')
    st.plotly_chart(fig, use_container_width=True)

    # code for envelope expanders
    for i in range(len(selected_envelopes)):

        name = selected_envelopes['email_subject'][i]+" - "+selected_envelopes["r_name"][i]

        my_expander = st.expander(label=name)
        
        with my_expander:

            st.markdown("<b>Envelope receiver email </b>: "+selected_envelopes['r_email'][i], unsafe_allow_html=True)
            st.write("<b>Envelope created at </b>: "+selected_envelopes['created_date_time'][i], unsafe_allow_html=True)
            
            if selected_envelopes['completed_date_time'][i]:
                st.write("<b>Envelope completed at </b>: "+" ".join(selected_envelopes['completed_date_time'][i].split(".")[0].split("T")), unsafe_allow_html=True)
            
            st.write("<b>Envelope status </b>: "+selected_envelopes['status'][i], unsafe_allow_html=True)

            if selected_envelopes['status'][i] == 'completed':
                tab_values = get_envelope_tabs_value(selected_envelopes['envelope_id'][i])
                st.write("<b>Feedback </b>: "+tab_values['feedback'], unsafe_allow_html=True)
                st.write("<b>Revision required ? </b>: "+tab_values['radio1'], unsafe_allow_html=True)

            st.write(" ")
            file_path = get_envelope_document(selected_envelopes['envelope_id'][i])
            st.markdown(download_file(file_path, name+".pdf"), unsafe_allow_html=True)
    