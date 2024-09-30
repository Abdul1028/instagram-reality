import base64
import os
import re
import requests
import uuid
from datetime import datetime
from firebase_admin import credentials, firestore, auth
import firebase_admin
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import json
from utils.snowchat_ui import StreamlitUICallbackHandler, message_func
from backend import preprocessor
from backend import helper
import nltk
import streamlit_shadcn_ui as ui
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('punkt_tab')

# Layout
st.set_page_config(
    page_title="Instagram Chat Analyzer",
    layout="wide",
    initial_sidebar_state="expanded")

import streamlit as st
from helper import InstagramHelper

def display_chat_message(message):
    st.markdown(f'<div class="chat-message">{message}</div>', unsafe_allow_html=True)


chat_history = []

# custom css for button and webview
st.markdown("""
    <style>

    .big-font {
    font-size:80px !important;
}

     .message-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        max-width: 60%;
        align-self: flex-end;

    }
    .other-message {
        background-color: #F1F0F0;
        padding: 10px;
        border-radius: 10px;
        max-width: 60%;
        align-self:flex-start;

    }

    .notification-message {
        background-color: #F1F0F0;
        padding: 10px;
        border-radius: 10px;
        max-width: 60%;
        align-self:center;

    }

    .sender {
        font-size: 12px;
        color: red;
    }
    .time {
        font-size: 10px;
        color: black;
        text-align: right;

    }

       .chat-message {
        background-color: #DCF8C6;
        color: #000000;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        max-width: 70%;
    }
    .chat-message:nth-child(odd) {
        align-self: flex-start;
        text-align: left;
    }
    .chat-message:nth-child(even) {
        align-self: flex-end;
        text-align: right;
        background-color: #DCF8C6;
        color: #000000;
    }



    </style>
""", unsafe_allow_html=True)

github_link = ""
file_path = 'sample_whatsapp_export.txt'


@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f"""<img style = "width: 100%" src="data:image/svg+xml;base64,{b64}"/>"""
    st.write(html, unsafe_allow_html=True)


def download_button(object_to_download, download_filename, button_text):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    b64 = base64.b64encode(object_to_download.encode()).decode()
    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:text/plain;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


def display_chat_message(sender, message, sentiment):
    st.markdown(
        f"<div class='chat-message'>Sender: {sender}<br>Message: {message}<br>Sentiment: {sentiment}</div>",
        unsafe_allow_html=True
    )


# Check if Firebase app has already been initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("firebase-metadata/wit-reality-firebase-data.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

globalcredits = 0
globaluid = ""
st.session_state.isLoggedIn = "false"


# Signup page
def signup():
    st.header("Signup")

    email = st.text_input("Email")
    nickname = st.text_input("Name")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if email and password:
            try:
                user = auth.create_user(email=email, password=password)
                print(user)
                st.success("User created successfully")
                # # Check if email is already registered
                # user_ref = db.collection("users").document(email)
                # if user_ref.get().exists:
                #     st.error("User already exists. Please use a different email.")
                # else:
                #     # Store user credentials in Firestore
                #     user_ref.set({"email": email, "password": password,"nickname":nickname})
                #     st.success("User signed up successfully.")
            except Exception as e:
                st.error(f"Signup failed: {e}")


firebase_api_key = "AIzaSyDqFTgBTs10Qx3Km2eVWASTum-1Eoy64xo"


def signin_with_password(email, password):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    api_key = "AIzaSyDqFTgBTs10Qx3Km2eVWASTum-1Eoy64xo"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    params = {"key": api_key}

    try:
        response = requests.post(url, params=params, json=payload)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        data = response.json()
        if "idToken" in data:
            # Authentication successful, return the secure token
            return data["idToken"]
        else:
            # Authentication failed, handle error
            return None
    except requests.exceptions.RequestException as e:
        # Handle request errors
        print("Error:", e)
        return None


# Login page
def login():
    st.header("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        if email and password:
            try:
                # # Retrieve user credentials from Firestore
                # user_ref = db.collection("users").document(email)
                # user_data = user_ref.get().to_dict()
                # if user_data and user_data.get("password") == password:
                #     st.session_state.user = {"nickname": user_data.get("nickname")}  # Set session
                #
                #     st.success("Login successful.")
                # else:
                #     st.error("Invalid email or password.")
                token = signin_with_password(email, password)
                if token:
                    st.success("successfully signed in")
                    decoded_token = auth.verify_id_token(token)
                    uid = decoded_token['uid']
                    st.session_state.user = uid
                    st.session_state.uid = uid
                    globaluid = uid

                else:
                    st.error("Authentication failed.")
            except Exception as e:
                st.error(f"Login failed: {e}")


def add_credits_to_user(uid, credits):
    # Get the Firestore client
    db = firestore.client()
    try:
        # Create a reference to the user's document
        user_ref = db.collection('users').document(st.session_state.uid)
        # Update the user's document with credits
        user_ref.set({
            'credits': credits
        }, merge=True)  # merge=True ensures that existing data is not overwritten

        # You can add additional data here in the future
        # For example, randomly generated data
        # user_ref.set({
        #     'random_data': {
        #         'field1': value1,
        #         'field2': value2,
        #         ...
        #     }
        # }, merge=True)

        print(f"Credits added successfully for user with UID: {uid}")
    except Exception as e:
        print(f"Failed to add credits: {e}")


# add credits
# add_credits_to_user(globaluid,5000)
# st.success(f"succesfully added credits to: {globaluid}")


def dashboard():
    st.header("Dashboard")

    # Check if user is logged in
    if "user" not in st.session_state:
        st.error("Please login to access the dashboard.")
        return

    user_name = st.session_state.user["nickname"]

    st.write(f"Hello, {user_name}!")

    # Text area for posting
    post_text = st.text_area("Write your post here:")
    if st.button("Post"):
        if post_text:
            try:
                # Get user's document reference
                user_ref = db.collection("users").document(user_name)

                # Add post to user's document
                user_ref.update({
                    "post": firestore.ArrayUnion([post_text])
                })
                st.success("Post added successfully.")
            except Exception as e:
                st.error(f"Failed to add post: {e}")
        else:
            st.warning("Please enter some text to post.")


# Options Menu
with st.sidebar:
    selected = option_menu('Chat Analyzer', ["Intro", 'Search', 'Osintgram', 'Login'],
                           icons=['play-btn', 'search', 'info-circle', 'gear'], menu_icon='intersect', default_index=0)
    lottie = load_lottiefile("lottie_jsons/instagram-sidebar.json")
    st_lottie(lottie, key='loc')

if selected == "Intro":
    c1, c2 = st.columns((2, 1))
    c1.title("""Instagram Chat Analyser""")
    c1.subheader("""Discover trends, analyse your chat history and judge your friends!""")
    c1.markdown(
        f"Dont worry, we wont peek, we're not about that, in fact, you can check the code in here: [link]({github_link})")

    uploaded_file = c1.file_uploader(label="""Upload your Whatsapp chat, don't worry, we won't peek""",
                                     key="notniq", type=["json"])

    with open(file_path, 'r') as f:
        dl_button = download_button(f.read(), 'sample_file.txt', 'Try it out with my sample file!')
        c1.markdown(dl_button, unsafe_allow_html=True)

    with c2:
        lottie = load_lottiefile("lottie_jsons/chat_icon.json")
        st_lottie(lottie, key='loc2')

    if uploaded_file is not None:
        df = preprocessor.process_file(uploaded_file)
        st.toast("File processed successfully!")
        print("YOUR DATA FRAME IS: ", df)
        st.write(df)
        # Assuming 'date' is a datetime column in your DataFrame

        start_date = df['date'].min()
        end_date = df.iloc[-1]['date']

        # Convert datetime to timestamp for slider
        start_date_timestamp = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_timestamp = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

        s_timestamp = int(start_date_timestamp.timestamp())
        e_timestamp = int(end_date_timestamp.timestamp())



        # Convert timestamp back to datetime
        start_datee = datetime.utcfromtimestamp(s_timestamp).strftime('%Y-%m-%d')
        end_datee = datetime.utcfromtimestamp(e_timestamp).strftime('%Y-%m-%d')

        # Convert to datetime objects for showing them in slider
        date_object1 = datetime.strptime(start_datee, "%Y-%m-%d")
        date_object2 = datetime.strptime(end_datee, "%Y-%m-%d")

        # Create a date slider
        selected_date_range_timestamp = st.slider(
            'Select date',
            min_value=start_date_timestamp,
            value=(date_object1, date_object2),
            max_value=end_date_timestamp,
            format="YYYY-MM-DD",  # Display format
        )

        # Display the selected date range

        selected_start_date = selected_date_range_timestamp[0].strftime("%Y-%m-%d")
        selected_end_date = selected_date_range_timestamp[1].strftime("%Y-%m-%d")
        st.write(
            f'Start Date: {selected_date_range_timestamp[0].strftime("%Y-%m-%d")} & End Date: {selected_date_range_timestamp[1].strftime("%Y-%m-%d")}')

        # fetch unique users
        user_list = df['user'].unique().tolist()
        # user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        c3, c4, c5 = st.columns((1, 2, 1))

        with c3:
            selected_user = st.selectbox("Select Participants for analysis", user_list, )
        with c4:
            selected_participants = st.multiselect("Select Participants to view there conversation", user_list,
                                                   key="new2")
        with c5:
            selected_participant_for_displaying_messsage = st.selectbox("select participant for viewing: ",
                                                                        selected_participants)

        placeholder = st.empty()

        if selected_user:
            with placeholder.container():
                # Stats Area
                num_messages, words, num_media_messages, num_links , num_reactions= helper.fetch_stats(selected_user, df)
                st.title("Top Statistics")
                cols = st.columns(4)

                with cols[0]:
                    ui.metric_card(title="Messages", content=num_messages, description="Total messages done",
                                   key="card1")
                with cols[1]:
                    ui.metric_card(title="Words", content=words, description="Total words in conversation",
                                   key="card2")

                with cols[2]:
                    ui.metric_card(title="Media shared", content=int(num_media_messages), description="Total media shared in conversation",
                                   key="card6")

                with cols[3]:
                    ui.metric_card(title="Reactions", content=int(num_reactions), description="Total reactions in conversation",
                                   key="card90")



                # working but shows a lot of graphs
                # figures = helper.calculate_monthly_sentiment_trends(selected_user, df)
                # # Display the figures in Streamlit
                # for fig in figures:
                #     st.plotly_chart(fig)

                # monthly timeline
                st.title("Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                # fig, ax = plt.subplots()
                # ax.plot(timeline['time'], timeline['message'], color='green')
                # plt.xticks(rotation='vertical')
                # st.pyplot(fig)

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(x=timeline['time'], y=timeline['message'], mode='lines', marker=dict(color='green')))
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

                # daily timeline
                st.title("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                # fig, ax = plt.subplots()
                # ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                # plt.xticks(rotation='vertical')
                # st.pyplot(fig)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_timeline['only_date'], y=daily_timeline['message'], mode='lines',
                                         marker=dict(color='black')))
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

                # activity map
                st.title('Activity Map')

                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig = px.bar(busy_day, x=busy_day.index, y=busy_day.values, color=busy_day.values,
                             color_continuous_scale='Viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig = px.bar(busy_month, x=busy_month.index, y=busy_month.values, color=busy_month.values,
                             color_continuous_scale='Viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)

                # st.title("Weekly Activity Map")
                # user_heatmap = helper.activity_heatmap(selected_user, df)
                # fig, ax = plt.subplots()
                # ax = sns.heatmap(user_heatmap)
                # st.pyplot(fig)

                # heatmap_data = helper.activity_heatmap(selected_user, df)
                #
                # # Create a Plotly heatmap
                # fig = go.Figure(data=go.Heatmap(
                #     z=heatmap_data.values,
                #     x=heatmap_data.columns,
                #     y=heatmap_data.index,
                #     colorscale='Viridis'))
                #
                # fig.update_layout(
                #     title="Activity Heatmap",
                #     xaxis_title="Period",
                #     yaxis_title="Day of Week"
                # )
                #
                # # Display the Plotly heatmap
                # st.plotly_chart(fig)

                # finding the busiest users in the group(Group level)
                if selected_user == 'Overall':
                    st.title('Most Busy Users')
                    x, new_df = helper.most_busy_users(df)
                    # fig, ax = plt.subplots()

                    # Create a bar plot using Plotly Express
                    fig = px.bar(x=x.index, y=x.values, labels={'x': 'User', 'y': 'Count'})
                    fig.update_layout(title="Most Busy Users")
                    fig.update_xaxes(title_text='User', tickangle=-45)
                    fig.update_yaxes(title_text='Count')
                    st.plotly_chart(fig)

                    st.dataframe(new_df)

                st.title("Wordcloud")

                # df_wc = helper.create_wordcloud(selected_user, df)
                # fig, ax = plt.subplots()
                # ax.imshow(df_wc)
                # plt.axis("off")
                # st.pyplot(fig)

                wordcloud_fig = helper.create_plotly_wordcloud(selected_user, df)
                st.plotly_chart(wordcloud_fig)

                # most common words
                most_common_df = helper.most_common_words(selected_user, df)

                # fig, ax = plt.subplots()
                #
                # ax.barh(most_common_df[0], most_common_df[1])

                st.title('Most common words')
                # st.pyplot(fig)

                # Create a bar plot using Plotly Express
                fig = px.bar(most_common_df, x='Word', y='Frequency', labels={'Word': 'Word', 'Frequency': 'Frequency'})
                fig.update_layout(title="Most Common Words")
                fig.update_xaxes(title_text='Word', tickangle=-45)
                fig.update_yaxes(title_text='Frequency')
                st.plotly_chart(fig)

                # emoji analysis
                emoji_df = helper.emoji_helper(selected_user, df)
                st.title("Emoji Analysis")
                fig = px.pie(emoji_df.head(8), labels={'0': 'Emoji', '1': 'Frequency'}, values=1, names=0,
                             title="Emoji Distribution")
                st.plotly_chart(fig)

                helper.show_average_reply_time(df)

                ##Start of sentimental analysis
                # Perform sentiment analysis on the selected messages
                positive_fig, negative_fig = helper.analyze_and_plot_sentiment(selected_user, df)
                # Display the positive and negative sentiment figures
                st.plotly_chart(positive_fig)
                st.plotly_chart(negative_fig)

                user_sentiment_percentages, most_positive, least_positive = helper.calculate_sentiment_percentage(
                    selected_user, df)
                for user, percentages in user_sentiment_percentages.items():
                    st.write(f"User: {user}")
                    st.write(f"Positivity Percentage: ", percentages[0])
                    st.write(f"Negativity Percentage: ", percentages[1])
                    st.write("---")  # Separator between users

                st.write("Most positive User: ", most_positive)
                st.write("Least positive: ", least_positive)

                f = helper.calculate_monthly_sentiment_trend(df)
                st.plotly_chart(f)

                ###End of sentimental analysis
                st.title("Busiest Hours")
                helper.busiest_hours_analysis(df)

                c_11, c_12 = st.columns((1, 1))
                fig1, most_messages_winner = helper.message_count_aggregated_graph(df)
                c_11.subheader("Who talks the most?")
                c_11.markdown(
                    f"How many messages has each one sent in your convo? apparently **{most_messages_winner}** did")
                with c_11:
                    st.plotly_chart(fig1)

                # # Show who starts the conversations
                # c_11, c_12 = st.columns((1, 1))
                # fig1,most_messages_winner= helper.conversation_starter_graph(df)
                # c_11.subheader("Who's starts the conversations?")
                # c_11.markdown(f"This clearly shows that **{most_messages_winner}** started all the convos")
                # with c_11:
                #     st.plotly_chart(fig1)

                # fig = helper.conversation_size_aggregated_graph(df)
                # st.subheader("How long are your conversations?")
                # st.markdown(
                #     f"This is how many messages (on average) your conversations had, the more of them there are, the more messages you guys exchanged everytime one of you started the convo!")
                # st.plotly_chart(fig)

                c1, c2 = st.columns(2)

                helper.top_emojis_used(selected_user, df)

                with c1:
                    st.dataframe(emoji_df)

                with c2:
                    helper.message_count_by_month(selected_user, df)

                helper.greeting_farewell_analysis(selected_user, df)

                # Call functions to plot graphs
                st.write('### Top Users')
                st.plotly_chart(helper.plot_top_users(df))

                st.write('### Hashtag and Mention Frequency')
                hashtag_fig, mention_fig = helper.plot_hashtag_mention_frequency(df)
                st.plotly_chart(hashtag_fig)
                st.plotly_chart(mention_fig)

                st.write('### Media Type Distribution')
                st.plotly_chart(helper.plot_media_type_distribution(df))

                st.write('### Word Frequency by User')
                st.plotly_chart(helper.plot_word_frequency_by_user(df))

                # Call the functions to retrieve the information
                most_stories_user, most_stories_count = helper.most_stories_user(df)
                most_reels_user, most_reels_count = helper.most_reels_user(df)
                most_posts_user, most_posts_count = helper.most_posts_user(df)

                # Call the function to create the bar chart
                helper.create_plot_for_attachment_distribution({
                    'most_reels_user': most_reels_user,
                    'most_reels_count': most_reels_count,
                    'most_posts_user': most_posts_user,
                    'most_posts_count': most_posts_count,
                    'most_stories_user': most_stories_user,
                    'most_stories_count': most_stories_count
                })

                # # Call the function to retrieve the information
                # most_story_replies_user, most_story_replies_count = helper.most_story_replies_user(df)
                #
                # st.write("User who has replied to stories the most:", most_story_replies_user)
                # st.write("Number of story replies:", most_story_replies_count)
                #
                # # Call the function to retrieve the story reply messages
                # story_reply_messages = helper.get_story_replies(df)
                #
                # if story_reply_messages:
                #     st.write("Story reply messages:")
                #     for message in story_reply_messages:
                #         st.write(message)
                # else:
                #     st.write("No story replies found")

                # Call the function to categorize messages as story mentions or story replies and keep track of counts
                helper.categorize_story_mentions_and_replies(df)

                # max_user, max_time = helper.longest_reply_user(df)
                #
                # st.write(max_user, " takes the most time to reply wiz ", max_time)
                # user, time, msg, reply = helper.longest_reply_user2(df)
                # st.write(f"User with longest reply time: {user}")
                # st.write(f"Longest reply time (minutes): {time}")
                # st.write(f"Message to which the user replied the most late: {msg}")
                # st.write(f"Replied message: {reply}")

                # user, time, msg, reply = helper.top5_late_replies(df)
                # st.write(f"User with longest reply time: {user}")
                # st.write(f"Longest reply time (minutes): {time}")
                # st.write(f"Message to which the user replied the most late: {msg}")
                # st.write(f"Replied message: {reply}")

                # user, time, msg, reply = helper.top_texts_late_replies(df)
                # st.write(f"User with longest reply time: {user}")
                # st.write(f"Longest reply time (minutes): {time}")
                # st.write(f"Message to which the user replied the most late: {msg}")
                # st.write(f"Replied message: {reply}")

                helper.message_length_analysis(selected_user, df)

                fig,user,count = helper.visualize_attachments_by_user_plotly(df)
                st.plotly_chart(fig)

                st.write(f"{user} has sent the most attachments wiz  {count} total attachments")


                max_idle_date, max_idle_time = helper.most_idle_date_time(df)
                st.write(f"The date(s) when the group was idle for the most time:")
                st.write(f"Date: {max_idle_date}")

                median_delay_per_user = helper.median_delay_between_conversations(selected_user, df)
                if median_delay_per_user is not None:
                    st.write(f"Median Reply Delay for {selected_user}: {median_delay_per_user:.2f} minutes")

                # double_text_count = helper.double_text_counts(selected_user, df)
                # st.write(double_text_count)
                #
                # counts = helper.response_activity(selected_user, df)
                # st.write(counts)

        if selected_participant_for_displaying_messsage:
            placeholder.empty()
            st.header(f"You are viewing as {selected_participant_for_displaying_messsage}")

            # Convert the 'date' column to pandas datetime object
            df['date'] = pd.to_datetime(df['date'])

            # # Sort the DataFrame by 'date' and 'user'
            # df = df.sort_values(by=['date', 'user'])

            # Iterate through messages and display them in a chat-like format
            for _, group in df[df['user'].isin(selected_participants)].iterrows():
                sender = group['user']
                message = group['message']
                time = group['date']
                sentiment = helper.analyze_sentiment(message)  # assuming you have a helper function

                # Apply custom CSS class based on the sender
                if sender == selected_participant_for_displaying_messsage:
                    st.markdown(
                        f'<div class="message-container"><div class="user-message">{message}</div>'
                        f'<div class="time"  >{time} </div></div>',
                        unsafe_allow_html=True
                    )
                elif sender == "group_notification":
                    st.markdown(
                        f'<div class="message-container">'
                        f'<div class="notification-message">{message}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="message-container"><div class="sender">{sender}</div>'
                        f'<div class="other-message">{message}</div><div class="time"  style="text-align:left " >{time}</div></div>'
                        ,
                        unsafe_allow_html=True
                    )

            selected_participant_for_sentiments = placeholder.multiselect(f"Show Messages and Sentiments", user_list)

            if selected_participant_for_sentiments:
                st.header(f"Message sentiments of {selected_participant_for_sentiments}")
                filtered_df = df[df['user'].isin(selected_participant_for_sentiments)]

                for _, group in filtered_df.iterrows():
                    sender = group['user']
                    message = group['message']
                    sentiment = helper.analyze_sentiment(message)  # assuming you have a helper function
                    display_chat_message(sender, message, sentiment)

if selected == "Search":

    if "user" in st.session_state:
        uploaded_file = st.file_uploader(label="""Upload your Whatsapp chat, don't worry, we won't peek""",
                                         key="notniq")
        if uploaded_file is not None:
            if uploaded_file is not None:
                df = preprocessor.process_file(uploaded_file)
                st.toast("File processed successfully!")
                print("YOUR DATA FRAME IS: ", df)
                st.write(df)
            lottie = load_lottiefile("lottie_jsons/chatbot-icon.json")
            # with st.sidebar:
            #     st_lottie(lottie, key='loc2')

            st.write("Search page")
            # question = st.text_input("Enter your question: ")
            # # ans = helper.run_pandas_ai(df, question)

            st.caption("Talk your way through data")
            model = st.radio(
                "",
                options=["GPT-3.5 - OpenAI", "Gemini 1.5 - Openrouter", "Mistral 8x7B - Groq"],
                index=0,
                horizontal=True,
            )
            st.session_state["model"] = model

            if "toast_shown" not in st.session_state:
                st.session_state["toast_shown"] = False

            # Show the toast only if it hasn't been shown before
            if not st.session_state["toast_shown"]:
                st.toast("The snowflake data retrieval is disabled for now.", icon="👋")
                st.session_state["toast_shown"] = True

            if st.session_state["model"] == "👑 Mistral 8x7B - Groq":
                st.warning("This is highly rate-limited. Please use it sparingly", icon="⚠️")

            INITIAL_MESSAGE = [
                {"role": "user", "content": "Hi!"},
                {
                    "role": "assistant",
                    "content": "Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍",
                },
            ]

            # Add a reset button
            if st.sidebar.button("Reset Chat"):
                st.session_state["messages"] = INITIAL_MESSAGE
                st.session_state["history"] = []

            st.sidebar.markdown(
                "**Note:** <span style='color:red'>The snowflake data retrieval is disabled for now.</span>",
                unsafe_allow_html=True,
            )

            # Initialize the chat messages history
            if "messages" not in st.session_state.keys():
                st.session_state["messages"] = INITIAL_MESSAGE

            if "history" not in st.session_state:
                st.session_state["history"] = []

            if "model" not in st.session_state:
                st.session_state["model"] = model

            # Prompt for user input and save
            if prompt := st.chat_input():
                st.session_state.messages.append({"role": "user", "content": prompt})

            for message in st.session_state.messages:
                message_func(
                    message["content"],
                    True if message["role"] == "user" else False,
                    True if message["role"] == "data" else False,
                    model,
                )

            callback_handler = StreamlitUICallbackHandler(model)


            def append_chat_history(question, answer):
                st.session_state["history"].append((question, answer))


            def append_message(content, role="assistant"):
                """Appends a message to the session state messages."""
                if content.strip():
                    st.session_state.messages.append({"role": role, "content": content})


            if (
                    "messages" in st.session_state
                    and st.session_state["messages"][-1]["role"] != "assistant"
            ):
                user_input_content = st.session_state["messages"][-1]["content"]

                if isinstance(user_input_content, str):
                    callback_handler.start_loading_message()

                    agent = helper.get_gpt_response()
                    result = agent.invoke(user_input_content)
                    append_message(result["output"])
                    st.experimental_rerun()

    else:
        st.warning("Please login to access this feature")

import osint
if selected == "Osintgram":
    if "user" in st.session_state:
        ## OSINT.PY (WHOLE STREAMLIT APP)
        osint.main()
    else:
        st.warning("Please login to access this feature")

    # Kali like CLI UI made but not working so jusg load the osint component //sole py file (streamlit app)

    # target_username = st.text_input("Enter username")
    # if target_username :
    #     try:
    #         help = InstagramHelper(target_username, "output")
    #     except Exception as e:
    #         st.error(e)
    #
    # def execute_command(command):
    #     username = "example_username"  # You can replace this with actual username input from the user
    #     if command.lower() == "user_info":
    #         data = help.get_user_info()
    #     elif command.lower() == "captions":
    #         data = help.get_captions()
    #     elif command.lower() == "people_tagged":
    #         data = help.get_people_tagged_by_user()
    #     elif command.lower() == "comments":
    #         data = help.get_comments()
    #     elif command.lower() == "hashtags":
    #         data = help.get_hashtags()
    #     elif command.lower() == "addresses":
    #         data = help.get_addrs()
    #     elif command.lower() == "comment_data":
    #         data = help.get_comment_data()
    #     elif command.lower() == "followers":
    #         data = help.get_followers()
    #     elif command.lower() == "followings":
    #         data = help.get_followings()
    #     elif command.lower() == "follower_email":
    #         data = help.get_fwersemail()
    #     elif command.lower() == "follower_number":
    #         data = help.get_fwersnumber()
    #     elif command.lower() == "following_email":
    #         data = help.get_fwingsemail()
    #     elif command.lower() == "following_number":
    #         data = help.get_fwingsnumber()
    #     elif command.lower() == "people_who_commented":
    #         data = help.get_people_who_commented()
    #     elif command.lower() == "people_who_tagged":
    #         data = help.get_people_who_tagged()
    #     elif command.lower() == "total_comments":
    #         data = help.get_total_comments()
    #     elif command.lower() == "total_likes":
    #         data = help.get_total_likes()
    #     else:
    #         data = f"Error: Command '{command}' not recognized."
    #
    #     return data
    #
    # st.title("Instagram Terminal")
    #
    # # Function to initialize session state
    # def init_session_state():
    #     if 'text_value' not in st.session_state:
    #         st.session_state.text_value = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n$wit-reality/ig-service \n"
    #
    # # Initialize session state
    # init_session_state()
    #
    # with stylable_container(
    #         key="green_button",
    #         css_styles="""
    #         textarea {
    #             background-color: black;
    #         color: lime;
    #         font-family: monospace;
    #         padding: 10px;
    #         border-radius: 5px;
    #         overflow-y: scroll;
    #         height: 300px;
    #         }
    #         """,
    # ):
    #     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     a = st.text_area("Enter command:", value=st.session_state.text_value)
    #
    #     # Store the entered text in session state
    #     st.session_state.text_value = a
    #
    #     if st.button("Submit"):
    #         entered_command = st.session_state.text_value.split('\n')[-1].strip().split()[-1]
    #         executed_command = f"\n$wit-reality/ig-service> "
    #         st.session_state.text_value += executed_command
    #         st.write("Executed:", entered_command)
    #         st.experimental_rerun()
    #
    #     st.toast(st.session_state.text_value.split('\n')[-2].strip().split()[-1])
    #
    #     command = st.session_state.text_value.split('\n')[-2].strip().split()[-1]
    #     if command == "mkdir":
    #         st.toast("direcrory created")
    #
    #     try:
    #         data = execute_command(command)
    #         st.toast(data)
    #     except Exception as e:
    #         os.remove("settings.json")
    #         st.error("Ahh Ahh! Instagram caugh us! please refresh the page")


if selected == "Login":
    # Page navigation
    page = option_menu('Authentication', ["Login", 'Signup', 'Dashboard'], icons=['play-btn', 'search', 'info-circle'],
                       menu_icon='intersect', default_index=0, orientation="horizontal")
    if page == "Signup":
        signup()
    elif page == "Login":
        login()
    elif page == "Dashboard":
        dashboard()