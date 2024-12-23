import streamlit as st
import requests

def create_thread(title):
    url = 'http://localhost:5000/threads'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.post(url, json={'title': title}, headers=headers)
    return response

def fetch_threads():
    url = 'http://localhost:5000/threads'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.session_state.threads = response.json()
    else:
        st.error("Failed to fetch threads.")
    return response

st.sidebar.page_link('frontend.py', label='Home')
st.sidebar.page_link('pages/create_thread.py', label='Create Thread')

st.sidebar.button("Logout", on_click=lambda: (st.session_state.clear(), st.switch_page('pages/login.py')))

st.subheader("Create a New Thread")
new_thread_title = st.text_input("Thread Title")
if st.button("Create Thread"):
    if not new_thread_title.strip():
        st.error("Thread title cannot be empty.")
    else:
        response = create_thread(new_thread_title)
        if response.status_code == 201:
            st.success("Thread created successfully.")
            fetch_threads()
            st.switch_page('frontend.py')
        else:
            st.error("Failed to create thread.")