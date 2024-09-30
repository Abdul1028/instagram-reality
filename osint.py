import streamlit as st
import json
import codecs
import os.path
from instagram_private_api import (
    Client, ClientError, ClientLoginError,
    ClientCookieExpiredError, ClientLoginRequiredError,
    __version__ as client_version
)
from helper import InstagramHelper
import streamlit_shadcn_ui as ui



# Helper functions for JSON serialization/deserialization
def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object

def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)

def login(username,password):
    try:
        # Initialize the Instagram API client
        device_id = None
        settings_file = 'settings.json'  # Change this to your desired file name

        if not os.path.isfile(settings_file):
            # Settings file does not exist, perform a new login
            api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, settings_file))
            st.toast("Logged in successfully.")
            st.balloons()
            return api

        else:
            # Reuse cached settings
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            device_id = cached_settings.get('device_id')
            api = Client(username, password, settings=cached_settings)
            st.toast("Logged in from cache.")
            return api

    except ClientLoginError as e:
        st.subheader('Login Failed')
        st.error('Invalid username or password. Please try again.')
    except Exception as e:
        st.subheader('Login Failed')
        st.error(f'Unexpected Exception: {e}')

def main():
    st.title('Instagram Analysis')
    st.sidebar.header('Login')
    username = st.sidebar.text_input('Instagram Username')
    password = st.sidebar.text_input('Instagram Password', type='password')
    with st.sidebar:
        submit_button = ui.button("Login", variant="outline", key="login")

    fetch_tagged = None
    fetch_comments = None
    fetch_followings = None
    fetch_total_likes = None
    fetch_fwersemail = None
    fetch_fwersnumber = None
    fetch_fwingsemail = None
    fetch_fwingsnumber = None
    fetch_people_commented = None
    fetch_people_tagged = None
    fetch_total_comments = None
    fetch_followers = None
    fetch_user_info = None
    fetch_captions = None
    fetch_hashtags = None
    fetch_address = None
    logout = None

    # Ask the user to input the target username
    st.subheader('Enter Target Username')
    target_username = st.text_input('Target Username')


    value = ui.tabs(options=['Profile Insights', 'Post Engagement', 'Connections', 'Interactions'], default_value='Profile Insights',
                    key="categories")


    if value == "Profile Insights":
        cols = st.columns(2)
        with cols[0]:
            st.write("Get information of user ")
        with cols[1]:
            fetch_user_info = ui.button("User Info", variant="outline", key="byf")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get captions of user ")
        with cols[1]:
            fetch_captions = ui.button("Captions", variant="outline", key="byf2")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get hashtags of user ")
        with cols[1]:
            fetch_hashtags = ui.button("Hashtags", variant="outline", key="byf3")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get adresses of user ")
        with cols[1]:
            fetch_address = ui.button("Addresses", variant="outline", key="byf4")


    elif value == "Post Engagement":
        cols =st.columns(2)
        with cols[0]:
            st.write("Target tagged profiles")
        with cols[1]:
            fetch_tagged = ui.button("People Tagged", variant="outline", key="byf")
        cols = st.columns(2)
        with cols[0]:
            st.write("Profiles tagged target")
        with cols[1]:
            fetch_people_tagged = ui.button("People Who Tagged", variant="outline", key="byf2")
        cols = st.columns(2)
        with cols[0]:
            st.write("Comments of target profile ")
        with cols[1]:
            fetch_comments = ui.button("Comments", variant="outline", key="byf3")
        cols = st.columns(2)
        with cols[0]:
                st.write("Profiles that commented on target ")
        with cols[1]:
            fetch_people_commented = ui.button("People Who Commented", variant="outline", key="byf4")



    elif value == "Connections":
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's followers's emails")
        with cols[1]:
            fetch_fwersemail = ui.button("Followers' Emails", variant="outline", key="byf")

        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's follower's numbers")
        with cols[1]:
            fetch_fwersnumber = ui.button("Followers' Numbers", variant="outline", key="byf2")

        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's following's emails")
        with cols[1]:
            fetch_fwingsemail = ui.button("Followings' Emails", variant="outline", key="byf3")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's following's numbers")
        with cols[1]:
            fetch_fwingsnumber = ui.button("Followings' Numbers", variant="outline", key="byf4")

    elif value == "Interactions":
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's followings")
        with cols[1]:
            fetch_followings = ui.button("Followings", variant="outline", key="byf")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's followers")
        with cols[1]:
            fetch_followers = ui.button("Followers", variant="outline", key="byf2")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's total likes")
        with cols[1]:
            fetch_total_likes = ui.button("Total Likes", variant="outline", key="byf3")
        cols = st.columns(2)
        with cols[0]:
            st.write("Get target's total comments")
        with cols[1]:
            fetch_total_comments = ui.button("Total Comments", variant="outline", key="byf4")

    logout = ui.button("Logout", variant="destructive", key="logout")

    if logout:
        os.remove("./settings.json")
        st.toast("Logged out successfully")

    api = None

    if submit_button:
         api = login(username,password)

    with st.sidebar:
        if(api != None):
            st.write(f"Welcome {username} you can use services now")


    if target_username :
        try:
            help = InstagramHelper(target_username, "output", username, password)
            if fetch_user_info:
                help.get_user_info()

            if fetch_captions:
                help.get_captions()

            if fetch_tagged:
                help.get_people_tagged_by_user()

            if fetch_comments:
                help.get_total_comments()
                help.get_comments()
                help.get_comment_data()
                help.get_people_who_commented()

            if fetch_hashtags:
                help.get_hashtags()

            if fetch_address:
                help.get_addrs()

            if fetch_followings:
                help.get_followings()

            if fetch_total_likes:
                help.get_total_likes()

            if fetch_fwersemail:
                help.get_fwersemail()

            if fetch_fwersnumber:
                help.get_fwersnumber()

            if fetch_fwingsemail:
                help.get_fwingsemail()

            if fetch_fwingsnumber:
                help.get_fwingsnumber()

            if fetch_people_commented:
                help.get_people_who_commented()

            if fetch_people_tagged:
                help.get_people_who_tagged()

            if fetch_total_comments:
                help.get_total_comments()

            if fetch_followers:
                help.get_followers()

        except ClientError as e:
            st.subheader('Error')
            st.error(f'Client Error: {e}')
            os.remove("./settings.json")
            st.toast("Sorry login again we cleared the session")
        except Exception as e:
            st.warning("Please login before using services")
    else:
        st.toast("Please enter username first ")






if __name__ == '__main__':
    main()