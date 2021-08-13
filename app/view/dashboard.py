"""
filename : dashboard.py

Page : Dashboard

This script is responsible for generating plots on dashboard page.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.controller.envelope_info import list_envelopes
from app.utils.utilities import page_title

def display_stats():
    """
    Function for Dashboard page, fetches envelopes information and generates plots

    input ::

    output :: donut plot of envelope status and bar plot of day wise sent envelopes
    """

    page_title("Dashboard")

    with st.spinner('Did you know.. The 20 billion sheets of paper Docusign and its customers have saved? And its just the beginning.'):
	    envelopes_df = list_envelopes()

    # code for donut plot
    labels = envelopes_df['status'].value_counts().index.tolist()
    values = envelopes_df['status'].value_counts().values.tolist()

    l = [0] * len(values)
    maxpos = values.index(max(values))
    l[maxpos] = 0.1

    fig = go.Figure(data=[go.Pie(labels=labels, values=values,
                    pull=l, hole=.3)])
    fig.update_layout(title_text='Envelope status')
    st.plotly_chart(fig, use_container_width=True)

    # code for bar plot
    dates = envelopes_df['created_date_time']
    dates = dates.apply(lambda x : x.split("T")[0])

    labels = dates.value_counts().index.tolist()
    values = dates.value_counts().values.tolist()

    # green bar with max value highlighting
    colors = ['cornflowerblue'] * len(labels)
    maxval = max(values)
    ind = [i for i, v in enumerate(values) if v == maxval]

    for i in ind:
        colors[i] = 'green'
        layout = dict(
            xaxis=dict(title='Date', ticklen=5, zeroline=False),
            yaxis=dict(title='No. of envelopes', ticklen=5, zeroline=False)
            )

    fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=colors
        )], layout=layout)

    fig.update_layout(title_text='Sent Envelopes')
    st.plotly_chart(fig, use_container_width=True)
