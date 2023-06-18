
# -- documentation --
# project : nhs web app
# author : ceefar

# -- imports --
import streamlit as st
import os
import openai
import folium
from streamlit_folium import folium_static
from dotenv import load_dotenv
# -- internal imports --
import func_web_api as webapi
from func_misc import Misc, get_cleaned_dept


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
def get_london_daily_avg_first_apt(user_department):
    cleaned_dept = get_cleaned_dept(user_department)
    london_avg_data = webapi.get_london_daily_avg_first_apt(cleaned_dept)
    return london_avg_data

@st.cache_data
def get_mids_daily_avg_first_apt(user_department):
    cleaned_dept = get_cleaned_dept(user_department)
    mids_avg_data = webapi.get_mids_daily_avg_first_apt(cleaned_dept)
    return mids_avg_data

@st.cache_data
def get_hospital_names_for_region(region): # note isnt an api function was just due to setup, can actually untangled/abstract out just to where its relevant
    regions_hospital_names_list = [key.title().replace("Nhs", "NHS") for key, value in Misc.hospitals_regions.items() if value == region] # also formats the list to title case
    print(f"{regions_hospital_names_list = }")
    return regions_hospital_names_list


# -- TEMP AF --
def display_temp_faux_map():
    initial_location = [50.389484405517578, -3.9596600532531738]
    folium_map = folium.Map(location=initial_location, zoom_start=12)
    folium.Marker(location=initial_location, popup="Your Location").add_to(folium_map)
    folium_static(folium_map, width=400, height=400) # doesnt properly resize oof

# -- 
def main():
    # --
    st.markdown(f"### NHS Web App")
    st.write("###")
    # --
    with st.sidebar:
        app_mode = st.radio(label="Select a Mode", options=["Manual", "NHS GPT"])

    # -- abstract the below stuff into own funcs plis btw --
    if app_mode == "Manual":

        # -- top input section --
        st.markdown("##### Search For Wait Time Info")
        top_col_1, top_col_2, top_col_3 = st.columns([1,1,1], gap="large")
        with top_col_1:
            user_department_entry = st.selectbox(label="Select a Department", options=Misc.departments_list)
        with top_col_2:
            user_region_entry = st.selectbox(label="Select a Region", options=[region.title() for region in Misc.regions_list.keys()]) # formats the region list to title case
            user_region_shortcode = Misc.regions_list[user_region_entry.lower()]
        with top_col_3:
            user_trust_entry = st.selectbox(label="Select an NHS Trust", options=get_hospital_names_for_region(user_region_shortcode)) # must convert the param back to lower because of this
        st.divider()

        # -- make api calls to get selected data
        trust_first_apt_wait_time_from_db_name, trust_first_apt_wait_time_from_db_wait_time = get_trust_curr_first_apt_for_a_department(user_department_entry, user_trust_entry)
        trust_avg_wait_time_from_db_name, trust_avg_wait_time_from_db_wait_time = get_trust_curr_avg_wait_time_for_a_department(user_department_entry, user_trust_entry)
        min_max_for_dept_x_region = webapi.get_min_max_first_apt_wait_for_department_and_region(user_department_entry, user_region_shortcode)

        # -- temp faux map --

        st.markdown(f"#### {trust_first_apt_wait_time_from_db_name}")
        temp_col_1, temp_col_2 = st.columns(2)
        with temp_col_1:
            st.metric(label="First Appointment Avg Wait", value=trust_first_apt_wait_time_from_db_wait_time)
        with temp_col_2:
            st.metric(label="Treatment Avg Wait", value=trust_avg_wait_time_from_db_wait_time)
        st.divider()


        # --
        st.markdown("##### Regional Min Max Snapshot [First Appointment Wait Times]")
        min_wait_col_1, max_wait_col_2, selected_wait_col_3 = st.columns(3)
        min_wait_name, min_wait_time, max_wait_name, max_wait_time = min_max_for_dept_x_region[0]
        with min_wait_col_1:
            st.write(f"Fastest NHS Trust In The Region [ {user_region_entry} ]")
            st.metric(label=min_wait_name, value=min_wait_time, delta=trust_first_apt_wait_time_from_db_wait_time - min_wait_time)
        with max_wait_col_2:
            st.write(f"Slowest NHS Trust In The Region [ {user_region_entry} ]")
            st.metric(label=max_wait_name, value=max_wait_time, delta=trust_first_apt_wait_time_from_db_wait_time - max_wait_time)
        with selected_wait_col_3:
            st.write(f"Your Selected NHS Trust [ {user_region_entry} ]")
            st.metric(label=trust_first_apt_wait_time_from_db_name, value=trust_first_apt_wait_time_from_db_wait_time)
        st.divider()
        

        # -- REMEMBER NEED TO MAKE THEM FUNCS HERE AND CACHE DEM --
        london_avg = get_london_daily_avg_first_apt(user_department_entry)
        mids_avg = get_mids_daily_avg_first_apt(user_department_entry)
        st.metric(label="ALL LONDON Avg Wait", value=f"{float(london_avg):.1f}")
        st.metric(label="ALL MIDLANDS Avg Wait", value=f"{float(mids_avg):.1f}")
        st.divider()

        # --
        st.write("Fastest Slowest Countrywide")
        rv = webapi.get_min_max_first_apt_wait_for_department_countrywide(user_department_entry)
        st.write(rv)

        

    elif app_mode == "NHS GPT":
        st.markdown("##### NHS GPT")
        user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")
            

if __name__ == "__main__":
    main()


# SO RNRN
# - put on cloud
# - check out the ui on mobile
# - do below new version thing and maybe quickly test thing too
#   - make small mobile changes to ui while doing this
# - continue with completing the backend  
#   - as ui really doesnt matter and id rather just have working backend to use this myself and then do sumnt new even if that is a game

# NEW VERSION
# NEW UI TO HAVE 
# - TABS
# - FIRST TAB FASTEST
#   - THIS CAN SHOW REGIONS AND COUNTRYWIDE!
# - SECOND TAB SLOWEST
# - THIRD TAB RANK

# QUICKLY TEST
# - ask gpt all maps in trust

# UI
# - add in this nationwide min max and quickly 
# - all currently available regional averages
# - this rank idea in some visualiser
# - add back on button press
# - overhaul the ui
# - custom css components
# - show hospital on map n ting
#   - all the info on a trust, i.e. the hospitals + their details, how close to postcode, etc (use nhs csv and old code for maps stuff surely duh?)
# - postcodes ting

# BACKEND
# - all regions
# - all averages table
# - all stored procedures
# - cicd
# - singleton the connection?

# CRIT / OTHER / OLD
# - ABILITY TO GO BACK IN TIME WITH WHOLE DATE PASSING THING TO WEB_API FUNCTIONS PLEASE, DO THIS BY HAVING A CAL IN SIDEBAR!
# - DATACLASSES AND CLASS BASED STRUCTURE! (and data structures x design patterns)
# - CHATBOT STUFF
