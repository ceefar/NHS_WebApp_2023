
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


# -- 
def main():
    col_1_selectbox, col_2_chatbox = st.columns([2,3], gap="large")
    with col_1_selectbox:
        st.write("Sumnt")
        st.selectbox(label="Select a Region", options=Misc.regions_list)
    with col_2_chatbox:
        st.markdown(f"#### NHS-GPT")
        user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")



if __name__ == "__main__":
    main()



# PUT V1.01 ON ST.CLOUD OF OTHER PROJECT TING
# PUT THIS ON ST.CLOUD

# DO THE REGION STUFF AS A FUNCTION AND CACHE IT
# webapi.get_db_accurate_hospital_names() 
# THEN DO THE GETTING NAMES FROM DB THING, ALSO CACHED - USING THE REGION AS THE THING THAT WILL TRIGGER A NEW CALL
# THEN ADD IN THE FULL BASIC FUNCTIONALITY HERE
# THEN START DOING POSTCODE AND MAP STUFF! (legit do this early as else it can get too complicated duh!)