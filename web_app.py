
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
def get_trust_curr_avg_wait_time_for_a_department(user_department, user_trust):
    wait_time_data = webapi.get_trust_curr_avg_wait_time_for_a_department(user_department, user_trust)
    print(f"{wait_time_data = }")
    return wait_time_data[0]

@st.cache_data
def get_trust_curr_first_apt_for_a_department(user_department, user_trust):
    wait_time_data = webapi.get_trust_curr_first_apt_for_a_department(user_department, user_trust)
    print(f"{wait_time_data = }")
    return wait_time_data[0]

@st.cache_data
def get_hospital_names_for_region(region): # note isnt an api function was just due to setup, can actually untangled/abstract out just to where its relevant
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
            trust_first_apt_wait_time_from_db = get_trust_curr_first_apt_for_a_department(user_department_entry, user_trust_entry)
            trust_avg_wait_time_from_db = get_trust_curr_avg_wait_time_for_a_department(user_department_entry, user_trust_entry)
            st.divider()
            st.markdown(f"##### {trust_first_apt_wait_time_from_db[0]}")
            st.metric(label="First Appointment Avg Wait", value=trust_first_apt_wait_time_from_db[1])
            st.metric(label="Treatment Avg Wait", value=trust_avg_wait_time_from_db[1])

            # -- 
            st.divider()
            print(f"{user_department_entry = }")
            london_avg = webapi.get_london_daily_avg_first_apt(user_department_entry if user_department_entry != "Ear Nose and Throat" else "ent")
            mids_avg = webapi.get_mids_daily_avg_first_apt(user_department_entry if user_department_entry != "Ear Nose and Throat" else "ent")
            st.metric(label="ALL LONDON Avg Wait", value=f"{float(london_avg):.1f}")
            st.metric(label="ALL MIDLANDS Avg Wait", value=f"{float(mids_avg):.1f}")
            

        elif app_mode == "NHS GPT":
            st.markdown("##### NHS GPT")
            user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")
            

if __name__ == "__main__":
    main()



# [DONE]
# ADDED ALL MIDS HOSPS
# ADDED NEW TABLE FOR AVG WAIT (NOT JUST FIRST APT)
# ADD AVG TREATMENT TIME, MAKE THEM BOTH METRICS
# STORED PROCEDURE FOR FIRST_APT AVERAGES IN NEW TABLE


# ADD TO WEB APP...
# REGIONS AVERAGE 
# FASTEST IN REGION
# SLOWEST IN REGION


# IMPROVE THE OTHER METRIC DISPLAY
# - start thinking about specific usecases now please, particularly own version!
# ADD BARTS AND A FEW OTHER LONDON HOSPS TOO!
# - including the averages table
# - actually just do all london too
# AND ACTUALLY YH USE A CACHED FUNCTION TO GET NAMES FROM THE DB INSTEAD WHILE WE ARE TESTING 100%!
# DO POSTCODES
# PUT ON CLOUD!
# ADD THE OTHER AVERAGE TO THE DB TOO!
# ADD THE CHATBOT
# CLASS BASED AND DESIGN PATTERNS x DATA STRUCTURES



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