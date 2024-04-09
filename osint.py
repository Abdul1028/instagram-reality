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
            return api
        else:
            # Reuse cached settings
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            device_id = cached_settings.get('device_id')
            api = Client(username, password, settings=cached_settings)
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
    submit_button = st.sidebar.button('Login')

    col1, col2, col3, col4 = st.columns(4)

    # First button
    fetch_followers = col1.button("Fetch Followers")

    # Second button
    get_followers_button = col2.button("Fetch Followings")

    # Third button
    get_comments_button = col3.button("Fetch Comments")

    # Fourth button
    address = col4.button("Fetch Address")
    # Ask the user to input the target username
    st.subheader('Enter Target Username')
    target_username = st.text_input('Target Username')


    if submit_button:
         login(username,password)


    if target_username :
        try:
            help = InstagramHelper(target_username, "output")

            help.setTarget(target_username)
            help.get_user_info()
            help.get_captions()
            help.get_people_tagged_by_user()
            # help.get_comments()
            help.get_hashtags()
            help.get_addrs()
            # help.get_comment_data()
            help.get_addrs()


            # help.get_followers()
            # help.get_followings()
            # help.get_fwersemail()
            # help.get_fwersnumber()
            # help.get_fwingsemail()
            # help.get_fwingsnumber()
            help.get_people_who_commented()
            help.get_people_who_tagged()
            help.get_total_comments()
            help.get_total_likes()

        except ClientError as e:
            st.subheader('Error')
            st.error(f'Client Error: {e}')



    if fetch_followers:
        print("clicked")
        my_ds = help.getmy_followings("21889505654")
        # Display the DataFrame using Streamlit
        st.table(my_ds)

    if address:
        help.get_addrs()

    if get_followers_button:
        st.success(getuser())
        st.write("heyy")

    if get_comments_button:
        pass


if __name__ == '__main__':
    main()
