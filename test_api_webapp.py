
# -- imports --
import streamlit as st
import requests
import json
# -- internal imports --
from func_misc import st_page_load

# -- setup --
st_page_load()

# -- temp column ui setup --
col_1, col_2 = st.columns(2, gap="large")

# -- 
with col_1:

    # -- get user info for wait times data --
    hospital_value = st.text_input(label="Enter a hospital: ", value="WALSALL HEALTHCARE NHS TRUST")
    department_value = st.text_input(label="Enter a department: ", value="Cardiology")

    # -- button to get first apt wait times data for a given trust and department --
    if st.button(label="Get Wait Times Data"):
        # -- make a GET request to the Flask API
        response = requests.get(f"http://localhost:5000/api/get_first_apt_wait_times?hospital={hospital_value}&department={department_value}")
        # -- parse the JSON response
        trust_dept_wait_times_data = response.json()
        # -- display the data --
        st.markdown(f"#### First Appointment Wait Times")
        st.write("")
        for data in trust_dept_wait_times_data:
            data_date = data["date"]
            data_dept = data["dept"]
            data_trust = data["trust"]
            data_wait_time = data["wait_time"]
            # --
            st.write(data_date)
            st.write(f"- {data_wait_time} Weeks Wait")
            st.write("###")

# -- 
with col_2:

    # -- get all trust names --
    region_list = ["all","mids", "london", "ney"]
    user_region = st.selectbox(label="Region : ", options=region_list)
    if user_region == "all":
        all_trust_names = requests.get('http://localhost:5000/api/all_trusts')
    else:
        all_trust_names = requests.get(f'http://localhost:5000/api/all_trusts?region={user_region}')
    # --
    if st.button(label="Get Trust Names Data"):
        st.write("")
        if all_trust_names.status_code == 200:
            all_trust_names = all_trust_names.json()
            for i, a_trust_name in enumerate(all_trust_names):
                st.write(f"{i+1}. {a_trust_name['hospital_name']}")
        else:
            st.write('Failed to get data from API')