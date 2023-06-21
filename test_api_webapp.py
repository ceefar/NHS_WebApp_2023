import requests
import streamlit as st

response = requests.get('http://localhost:5000/api/data')

if response.status_code == 200:
    data = response.json()
    st.write(data)
else:
    st.write('Failed to get data from API')
