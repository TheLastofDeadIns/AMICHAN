import streamlit as st
import requests

def fetch_comments(thread_id):
    url = f'http://localhost:5000/threads/{thread_id}/comments'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.session_state.comments = response.json()
    else:
        st.error("Failed to fetch comments.")
    return response

def add_comment(thread_id, text):
    url = f'http://localhost:5000/threads/{thread_id}/comments'
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.post(url, json={'text': text}, headers=headers)
    return response

st.sidebar.page_link('frontend.py', label='Home')
st.sidebar.page_link('pages/create_thread.py', label='Create Thread')

st.sidebar.button("Logout", on_click=lambda: (st.session_state.clear(), st.switch_page('pages/login.py')))

thread = st.session_state.selected_thread
if thread:
    st.subheader(thread['title'])
    st.write("Comments:")
    new_comment_text = st.text_input("Add a Comment")
    if st.button("Add Comment"):
        if not new_comment_text.strip():
            st.error("Comment cannot be empty.")
        else:
            response = add_comment(thread['id'], new_comment_text)
            if response.status_code == 201:
                st.success("Comment added successfully.")
                fetch_comments(thread['id'])
            else:
                st.error("Failed to add comment.")
    fetch_comments(thread['id'])
    for comment in st.session_state.comments:
        st.write(f"{comment['id']}. {comment['text']}")
