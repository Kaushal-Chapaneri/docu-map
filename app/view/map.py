"""
filename : map.py

Page : Generate Map

This script is responsible for generating map using Arcgis javascript library \
    and showcasing generated maps.
"""

import streamlit as st
import re
import json
import geopandas as gpd
import zipfile
import glob
from html2image import Html2Image
from datetime import datetime
import os

from app.utils.utilities import load_config
from app.utils.utilities import load_arcgis_js
from app.utils.utilities import page_title

def map_input():
    """
    Function for Map page, takes shape input and calls arcgis javascript library \
        and generates map

    input :: 

    output :: Map generated for input shape file.
    """

    page_title("Generate Map")
    st.sidebar.write('')

    config = load_config()
    
    page = st.sidebar.selectbox("Select a page",
                    ["Map input", "View map"])

    if page == "Map input":

        with st.form(key='map_input'):

            map_title = st.text_input('Title')
            zip_file = st.file_uploader('Select zip file', key='upload_doc', type=["zip"])
        
            submit = st.form_submit_button('Submit')

        if submit:
            if not map_title:
                return st.error('Please enter title.')
            if zip_file is not None:
                myzipfile = zipfile.ZipFile(zip_file)
                myzipfile.extractall('asset/tmp')
            else:
                return st.error('Please select shape file.')

            shape_file_name = glob.glob('asset/tmp/'+zip_file.name[:-4]+'/*.shp')[0]

            if not config["arcgis_key"]:
                return st.error('Arcgis authentication key missing.')

            try:

                gdf = gpd.read_file(shape_file_name)
                data = json.loads(gdf['geometry'].to_json())['features']

                # here we are getting javascript code to call arcgis library.
                arcgis_js = load_arcgis_js()

                matches = re.finditer('<<(\w*)>>', arcgis_js)

                for i in matches:

                    if i.group(0) == "<<title>>":
                        arcgis_js = arcgis_js.replace(i.group(0), map_title)
                        
                    if i.group(0) == "<<api_key>>":
                        arcgis_js = arcgis_js.replace(i.group(0), config["arcgis_key"])
                        
                    if i.group(0) == "<<cordi>>":
                        arcgis_js = arcgis_js.replace(i.group(0), json.dumps(data[0]['geometry']['coordinates'][0][0][0][:2]))
                        
                    if i.group(0) == "<<multi_ploy_list>>":
                        arcgis_js = arcgis_js.replace(i.group(0), json.dumps(data[0]['geometry']['coordinates'][0]))

                map_file_name = "asset/html/"+zip_file.name[:-4]+".html"
                file_dump = open(map_file_name,"w")
                file_dump.write(arcgis_js)  
                file_dump.close()

                hti = Html2Image(custom_flags=['--virtual-time-budget=10000', '--hide-scrollbars'],output_path='asset/images/')
                map_image_name = map_title+"_"+str(datetime.today())+"_"+zip_file.name[:-4]+'.png'
                hti.screenshot(html_file=map_file_name,save_as=map_image_name,size=(946,575))

                st.image('asset/images/'+map_image_name)

            except Exception as e:
                return st.error("There was some issue in generating map.")

    else:

        images_path = 'asset/images'

        images = os.listdir(images_path)

        image = st.selectbox("Select an image",images)

        st.write('')
        st.markdown("<b>Map title</b> : "+image.split("_")[0], unsafe_allow_html=True)
        st.write('')
        st.markdown("<b>Map created at</b> : "+image.split("_")[1].split(".")[0], unsafe_allow_html=True)
        st.write('')

        st.image(images_path+"/"+image)

           


