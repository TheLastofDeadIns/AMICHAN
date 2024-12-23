import streamlit as st
import requests

# Состояние приложения
if 'access_token' not in st.session_state:
    st.session_state.access_token = ''
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'threads' not in st.session_state:
    st.session_state.threads = []
if 'selected_thread' not in st.session_state:
    st.session_state.selected_thread = None


# Функции взаимодействия с API
def register(email, password):
    url = 'http://localhost:5000/register'
    response = requests.post(url, json={'email': email, 'password': password})
    return response

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

def create_thread(title):
    url = 'http://localhost:5000/threads'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.post(url, json={'title': title}, headers=headers)
    return response

def add_comment(thread_id, text):
    url = f'http://localhost:5000/threads/{thread_id}/comments'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.post(url, json={'text': text}, headers=headers)
    return response

# Интерфейс пользователя
st.title("AMICHAN")

if not st.session_state.logged_in:
    st.sidebar.page_link('frontend.py', label='Home')
    st.sidebar.page_link('pages/register.py', label='Register')
    st.sidebar.page_link('pages/login.py', label='Login')
else:
    st.sidebar.page_link('frontend.py', label='Home')
    st.sidebar.page_link('pages/create_thread.py', label='Create Thread')

    st.sidebar.button("Logout", on_click=lambda: (st.session_state.clear(), st.switch_page('pages/login.py')))

    st.subheader("Threads")
    if st.button("Refresh Threads"):
        fetch_threads()
    for thread in st.session_state.threads:
        st.write(f"{thread['id']}: {thread['title']} ({thread['comment_count']} comments)")
        if st.button(f"View {thread['id']}"):
            st.session_state.selected_thread = thread
            st.switch_page('pages/view_thread.py')
