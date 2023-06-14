
# -- documentation --
# project : nhs web app
# author : ceefar

# -- imports --
import streamlit as st
from dotenv import load_dotenv
import os
import openai

# -- streamlit setup --
def on_page_load():
    """ self referencing af """
    st.set_page_config(layout="wide")

# -- frontend/backend setup --
on_page_load()   
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# -- 
def main():
    col_1_selectbox, col_2_chatbox = st.columns([2,3], gap="large")
    with col_1_selectbox:
        st.write("Sumnt")
    with col_2_chatbox:
        st.markdown(f"#### NHS-GPT")
        user_chat_entry = st.text_input(label="What wait time information would you like to know?", value="What are the wait times for Neurology at Barts NHS Trust?", help="E.g. What are the wait times for `DEPARTMENT` at `NHS TRUST`")


if __name__ == "__main__":
    main()





# being deadly serious
# how many of the data engineers of the what 4/5 (juniors btw) at that NHS job that I couldnt get 
# do you think have done *any* NHS projects in their actual spare time (they're studying so obvs might do it during but I literally mean for fun...)