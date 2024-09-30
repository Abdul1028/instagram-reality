
import streamlit as st
import json
import codecs
import os.path
from getpass import getuser

import logging
import datetime
from instagram_private_api import (
    Client, ClientError, ClientLoginError,
    ClientCookieExpiredError, ClientLoginRequiredError,
    __version__ as client_version
)

from helper import InstagramHelper
from getpass import getuser



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
        st.text('SAVED: {0!s}'.format(new_settings_file))

#
# def login(username,password):
#     try:
#         # Initialize the Instagram API client
#         device_id = None
#         settings_file = 'settings.json'  # Change this to your desired file name
#
#         if not os.path.isfile(settings_file):
#             # Settings file does not exist, perform a new login
#             api = Client(
#                 username, password,
#                 on_login=lambda x: onlogin_callback(x, settings_file))
#             return api
#         else:
#             # Reuse cached settings
#             with open(settings_file) as file_data:
#                 cached_settings = json.load(file_data, object_hook=from_json)
#             device_id = cached_settings.get('device_id')
#             api = Client(username, password, settings=cached_settings)
#             return api
#
#     except ClientLoginError as e:
#         st.subheader('Login Failed')
#         st.error('Invalid username or password. Please try again.')
#     except Exception as e:
#         st.subheader('Login Failed')
#         st.error(f'Unexpected Exception: {e}')

def main():
    st.title('Instagram Analysis')
    st.sidebar.header('Login')
    username = st.sidebar.text_input('Instagram Username')
    password = st.sidebar.text_input('Instagram Password', type='password')
    submit_button = st.sidebar.button('Login')

    col1, col2, col3, col4 = st.columns(4)

    # Buttons for different operations
    fetch_followers = col1.button("Fetch Followers")
    fetch_captions = col2.button("Fetch Captions")
    fetch_tagged = col3.button("Fetch People Tagged")
    fetch_comments = col4.button("Fetch Comments")

    fetch_hashtags = col1.button("Fetch Hashtags")
    fetch_address = col2.button("Fetch Address")
    fetch_followings = col3.button("Fetch Followings")
    fetch_total_likes = col4.button("Fetch Total Likes")

    # Ask the user to input the target username
    st.subheader('Enter Target Username')
    target_username = st.text_input('Target Username')
    if submit_button:
        helper = InstagramHelper()
        helper.login(username, password)

    if target_username:
        help = InstagramHelper(target_username, "output")
        help.setTarget(target_username)
        st.toast("Target set succesfully!! perform operations")

        # Only fetch data for the button that was clicked
        if fetch_followers:
            st.info("Fetching followers...")
            try:
                help.get_followers()
                st.success("Followers fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching followers: {e}')

        if fetch_captions:
            st.info("Fetching captions...")
            try:
                help.get_captions()
                st.success("Captions fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching captions: {e}')

        if fetch_tagged:
            st.info("Fetching people tagged...")
            try:
                help.get_people_tagged_by_user()
                st.success("People tagged fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching people tagged: {e}')

        if fetch_comments:
            st.info("Fetching comments...")
            try:
                help.get_comments()
                st.success("Comments fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching comments: {e}')

        if fetch_hashtags:
            st.info("Fetching hashtags...")
            try:
                help.get_hashtags()
                st.success("Hashtags fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching hashtags: {e}')

        if fetch_address:
            st.info("Fetching address...")
            try:
                help.get_addrs()
                st.success("Address fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching address: {e}')

        if fetch_followings:
            st.info("Fetching followings...")
            try:
                help.get_followings()
                st.success("Followings fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching followings: {e}')

        if fetch_total_likes:
            st.info("Fetching total likes...")
            try:
                help.get_total_likes()
                st.success("Total likes fetched successfully!")
            except ClientError as e:
                st.error(f'Error fetching total likes: {e}')


if __name__ == '__main__':
    main()
