
# -- documentation --
# project : nhs web app
# author : ceefar

# -- imports --
import streamlit as st
from streamlit.errors import StreamlitAPIException 
import os
import openai
import folium
import datetime
from streamlit_folium import folium_static
from dotenv import load_dotenv
# -- internal imports --
import func_web_api as webapi
from func_misc import Misc, NHSColors, get_cleaned_dept, hex_to_rgb, st_page_load

# -- frontend/backend setup : st, env, openai api --
try:
    st_page_load() # just ensures this is run incase for some reason it hasnt been which tbh happens mostly just during debugging / dev hence why am still leaving it for now
except StreamlitAPIException as stErr:
    print(f"{stErr = }")
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
def get_london_daily_avg_first_apt(user_department, date):
    cleaned_dept = get_cleaned_dept(user_department)
    london_avg_data = webapi.get_london_daily_avg_first_apt(cleaned_dept, date)
    return london_avg_data

@st.cache_data
def get_mids_daily_avg_first_apt(user_department, date):
    cleaned_dept = get_cleaned_dept(user_department)
    mids_avg_data = webapi.get_mids_daily_avg_first_apt(cleaned_dept, date)
    return mids_avg_data

@st.cache_data
def get_ney_daily_avg_first_apt(user_department, date):
    cleaned_dept = get_cleaned_dept(user_department)
    ney_avg_data = webapi.get_ney_daily_avg_first_apt(cleaned_dept, date)
    return ney_avg_data

@st.cache_data
def get_swest_daily_avg_first_apt(user_department, date):
    cleaned_dept = get_cleaned_dept(user_department)
    swest_avg_data = webapi.get_swest_daily_avg_first_apt(cleaned_dept, date)
    return swest_avg_data

@st.cache_data
def get_hospital_names_for_region(region): # note isnt an api function was just due to setup, can actually untangled/abstract out just to where its relevant
    regions_hospital_names_list = [key.title().replace("Nhs", "NHS") for key, value in Misc.hospitals_regions.items() if value == region] # also formats the list to title case
    print(f"FUNC : get_hospital_names_for_region - VAR : {regions_hospital_names_list = }") # temp debugging prints that will remove when not testing, is just easier than logs for rapid development
    return regions_hospital_names_list

@st.cache_data
def get_min_max_first_apt_wait_for_dept_countrywide(user_department_entry):
    list_of_tuples_of_countrywide_waits = webapi.get_min_max_first_apt_wait_for_department_countrywide(user_department_entry)
    print(f"FUNC : get_min_max_first_apt_wait_for_dept_countrywide - VAR : {list_of_tuples_of_countrywide_waits = }") # temp debugging prints that will remove when not testing, is just easier than logs for rapid development
    return list_of_tuples_of_countrywide_waits

@st.cache_data
def get_min_max_first_apt_wait_for_department_and_region(user_department_entry, user_region_shortcode):
    min_max_for_dept_and_region = webapi.get_min_max_first_apt_wait_for_department_and_region(user_department_entry, user_region_shortcode)
    return min_max_for_dept_and_region

@st.cache_data
def get_ranked_hospitals(department, date):
    hospitals = webapi.rank_hospitals(department, date)
    return hospitals

@st.cache_data
def display_hospitals(hospital_name, department, date):
    """ get the ranked hospitals for a given department and for a given date, in format : `2023-06-20` """
    hospitals = get_ranked_hospitals(department, date)
    # Find the selected hospital and the hospitals ranked 1 above and below
    selected_hospitals = []
    for i, hospital in enumerate(hospitals):
        if hospital['hospital_name'].lower() == hospital_name.lower():
            if i > 0:
                selected_hospitals.append(hospitals[i - 1])  # hospital ranked 1 above
            selected_hospitals.append(hospital)  # selected hospital
            if i < len(hospitals) - 1:
                selected_hospitals.append(hospitals[i + 1])  # hospital ranked 1 below
            break
    # -- 
    st.write(selected_hospitals)

# -- TO MOVE TO SOME NEW ST MODULE (or just the misc module tbf?) --
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

def display_selected_trust_wait_times_overview(trust_first_apt_wait_time_from_db_name, trust_first_apt_wait_time_from_db_wait_time, trust_avg_wait_time_from_db_wait_time):
    """ should add basic info as well from datasets/hospitals.csv """
    custom_title("Your Selected Trust", f"{trust_first_apt_wait_time_from_db_name}")
    top_col_1, top_col_2 = st.columns(2)
    with top_col_1:
        st.metric(label="First Appointment Avg Wait", value=f"{trust_first_apt_wait_time_from_db_wait_time} weeks")
    with top_col_2:
        st.metric(label="Treatment Avg Wait", value=f"{trust_avg_wait_time_from_db_wait_time} weeks")
    st.divider()

def display_min_max_wait_times_for_region(user_region_entry, min_max_for_dept_x_region, trust_first_apt_wait_time_from_db_wait_time, trust_first_apt_wait_time_from_db_name):
    """ """
    custom_title("Min Max Wait Times", f"For {user_region_entry} Region")
    st.write("")
    subheader_style = f"font-size: 0.9rem; margin-top: -10px; margin-bottom: 0px; color: {NHSColors.NHS_Purple}; letter-spacing: 1px"
    minmax_col_1, minmax_col_2, minmax_col_3 = st.columns(3)
    min_wait_name, min_wait_time, max_wait_name, max_wait_time = min_max_for_dept_x_region[0]
    with minmax_col_1:
        st.markdown(f"<p style='{subheader_style}'><b>Fastest NHS Trust In The Region</b></p>", unsafe_allow_html=True)
        st.metric(label=min_wait_name, value=min_wait_time, delta=trust_first_apt_wait_time_from_db_wait_time - min_wait_time)
        st.write("###")
    with minmax_col_2:
        st.markdown(f"<p style='{subheader_style}'><b>Slowest NHS Trust In The Region</b></p>", unsafe_allow_html=True)
        st.metric(label=max_wait_name, value=max_wait_time, delta=trust_first_apt_wait_time_from_db_wait_time - max_wait_time)
        st.write("###")
    with minmax_col_3:
        st.markdown(f"<p style='{subheader_style}'><b>Your Selected NHS Trust</b></p>", unsafe_allow_html=True)
        st.metric(label=trust_first_apt_wait_time_from_db_name, value=trust_first_apt_wait_time_from_db_wait_time)
        st.write("###")
    st.divider()

def display_min_max_wait_times_countrywide(user_department_entry, trust_first_apt_wait_time_from_db_wait_time):
    custom_title("Min Max Wait Times", f"Countrywide")
    list_of_tuples_of_countrywide_waits = get_min_max_first_apt_wait_for_dept_countrywide(user_department_entry)
    sorted_countrywide_waits = sorted(list_of_tuples_of_countrywide_waits, key=lambda x: x[-1])
    for trust_waits_info_tuple in sorted_countrywide_waits:
        delta = trust_first_apt_wait_time_from_db_wait_time - trust_waits_info_tuple[2]
        subheader_style = f"font-size: 0.9rem; margin-top: -10px; margin-bottom: 0px; color: {NHSColors.NHS_Purple}; letter-spacing: 1px"
        st.markdown(f"<p style='{subheader_style}'><b>{'Fast' if delta >= 0 else 'Slow'}est NHS Trust In The Country</b></p>", unsafe_allow_html=True)
        st.metric(label=f"{trust_waits_info_tuple[0]} {trust_waits_info_tuple[1]}", value=trust_waits_info_tuple[2], delta=delta)
        st.write("###")

def display_regional_averages(user_department_entry, user_date_entry):
    st.write("###")
    region_avg_col_1, region_avg_col_2, region_avg_col_3, region_avg_col_4, region_avg_col_5, region_avg_col_6 = st.columns(spec=6, gap="medium")
    # -- region avgs, first apt, now date can update, note that this is currently the only thing date will update tho --
    swest_daily_avg_first_apt_wait = get_swest_daily_avg_first_apt(user_department_entry, user_date_entry)
    ney_daily_avg_first_apt_wait = get_ney_daily_avg_first_apt(user_department_entry, user_date_entry)
    london_avg = get_london_daily_avg_first_apt(user_department_entry, user_date_entry)
    mids_avg = get_mids_daily_avg_first_apt(user_department_entry, user_date_entry)
    # -- yes obvs need to do the proper ui here with columns -- 
    # -- and with this whole thing abstracted into its own function too, if refactoring make this stuff class based 100% --
    with region_avg_col_1:
        st.metric(label="ALL LONDON Avg Wait", value=f"{float(london_avg):.1f}")
    with region_avg_col_2:
        st.metric(label="ALL MIDLANDS Avg Wait", value=f"{float(mids_avg):.1f}")
    with region_avg_col_3:
        st.metric(label="ALL SWEST Avg Wait", value=f"{float(swest_daily_avg_first_apt_wait):.1f}")
    with region_avg_col_4:
        st.metric(label="ALL NEY Avg Wait", value=f"{float(ney_daily_avg_first_apt_wait):.1f}")
    st.divider()


# -- main --
def main():
    # -- title --
    custom_title(title="NHS Web App", subtitle="Do Stuff!", want_div=True)
    # -- sidebar --
    with st.sidebar:
        app_mode = st.radio(label="Select a Mode", options=["Manual", "NHS GPT"])

    # -- app mode : manual --
    if app_mode == "Manual":

        # -- NOTE : properly abstract all this stuff and bang it in functs/modules when the logic is finalised

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

        # -- additional test functionality for date in sidebar, is at the bottom due to control flow but can fix this by abstracting everything properly when completed --
        with st.sidebar:
            custom_div(NHSColors.NHS_Dark_Blue)
            first_valid_date = date = datetime.datetime(2023, 6, 13) # do this with an api call but this will be fine for now
            user_date_entry = st.date_input(label="Enter Date - NOT IMPLEMENTED PROPERLY YET!")

        # -- make api calls to get selected data --
        trust_first_apt_wait_time_from_db_name, trust_first_apt_wait_time_from_db_wait_time = get_trust_curr_first_apt_for_a_department(user_department_entry, user_trust_entry)
        trust_avg_wait_time_from_db_name , trust_avg_wait_time_from_db_wait_time = get_trust_curr_avg_wait_time_for_a_department(user_department_entry, user_trust_entry) 
        min_max_for_dept_x_region = get_min_max_first_apt_wait_for_department_and_region(user_department_entry, user_region_shortcode)

        # -- main display for data returned from db which is pulled from nhs mpc api daily via cicd pipeline --
        tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs(["Your Trust Info", "Region Min/Max", "Country Min/Max", "Regional Averages", "Rank Snapshot"])
        with tab_1:
            display_selected_trust_wait_times_overview(trust_first_apt_wait_time_from_db_name, trust_first_apt_wait_time_from_db_wait_time, trust_avg_wait_time_from_db_wait_time)
        with tab_2:
            display_min_max_wait_times_for_region(user_region_entry, min_max_for_dept_x_region, trust_first_apt_wait_time_from_db_wait_time, trust_first_apt_wait_time_from_db_name)
        with tab_3:
            display_min_max_wait_times_countrywide(user_department_entry, trust_first_apt_wait_time_from_db_wait_time)
        with tab_4:
            display_regional_averages(user_department_entry, user_date_entry)
        
        with tab_5:
            # N0TE : USING DATE HERE BUT REMEMBER THATS NOT FULLY IMPLEMENTED YET, THO LEAVING AS ITS WORTH DOING THE ERROR HANDLING AS IT ARISES!
            display_hospitals(user_trust_entry, user_department_entry, user_date_entry) 


            # CONTINUE FROM HERE - GET THE RETURN AND DO DISPLAY SEPERATELY, THEN ABSTRACT IT OUT PROPERLY AGAIN AND MOVE THE ABOVE N0TE ABOUT DATE INTO THERE TOO

            # basically to do from here is...
            # finish this regional averages bit,
            # then do cloud, date, chatbot, unit tests, and owt else that may be notable / pressing 
            # then new challenger thing initial project just fuck about as need to get back to grips with ocr and comp vision again huh


    # -- app mode : chatbot --
    elif app_mode == "NHS GPT":
        st.markdown("##### NHS GPT")
        user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")

    

if __name__ == "__main__":
    main()



# [ FINAL TOD0! ]
# -------------
# LAST REMAINING TABS TO ADD
# - update this display tab to do view this shit properly
# - add the rest of the averages for regions 
#   - its tab 4, do the cols too btw, and check it in mobile view also primarily 
# - add in the date thing just for this avg regions thing, AND MAKE SURE THAT IS SUPER CLEAR
#   - e.g. if selected date not currentdate then display a tooltip where valid bosh
#   - do some basic error handling also
#       - i.e. change the date to too early so there is no data
#       - i.e. dont let the date go past the current date and also find the first valid date of data 
#       - could also start unit testing here too tbf if u want
# - add in some super basic info to selected trust tab for like how fast slow it is in comparison, use text not delta (tho ig delta too if you want)
# THEN 
# - 100% put on cloud and ensure it works
# THEN
# - do chatbot multifunction thing just to test it pls, legit maybe even write a new api module for this as when refactoring can improve it all
# - 100% give it all the data from the mids averages for a week and ask it info on how things have changed over time!
#   - legit mostly just to see the quality of the response
#   - also note when making question have some kinda ui where you can copy them over (since not valid for a help tooltip)
# THEN
# - please unit-tests for once im actually interested in it and all of this will be super useful for wito project which we may even start later today :D
# THEN (back to tabs)
# - list for region ranked with urs highlighted
# - list of other fast trusts countrywide, like top 10 or 20 or sumnt (as could be useful to just see, could then easily tie this to postcode thing too)
# - rank of urs in country and any other random additional info

# QUICKLY UPDATE THE YML (so we're only at the preset times and not on 6/7 hour CRON)

# CHOOSE DATE THING IN SIDEBAR
# - with unit tests so do that with this basically
# UNIT TESTS & BASIC ERROR HANDLING
# - see north west general surgery (this kinda stuff may also be resolved by date change or even just names issue, tho this specifically is Alder Hey Children'S thats causing the problem)
# GPT INTEGRATION HELLA QUICK

# QUICKLY UPDATE COLOUR SO SUBTITLE "SEARCH FOR WAIT TIME" && CHANGE DO STUFF TO SAY SOMETHING LEGIT FFS EVEN IF TRASH ITS JUST A DRAFT U CLOWN 
# ITS CHEEKY AND NOT EVEN PORTFOLIO READY PROJECT BUT TAKE THE CUSTOM HTML AND CSS AND PUT IT IN ITS OWN FILE 
# OMG DO THE GPT GLOBAL STYLES THING OR ATLEAST CHECK IF THIS WORKS
# ALSO A BG IMG LIKE LINED PAPER WOULD BE NICE BUT TBF DW LMAO

# MAKE IT LIVE!
# - CHANGE THE CRON TO BE SCHEDULED, HAVE IT SCHEDULDED AT LIKE 1/2 THEN LIKE 3/4 ALSO JUST INCASE
# - ENSURE WE DONT HAVE THE CNX ISSUE, WHICH REMEMBER IS LIKE IF IT ERRORS THEN THE CNX NEEDS TO BE RESET TING (also singleton tho?)

# THEN EITHER WITO PROJECT OR QUICKLY SIDE PROJECT ON GAME FOR A FEW DAYS (latter preferably as still rusty and wanna be fresh af so i dont waste time due to bad coding)
