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
    # username = st.sidebar.text_input('Instagram Username')
    # password = st.sidebar.text_input('Instagram Password', type='password')
    # submit_button = st.sidebar.button('Login')

    with st.sidebar:
        with ui.card(key="card1"):
            ui.element("span", children=["Email"], className="text-gray-400 text-sm font-medium m-1", key="label1")
            ui.element("input", key="email_input", placeholder="Your email")

            ui.element("span", children=["Password"], className="text-gray-400 text-sm font-medium m-1", key="label2")
            ui.element("input", key="password_input", placeholder="Enter your password")
            ui.element("button", text="Login", key="button", className="m-1")

    # Define columns
    col1, col2, col3, col4 = st.columns(4)

    # First row of buttons
    fetch_user_info = col1.button("Get User Info")
    fetch_captions = col2.button("Get Captions")
    fetch_tagged = col3.button("Get People Tagged")
    fetch_comments = col4.button("Get Comments")

    # Second row of buttons
    fetch_hashtags = col1.button("Get Hashtags")
    fetch_address = col2.button("Get Addresses")
    fetch_followings = col3.button("Get Followings")
    fetch_total_likes = col4.button("Get Total Likes")

    # Third row of buttons
    fetch_fwersemail = col1.button("Get Followers' Emails")
    fetch_fwersnumber = col2.button("Get Followers' Numbers")
    fetch_fwingsemail = col3.button("Get Followings' Emails")
    fetch_fwingsnumber = col4.button("Get Followings' Numbers")

    # Fourth row of buttons
    fetch_people_commented = col1.button("Get People Who Commented")
    fetch_people_tagged = col2.button("Get People Who Tagged")
    fetch_total_comments = col3.button("Get Total Comments")
    fetch_followers = col4.button("Get Followers")

    # with ui.card(key="card13"):
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #     ui.element("button", text="Login", key="button", className="m-1")
    #
    # value = ui.tabs(options=['Profile Insights', 'Post Engagement', 'Connections', 'Interactions'], default_value='Profile Insights',
    #                 key="categories")
    #
    # with ui.card(key="image"):
    #     if value == "Profile Insights":
    #         ui.element("text", children=["Get Profile Insights of user seamlessly"], className="text-gray-400 text-sm font-medium m-1", key="profile")
    #         ui.element("button", text="Login", key="buttonf55", className="m-1")
    #         ui.element("button", text="Login", key="buttonih7", className="m-1")
    #         ui.element("button", text="Login", key="button876i", className="m-1")
    #
    #
    #     elif value == "Graphic Walker":
    #         ui.element("img", src="https://pub-8e7aa5bf51e049199c78b4bc744533f8.r2.dev/graphic-walker-banner.png",
    #                    className="w-full")
    #         ui.element("link_button", text=value + " Github", url="https://github.com/Kanaries/graphic-walker",
    #                    className="mt-2", key="btn2")
    #     elif value == "GWalkR":
    #         ui.element("img", src="https://pub-8e7aa5bf51e049199c78b4bc744533f8.r2.dev/gwalkr-banner.png",
    #                    className="w-full")
    #         ui.element("link_button", text=value + " Github", url="https://github.com/Kanaries/gwalkr",
    #                    className="mt-2", key="btn2")
    #     elif value == "RATH":
    #         ui.element("img", src="https://pub-8e7aa5bf51e049199c78b4bc744533f8.r2.dev/rath-painter.png",
    #                    className="w-full")
    #         ui.element("link_button", text=value + " Github", url="https://github.com/Kanaries/Rath", className="mt-2",
    #                    key="btn2")
    #     st.write("Selected:", value)
    #
    # st.write(ui.tabs)





    # Ask the user to input the target username
    st.subheader('Enter Target Username')
    target_username = st.text_input('Target Username')

    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card11")
    with cols[1]:
        ui.metric_card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card2")
    with cols[2]:
        ui.metric_card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card3")



    # if submit_button:
    #      login(username,password)


    if target_username :
        try:
            help = InstagramHelper(target_username, "output","abdul.ipa","Instagram@1028")


            # Now handle button clicks and invoke corresponding functions
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






            # help.get_user_info()
            # help.get_captions()
            # help.get_people_tagged_by_user()
            # help.get_comments()
            # help.get_hashtags()
            # help.get_addrs()
            # help.get_comment_data()
            # help.get_addrs()
            # help.get_followers()
            # help.get_followings()
            # help.get_fwersemail()
            # help.get_fwersnumber()
            # help.get_fwingsemail()
            # help.get_fwingsnumber()
            # help.get_people_who_commented()
            # help.get_people_who_tagged()
            # help.get_total_comments()
            # help.get_total_likes()

        except ClientError as e:
            st.subheader('Error')
            st.error(f'Client Error: {e}')





if __name__ == '__main__':
    main()