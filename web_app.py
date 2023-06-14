
# -- documentation --
# project : nhs web app
# author : ceefar

# -- imports --
import streamlit as st
from dotenv import load_dotenv
import os
import openai
# -- internal imports --
import func_web_api as webapi
from func_misc import Misc


# -- streamlit setup --
def st_page_load():
    """ self referencing af """
    st.set_page_config(layout="wide")

# -- frontend/backend setup : st, env, openai api --
st_page_load()   
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# -- st cached api functions --
@st.cache_data
def get_hospital_names_for_region(region):
    regions_hospital_names_list = [key.title().replace("Nhs", "NHS") for key, value in Misc.hospitals_regions.items() if value == region] # also formats the list to title case
    print(f"{regions_hospital_names_list = }")
    return regions_hospital_names_list


# -- 
def main():
    # --
    st.markdown(f"### NHS Web App")
    st.divider()
    # --
    with st.sidebar:
        app_mode = st.radio(label="Select a Mode", options=["Manual", "NHS GPT"])
    # --
    col_1, col_2 = st.columns([2,3], gap="large")
    with col_1:
        if app_mode == "Manual":
            st.markdown("##### Sumnt")
            user_department_entry = st.selectbox(label="Select a Department", options=Misc.departments_list)
            user_region_entry = st.selectbox(label="Select a Region", options=[region.title() for region in Misc.regions_list.keys()]) # formats the region list to title case
            user_trust_entry = st.selectbox(label="Select an NHS Trust", options=get_hospital_names_for_region(Misc.regions_list[user_region_entry.lower()])) # must convert the param back to lower because of this
        elif app_mode == "NHS GPT":
            st.markdown("##### NHS GPT")
            user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")



if __name__ == "__main__":
    main()



# DISPLAY SOME INFO FROM THE DB USING CACHED WEB API MODULE HERE QUICKLY
# THEN DO THE WHOLE AVGS THING (basically exactly as below lmao)


# DO THE REGION STUFF AS A FUNCTION AND CACHE IT
# - SO SELECT A HOSPITAL WHERE THEY MATCH FROM THE MISC VAR 
# - THEN REMOVE THIS >>>>>>> webapi.get_db_accurate_hospital_names()    
# - THEN DEFO HAVE SOMETHING BEING PULLED FROM MY DB
# - THEN ACTUALLY CONTINUE TO THE WHOLE AVERAGES THING CICD
#   - legit do think exactly what do i want tho
#   - and then start mixing it in with gpt too (as per below and the full functionality thats what I mean, just basic no long ting)

# THEN ADD IN THE FULL BASIC FUNCTIONALITY HERE
# THEN START DOING POSTCODE AND MAP STUFF! (legit do this early as else it can get too complicated duh!)

# PUT THIS ON ST.CLOUD
# PUT V1.01 ON ST.CLOUD OF OTHER PROJECT TING