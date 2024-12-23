import streamlit as st
import requests

st.sidebar.page_link('frontend.py', label='Home')
st.sidebar.page_link('pages/register.py', label='Register')
st.sidebar.page_link('pages/login.py', label='Login')

def login(email, password):
    url = 'http://localhost:5000/login'
    response = requests.post(url, json={'email': email, 'password': password})
    if response.status_code == 200:
        st.session_state.access_token = response.json().get('access_token')
        st.session_state.logged_in = True
    return response

def fetch_threads():
    url = 'http://localhost:5000/threads'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.session_state.threads = response.json()
    elif response.status_code == 422:
        st.session_state.logged_in = False
        st.switch_page('frontend.py')
    else:
        print(response.json())
        st.error("Failed to fetch threads.")
    return response

st.subheader("Login")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Login", key='login_button'):
    response = login(email, password)
    if response.status_code == 200:
        st.success("Logged in successfully.")
        fetch_threads()
        st.switch_page('frontend.py')
    else:
        st.error(response.json().get('error', 'Login failed.'))