# -- imports --
import streamlit as st
import requests
import json

# response = requests.get('http://localhost:5000/api/data')

# if response.status_code == 200:
#     data = response.json()
#     st.write(data)
# else:
#     st.write('Failed to get data from API')



# Use a Streamlit widget to collect the value of 'param' from the user
param_value = st.text_input(label="Enter a value: ", value="WALSALL HEALTHCARE NHS TRUST")

if st.button(label="Geddit"):
    # Make a GET request to the Flask API
    response = requests.get(f"http://localhost:5000/api/trust_data?param={param_value}")

    # Parse the JSON response
    data = response.json()

    # Display the data in your Streamlit app
    st.write(data)