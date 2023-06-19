
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
from func_misc import Misc, NHSColors, get_cleaned_dept, hex_to_rgb


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


# -- MOVE DIS TO SOME NEW ST MISC MODULE? (or just the misc module tbf) --
def custom_div(hex_colour=NHSColors.NHS_Dark_Green, thickness=2):
    r_for_a, g_for_a, b_for_a = hex_to_rgb(hex_colour)
    divider_style = f"border-bottom: {thickness}px dashed rgba({r_for_a}, {g_for_a}, {b_for_a}, 0.3); margin-top: 20px;"
    st.markdown(f"<hr style='{divider_style}'>", unsafe_allow_html=True)

def custom_title(title, subtitle, want_div=False):
    """ custom CSS style for the title and subtitle to fix excessive padding in st """
    title_style = f"font-size: 1.8rem; margin-bottom: -20px; color: {NHSColors.NHS_Light_Blue};"
    subtitle_style = f"font-size: 0.9rem; margin-top: -10px; margin-bottom: {0 if want_div else 20}px; color: {NHSColors.NHS_Dark_Green}; letter-spacing: 1px"
    st.markdown(f"<h1 style='{title_style}'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='{subtitle_style}'><b>{subtitle}</b></p>", unsafe_allow_html=True)
    if want_div:
        # -- convert the given colour to rgb so we can set its alpha --
        custom_div()


# -- 
def main():
    # --
    custom_title(title="NHS Web App", subtitle="Do Stuff!", want_div=True)
    # --
    with st.sidebar:
        app_mode = st.radio(label="Select a Mode", options=["Manual", "NHS GPT"])

    # -- abstract the below stuff into own funcs plis btw --
    if app_mode == "Manual":

        # -- top input section --
        st.markdown("##### Search For Wait Time Info")
        top_col_1, top_col_2, top_col_3 = st.columns([1,1,1], gap="medium")
        with top_col_1:
            user_department_entry = st.selectbox(label="Select a Department", options=Misc.departments_list)
        with top_col_2:
            user_region_entry = st.selectbox(label="Select a Region", options=[region.title() for region in Misc.regions_list.keys()]) # formats the region list to title case
            user_region_shortcode = Misc.regions_list[user_region_entry.lower()]
        with top_col_3:
            user_trust_entry = st.selectbox(label="Select an NHS Trust", options=get_hospital_names_for_region(user_region_shortcode)) # must convert the param back to lower because of this
        custom_div()

        # -- make api calls to get selected data --
        trust_first_apt_wait_time_from_db_name, trust_first_apt_wait_time_from_db_wait_time = get_trust_curr_first_apt_for_a_department(user_department_entry, user_trust_entry)
        _ , trust_avg_wait_time_from_db_wait_time = get_trust_curr_avg_wait_time_for_a_department(user_department_entry, user_trust_entry) # trust_avg_wait_time_from_db_name
        min_max_for_dept_x_region = webapi.get_min_max_first_apt_wait_for_department_and_region(user_department_entry, user_region_shortcode)


        # -- NOTE : properly abstract this and bang it in functs/modules when the logic is finalised


        # -- display segment 1 : overview --
        custom_title("Your Selected Hospital", f"{trust_first_apt_wait_time_from_db_name}")
        top_col_1, top_col_2 = st.columns(2)
        with top_col_1:
            st.metric(label="First Appointment Avg Wait", value=f"{trust_first_apt_wait_time_from_db_wait_time} weeks")
        with top_col_2:
            st.metric(label="Treatment Avg Wait", value=f"{trust_avg_wait_time_from_db_wait_time} weeks")
        st.divider()



        # FASTEST SLOWEST COUNTRYWIDE, && REGIONAL, && RANKED (FOR BOTH OOO), && AVERAGES FOR REGIONS -> ALL AS TABS
        # - QUICKLY THINK ABOUT EXACTLY HOW YOU WANT TO USE THIS!
        #   - defo starting with fastest in the country and fastest in the region and your comparison (also some text based rank would be good here, this is basically just overview tab)
        #   - defo do a ranking tab
        # BANG YOUR SELECTED THING ABOVE IN THE TABS TOO DUHHHHHH

        # QUICKLY UPDATE COLOUR SO SUBTITLE "SEARCH FOR WAIT TIME" && CHANGE DO STUFF TO SAY SOMETHING LEGIT FFS EVEN IF TRASH ITS JUST A DRAFT U CLOWN 
        # CHOOSE DATE THING IN SIDEBAR
        # - with unit tests so do that with this basically
        # UNIT TESTS & BASIC ERROR HANDLING
        # - see north west general surgery (this kinda stuff may also be resolved by date change or even just names issue, tho this specifically is Alder Hey Children'S thats causing the problem)
        # GPT INTEGRATION HELLA QUICK

        # MAKE IT LIVE!
        # - CHANGE THE CRON TO BE SCHEDULED, HAVE IT SCHEDULDED AT LIKE 1/2 THEN LIKE 3/4 ALSO JUST INCASE
        # - ENSURE WE DONT HAVE THE CNX ISSUE, WHICH REMEMBER IS LIKE IF IT ERRORS THEN THE CNX NEEDS TO BE RESET TING (also singleton tho?)

        # THEN EITHER WITO PROJECT OR QUICKLY SIDE PROJECT ON GAME FOR A FEW DAYS (latter preferably as still rusty and wanna be fresh af so i dont waste time due to bad coding)

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

