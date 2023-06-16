
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


# -- 
def main():
    # --
    st.markdown(f"### NHS Web App")
    st.divider()
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

        # --
        st.markdown(f"##### Selected Hospital :")
        st.markdown(f"{trust_first_apt_wait_time_from_db_name}")
        trust_wait_col_1, trust_wait_col_2 = st.columns([1,1])
        with trust_wait_col_1:
            st.metric(label="First Appointment Avg Wait", value=trust_first_apt_wait_time_from_db_wait_time)
        with trust_wait_col_2:
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

        

    elif app_mode == "NHS GPT":
        st.markdown("##### NHS GPT")
        user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")
            

if __name__ == "__main__":
    main()


# REGIONAL AVERAGES

# NATIONWIDE MIN MAX
# - maybe just for regions and then you can go do that yourself if you want (i.e. to see that region u can just go select it? - would be fine for now anyways)

# CONTINUE TO BELOW POSTCODES N TING!
# - YOU WANT TO BE ABLE TO VIEW THE INFO ON A TRUST I.E THE HOSPITALS AND DETAILS AND THEIR RELATION TO YOU
# - CAN ALL BE DONE VIA THE NHS CSV AND BASICALLY JUST THE OLD CODE FOR MAPS N STUFF

# ADD BACK ON BUTTON PRESS BTW DUHHHHH!

# COMPLETE THE BACKEND STUFF

# SINGLETON CONNECTION THING SO WE DONT LOAD AND RECONNECT EVERY TIME?

# THEN
# POSTCODES AND MAP STUFF
# PUT ON CLOUD
# ABILITY TO GO BACK IN TIME WITH WHOLE DATE PASSING THING TO WEB_API FUNCTIONS PLEASE, DO THIS BY HAVING A CAL IN SIDEBAR!
# DATACLASSES AND CLASS BASED STRUCTURE! (and data structures x design patterns)
# CHATBOT STUFF
 
# FOR FASTEST AND SLOWEST, I.E MIN MAX, DO IN SQL QUERY AND CACHE IT BOSH! <<<<<<<<<<<<<<<<<<<<<<<<<<<<< THIS FIRST RNRN OMG MAN! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


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