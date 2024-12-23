import streamlit as st
import requests

st.sidebar.page_link('frontend.py', label='Home')
st.sidebar.page_link('pages/register.py', label='Register')
st.sidebar.page_link('pages/login.py', label='Login')

def register(email, password):
    url = 'http://localhost:5000/register'
    response = requests.post(url, json={'email': email, 'password': password})
    return response

st.subheader("Register")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Register", key='register_button'):
    response = register(email, password)
    if response.status_code == 201:
        st.success("Registered successfully.")
        st.switch_page('pages/login.py')
    else:
        st.error(response.json().get('error', 'Registration failed.'))
