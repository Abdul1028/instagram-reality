import os

import numpy as np
import pylab as pl
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from backend import preprocessor
from sklearn.preprocessing import OrdinalEncoder
from textblob import TextBlob
from urlextract import URLExtract
import emoji
import streamlit as st
import pandas as pd
import nltk
# from pandasai import SmartDataframe
# from pandasai.llm import OpenAI

extract = URLExtract()
nltk.download('vader_lexicon')

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages (either '<Media omitted>\n', 'video omitted', or 'image omitted')
    num_media_messages = (df['message_type'] == 'media').sum()

    num_of_reactions = (df['message'] == 'reacted').sum()

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links),num_of_reactions


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user,df):

    f = open('backend/stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df    ['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


from wordcloud import WordCloud,STOPWORDS
import plotly.graph_objs as go
from plotly.offline import plot
from collections import Counter

def plotly_wordcloud(text, stopwords=None):
    if stopwords is None:
        stopwords = set(STOPWORDS)

    wc = WordCloud(stopwords=stopwords,
                   width=500,
                   height=500,
                   min_font_size=10,
                   background_color='white')
    df_wc = wc.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # calculate the relative occurrence frequencies
    max_freq = max(freq_list)
    new_freq_list = [freq / max_freq * 100 for freq in freq_list]

    trace = go.Scatter(x=[pos[0] for pos in position_list],
                       y=[pos[1] for pos in position_list],
                       textfont=dict(size=new_freq_list, color=color_list),
                       hoverinfo='text',
                       hovertext=['{0} (x: {1})'.format(w, c) for w, c in zip(word_list, new_freq_list)],                       mode='text',
                       text=word_list
                       )

    layout = go.Layout(xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                       yaxis=dict(showgrid=False, showticklabels=False, zeroline=False))

    fig = go.Figure(data=[trace], layout=layout)

    return fig

def create_plotly_wordcloud(selected_user, df):
    with open('backend/stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].isin(['<Media omitted>\n', 'image omitted', 'video omitted'])]

    def remove_stop_words(message):
        return " ".join(word for word in message.lower().split() if word not in stop_words)

    temp['message'] = temp['message'].apply(remove_stop_words)
    wordcloud_text = temp['message'].str.cat(sep=" ")

    return plotly_wordcloud(wordcloud_text)


def most_common_words(selected_user,df):

    f = open('backend/stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20),columns=['Word', 'Frequency'])
    return most_common_df


def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
        emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

def analyze_sentiment(message):
    blob = TextBlob(message)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        return "Positive"
    elif sentiment_score < 0:
        return "Negative"
    else:
        return "Neutral"

def message_length_analysis(selected_participant,df):
    filtered_df = df[df['user'] == selected_participant] if selected_participant != 'Overall' else df
    filtered_df['message_length'] = filtered_df['message'].apply(lambda msg: len(msg))
    average_length = filtered_df['message_length'].mean()
    st.info(f"Average Message Length for {selected_participant}: {average_length:.2f}")


# Function for busiest hours analysis
def busiest_hours_analysis(df):
    busiest_hours = df['hour'].value_counts()
    st.bar_chart(busiest_hours)


# Function for message count by month
def message_count_by_month(selected_participant,df):
    filtered_df = df[df['user'] == selected_participant] if selected_participant != 'Overall' else df
    message_count_per_month = filtered_df.groupby(['year', 'month']).count()['message'].reset_index()
    st.dataframe(message_count_per_month)


# Function for top emojis used
def top_emojis_used(selected_participant,df):
    filtered_df = df[df['user'] == selected_participant] if selected_participant != 'Overall' else df
    emojis = [c for message in filtered_df['message'] for c in message if c in emoji.UNICODE_EMOJI['en']]
    top_emojis = Counter(emojis).most_common()
    st.write(f"Top Emojis Used by {selected_participant}: {top_emojis}")


# Function for greeting and farewell analysis
def greeting_farewell_analysis(selected_participant, df):
    filtered_df = df[df['user'] == selected_participant] if selected_participant != 'Overall' else df

    greetings = filtered_df['message'].apply(lambda msg: 'hello' in msg.lower() or 'hi' in msg.lower()).sum()
    farewells = filtered_df['message'].apply(lambda msg: 'goodbye' in msg.lower() or 'bye' in msg.lower()).sum()
    birthdays = filtered_df['message'].apply(
        lambda msg: 'happy birthday' in msg.lower() or 'happiest birthday' in msg.lower()).sum()

    total_messages = filtered_df.shape[0]
    greeting_percentage = (greetings / total_messages) * 100
    farewell_percentage = (farewells / total_messages) * 100
    birthday_percentage = (birthdays / total_messages) * 100

    # Create a pie chart using Plotly
    labels = ['Greetings', 'Farewells', 'Birthday Wishes']
    sizes = [greeting_percentage, farewell_percentage, birthday_percentage]
    colors = ['yellowgreen', 'lightskyblue', 'lightcoral']

    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3)])
    fig.update_layout(title=f"Greeting, Farewell, and Birthday Wishes Analysis by {selected_participant}")

    greetings = filtered_df['message'].apply(lambda msg: 'hello' in msg.lower() or 'hi' in msg.lower()).sum()
    farewells = filtered_df['message'].apply(lambda msg: 'goodbye' in msg.lower() or 'bye' in msg.lower()).sum()
    birthdays = filtered_df['message'].apply(
        lambda msg: 'happy birthday' in msg.lower() or 'happiest birthday' in msg.lower()).sum()

    st.write(f"Total Greetings by {selected_participant}: {greetings}")
    st.write(f"Total Farewells by {selected_participant}: {farewells}")
    st.write(f"Total Birthday Wishes by {selected_participant}: {birthdays}")

    st.plotly_chart(fig)


# Function for topic analysis using LDA
with open('backend/stop_hinglish.txt', 'r') as f:
    stop_words = set(f.read().splitlines())

# Function for topic analysis using LDA with heuristic topic naming
# Load the stop words from the file
with open('backend/stop_hinglish.txt', 'r') as f:
    stop_words = set(f.read().splitlines())


#Only highest Reply time user display
def longest_reply_user(df):
    # Ordinal encoders will encode each user with its own number
    user_encoder = OrdinalEncoder()
    df['User Code'] = user_encoder.fit_transform(df['user'].values.reshape(-1, 1))

    # Find replies
    message_senders = df['User Code'].values
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['user'].eq('group_notification')

    df['Is Reply'] = is_reply

    # Calculate times based on replies
    reply_times, indices = preprocessor.calculate_times_on_trues(df, 'Is Reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index += 1
        else:
            reply_times_df_list.append(0)

    df['Reply Time'] = reply_times_df_list

    # Calculate the maximum reply time for each user
    max_reply_times = df.groupby('user')['Reply Time'].max()

    # Find the user with the longest reply time
    max_reply_user = max_reply_times.idxmax()
    max_reply_time = max_reply_times.max()
    return max_reply_user, max_reply_time


#additional info about reply

def longest_reply_user2(df):

    # Filter out messages containing the specified strings
    omitted_strings = ["image omitted", "media omitted", "video omitted"]
    df = df[~df['message'].str.lower().str.contains('|'.join(omitted_strings))]

    # Ordinal encoders will encode each user with its own number
    user_encoder = OrdinalEncoder()
    df['User Code'] = user_encoder.fit_transform(df['user'].values.reshape(-1, 1))

    # Find replies
    message_senders = df['User Code'].values
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['user'].eq('group_notification')

    df['Is Reply'] = is_reply

    # Calculate times based on replies
    reply_times, indices = preprocessor.calculate_times_on_trues(df, 'Is Reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index += 1
        else:
            reply_times_df_list.append(0)

    df['Reply Time'] = reply_times_df_list

    # Calculate the maximum reply time for each user
    max_reply_times = df.groupby('user')['Reply Time'].max()

    # Find the user with the longest reply time
    max_reply_user = max_reply_times.idxmax()
    max_reply_time_minutes = max_reply_times.max()  # Max reply time in minutes

    # Find the message to which the user replied the most late
    max_reply_message_index = df[df['Reply Time'] == max_reply_time_minutes].index[0]
    max_reply_message = df.loc[max_reply_message_index, 'message']

    reply = df.shift(1).loc[max_reply_message_index, 'message']

    return max_reply_user, max_reply_time_minutes, max_reply_message,reply



def top5_late_replies(df):
    # Filter out messages containing the specified strings
    omitted_strings = ["image omitted", "media omitted", "video omitted"]
    df = df[~df['message'].str.lower().str.contains('|'.join(omitted_strings))]

    # Ordinal encoders will encode each user with its own number
    user_encoder = OrdinalEncoder()
    df['User Code'] = user_encoder.fit_transform(df['user'].values.reshape(-1, 1))

    # Find replies
    message_senders = df['User Code'].values
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['user'].eq('group_notification')

    df['Is Reply'] = is_reply

    # Calculate times based on replies
    reply_times, indices = preprocessor.calculate_times_on_trues(df, 'Is Reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index += 1
        else:
            reply_times_df_list.append(0)

    df['Reply Time'] = reply_times_df_list

    # Calculate the maximum reply time for each user
    max_reply_times = df.groupby('user')['Reply Time'].max()

    # Find the top 5 users with the longest reply times
    top_5_users = max_reply_times.nlargest(5)

    # Initialize lists to store results
    users = []
    reply_times = []
    max_reply_messages = []
    replies = []

    # Iterate over the top 5 users
    for user, max_reply_time in top_5_users.items():
        # Find the message to which the user replied the most late
        max_reply_message_index = df[df['Reply Time'] == max_reply_time].index[0]
        max_reply_message = df.loc[max_reply_message_index, 'message']

        # Get the reply to the max reply message
        reply = df.shift(1).loc[max_reply_message_index, 'message']

        # Append user, max reply time, max reply message, and reply to lists
        users.append(user)
        reply_times.append(max_reply_time)
        max_reply_messages.append(max_reply_message)
        replies.append(reply)

    return users, reply_times, max_reply_messages, replies


def top_texts_late_replies(df):
    # Filter out messages containing the specified strings
    omitted_strings = ["image omitted", "media omitted", "video omitted"]
    df = df[~df['message'].str.lower().str.contains('|'.join(omitted_strings))]

    # Ordinal encoders will encode each user with its own number
    user_encoder = OrdinalEncoder()
    df['User Code'] = user_encoder.fit_transform(df['user'].values.reshape(-1, 1))

    # Find replies
    message_senders = df['User Code'].values
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['user'].eq('group_notification')

    df['Is Reply'] = is_reply

    # Calculate times based on replies
    reply_times, indices = preprocessor.calculate_times_on_trues(df, 'Is Reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index += 1
        else:
            reply_times_df_list.append(0)

    df['Reply Time'] = reply_times_df_list

    # Filter out texts with reply time greater than 1 day
    df = df[df['Reply Time'] > (48 * 60)]  # 1 day in minutes

    # Find the top 5 users with the longest reply times
    top_5_users = df.groupby('user')['Reply Time'].max().nlargest(5)

    # Initialize lists to store results
    users = []
    reply_times = []
    max_reply_messages = []
    replies = []

    # Iterate over the top 5 users
    for user, max_reply_time in top_5_users.items():
        # Find the message to which the user replied the most late
        max_reply_message_index = df[df['Reply Time'] == max_reply_time].index[0]
        max_reply_message = df.loc[max_reply_message_index, 'message']

        # Get the reply to the max reply message
        reply = df.shift(1).loc[max_reply_message_index, 'message']

        # Append user, max reply time, max reply message, and reply to lists
        users.append(user)
        reply_times.append(max_reply_time)
        max_reply_messages.append(max_reply_message)
        replies.append(reply)

    return users, reply_times, max_reply_messages, replies




# shows everyone's reply time and also plots graph
def show_average_reply_time(df):
    # Group by user and calculate the average reply time
    user_avg_reply_time = df.groupby('user')['Reply Time'].mean().reset_index()

    # Find the user with the highest average reply time
    highest_avg_reply_user = user_avg_reply_time.loc[user_avg_reply_time['Reply Time'].idxmax()]

    # Plot the interactive plot
    fig = px.bar(user_avg_reply_time, x='user', y='Reply Time', title='Average Reply Time by User')
    fig.update_layout(xaxis_title='User', yaxis_title='Average Reply Time')
    fig.update_traces(marker_color='lightskyblue')

    # Add annotation for the highest reply time user
    fig.add_annotation(x=highest_avg_reply_user['user'], y=highest_avg_reply_user['Reply Time'],
                       text=f'Highest Reply Time User: {highest_avg_reply_user["user"]}',
                       showarrow=True, arrowhead=1, ax=0, ay=-40)

    # Show the plot
    st.plotly_chart(fig)



def _create_wide_area_fig(df : pd.DataFrame, legend : bool = True):
    fig, ax = plt.subplots(figsize=(12,5))
    df.plot(
        alpha=0.6,
        cmap=plt.get_cmap('viridis'),
        ax=ax,
        stacked=True
    )
    ax.patch.set_alpha(0.0)
    fig.patch.set_alpha(0.0)
    if legend:
        ax.legend(df['user'])
    return fig


def create_narrow_pie_fig(df : pd.DataFrame):
    narrow_figsize = (6, 5)
    cmap = plt.get_cmap('viridis')
    fig1, ax = plt.subplots(figsize=narrow_figsize)
    df.plot(kind='pie', cmap=cmap, ax=ax, autopct='%1.1f%%', explode=[0.015] * len(df.index.unique()))
    centre_circle = plt.Circle((0, 0), 0.80, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    ax.patch.set_alpha(0.0)
    fig.patch.set_alpha(0.0)
    ax.set_ylabel('')
    return fig


def message_count_aggregated_graph(df):
    subject_df = df.groupby('user').count()['message'].sort_values(ascending=False)
    most_messages_winner = subject_df.index[subject_df.argmax()]
    # fig = create_narrow_pie_fig(subject_df)

    # Create a Pie chart
    fig = go.Figure(data=[go.Pie(labels=subject_df.index, values=subject_df.values)])
    fig.update_layout(title="Message Count Aggregated by User")

    return fig, most_messages_winner


def conversation_starter_graph(df):
    subject_df = df[df['Conv change']].groupby('user').count()['Reply Time']

    # Create a Pie chart
    fig = go.Figure(data=[go.Pie(labels=subject_df.index, values=subject_df.values)])
    fig.update_layout(title="Conversation Starter Count by User")

    most_messages_winner = subject_df.index[subject_df.argmax()]
    return fig,most_messages_winner

def conversation_size_aggregated_graph( df):
    conversations_df = df.groupby('Conv code').agg(count=('Conv code', 'size'),
                                                   mean_date=('date', 'mean')).reset_index()
    conversations_df.index = conversations_df['mean_date']
    conversations_df = conversations_df.resample('W').mean().fillna(0)

    # Create a line plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=conversations_df.index, y=conversations_df['count'], mode='lines', fill='tozeroy'))
    fig.update_layout(title="Conversation Size Aggregated over Time",
                      xaxis_title="Date",
                      yaxis_title="Average Conversation Size")

    return fig

def most_idle_date_time(df):
    df['date'] = pd.to_datetime(df['date'])

    # Group the data by date and calculate total idle time
    grouped_by_date = df.groupby(df['date'].dt.date)['Inter conv time'].sum()

    # Find the date(s) with the maximum idle time
    max_idle_date = grouped_by_date.idxmax()
    max_idle_time = grouped_by_date[max_idle_date]

    return max_idle_date,max_idle_time

def median_delay_btwn_convo(df):

    df['date'] = pd.to_datetime(df['date'])

    # Calculate reply delay within each conversation
    df['Reply Delay'] = df.groupby('Conv code')['date'].diff().dt.total_seconds() / 60.0  # Convert to minutes

    # Group by conversation and calculate median reply delay
    median_delay_per_conversation = df.groupby('Conv code')['Reply Delay'].median()

    # Calculate overall median delay across all conversations
    overall_median_delay = median_delay_per_conversation.median()

    print(f"Median Delay Between Conversations: {overall_median_delay:.2f} minutes")

def median_delay_between_conversations(user,df):
    if user != "Overall":
        df['date'] = pd.to_datetime(df['date'])
        # Filter DataFrame to include only messages sent by the specified user
        user_messages = df[df['user'] == user]

        # Calculate reply delay within each conversation for the user
        user_messages['Reply Delay'] = user_messages.groupby('Conv code')[
                                           'date'].diff().dt.total_seconds() / 60.0  # Convert to minutes
        # Display the median reply delay for the user
        median_delay_per_user = user_messages['Reply Delay'].median()
        return median_delay_per_user

    return None



def double_text_counts(user_of_interest, df):
    # Store the original index of the DataFrame
    original_index = df.index

    # Reset the index of the DataFrame
    df = df.reset_index(drop=True)

    # Filter DataFrame to include only messages sent by the specified user
    user_messages = df[df['user'] == user_of_interest]

    # Convert 'date' column to datetime if it's not already
    user_messages['date'] = pd.to_datetime(user_messages['date'])

    # Sort DataFrame by date
    user_messages = user_messages.sort_values(by='date')

    # Define the threshold for double texting (in minutes)
    threshold_minutes = 1440  # Adjust as needed

    # Initialize double texting count
    double_texting_count = 0

    # Calculate the time difference between consecutive messages for the user
    time_diff = user_messages['date'].diff().dt.total_seconds() / 60.0  # Convert to minutes

    # Identify instances of double texting
    double_texting_indices = time_diff < threshold_minutes

    # Count the number of double texting instances
    double_texting_count = sum(double_texting_indices)

    # Restore the original index of the DataFrame
    user_messages.index = original_index[user_messages.index]

    return double_texting_count


def response_activity(user,df):
    df['date'] = pd.to_datetime(df['date'])
    # Sort DataFrame by date
    df = df.sort_index()

    # Initialize counts dictionary to store counts for each time interval
    time_intervals = [20, 40, 60, 80, 100, 120]
    counts = {interval: 0 for interval in time_intervals}
    counts['>120'] = 0

    # Filter DataFrame to include only messages sent by the specified user
    user_messages = df[df['user'] == user]

    # Iterate over each row in the filtered DataFrame
    for index, row in user_messages.iterrows():
        # Check if the message is a repl
        if row['Is reply']:
            print("Row columns: ")
            print(row,index)
            # Find the index of the previous message sent by the same user
            previous_index = index - 1
            while previous_index >= 0 and df.loc[previous_index, 'user'] != user:
                previous_index -= 1

            # If a previous message is found, calculate the time difference
            if previous_index >= 0:
                reply_time = (row['date'] - df.loc[previous_index, 'date']).total_seconds()
                # Iterate over time intervals and update counts accordingly
                for interval in time_intervals:
                    if reply_time <= interval:
                        counts[interval] += 1
                        break
                else:
                    counts['>120'] += 1

    # Return the counts
    return counts



import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.graph_objects as go

def analyze_and_plot_sentiment(selected_users,df):
    nltk.download('vader_lexicon')
    # Filter messages based on selected users
    if selected_users  == 'Overall':
        selected_df = df['message']  # Consider the whole message column if 'Overall' is selected
    else:
        if isinstance(selected_users, str):
            selected_users = [selected_users]  # Convert to list if only one user is selected
        selected_df = df[df['user'].isin(selected_users)]['message']


    # Initialize the sentiment analyzer outside the function
    sid = SentimentIntensityAnalyzer()

    # Initialize dictionaries to store positive and negative scores for each word
    positive_word_sentiments = {}
    negative_word_sentiments = {}

    # Tokenize the conversation into words
    words = nltk.word_tokenize(' '.join(selected_df))

    # Iterate over each word in the conversation
    for word in words:
        # Get sentiment score for the word
        sentiment_score = sid.polarity_scores(word)['compound']

        # Update word_sentiments dictionary based on sentiment score
        if sentiment_score > 0:
            positive_word_sentiments[word] = positive_word_sentiments.get(word, 0) + sentiment_score
        elif sentiment_score < 0:
            negative_word_sentiments[word] = negative_word_sentiments.get(word, 0) + sentiment_score

    # Sort dictionaries by their values (sentiment scores)
    sorted_positive_words = sorted(positive_word_sentiments.items(), key=lambda x: x[1], reverse=True)
    sorted_negative_words = sorted(negative_word_sentiments.items(), key=lambda x: x[1], reverse=True)

    # Extract words and scores for plotting
    positive_words, positive_scores = zip(*sorted_positive_words)
    negative_words, negative_scores = zip(*sorted_negative_words)

    # Create hover text for positive sentiment scores
    positive_hover_text = [
        f'Word: {word}<br>Sentiment Score: {score}<br>Frequency: {positive_word_sentiments[word]}<br>Frequency: {words.count(word)}'
        for
        word, score in zip(positive_words, positive_scores)]

    # Create hover text for negative sentiment scores
    negative_hover_text = [
        f'Word: {word}<br>Sentiment Score: {score}<br>Frequency: {negative_word_sentiments[word]}<br>Frequency: {words.count(word)}'
        for
        word, score in zip(negative_words, negative_scores)]

    # Create histogram for positive sentiment scores
    positive_trace = go.Bar(
        x=positive_words,
        y=positive_scores,
        marker_color='blue',
        name='Positive',
        hovertext=positive_hover_text
    )

    # Create histogram for negative sentiment scores
    negative_trace = go.Bar(
        x=negative_words,
        y=negative_scores,
        marker_color='red',
        name='Negative',
        hovertext=negative_hover_text
    )

    # Create layout for positive scores histogram
    positive_layout = go.Layout(
        title='Positive Sentiment Scores by Word',
        xaxis=dict(title='Words'),
        yaxis=dict(title='Sentiment Score')
    )

    # Create layout for negative scores histogram
    negative_layout = go.Layout(
        title='Negative Sentiment Scores by Word',
        xaxis=dict(title='Words'),
        yaxis=dict(title='Sentiment Score', autorange="reversed")
    )

    # Create figure for positive scores histogram
    positive_fig = go.Figure(data=[positive_trace], layout=positive_layout)

    # Create figure for negative scores histogram
    negative_fig = go.Figure(data=[negative_trace], layout=negative_layout)


    return positive_fig, negative_fig



def calculate_sentiment_percentage(selected_users, df):
    nltk.download('vader_lexicon')

    # Filter messages based on selected users
    if selected_users == 'Overall':
        selected_df = df  # Consider the whole dataframe if 'Overall' is selected
    else:
        if isinstance(selected_users, str):
            selected_users = [selected_users]  # Convert to list if only one user is selected
        selected_df = df[df['user'].isin(selected_users)]

    # Initialize the sentiment analyzer outside the function
    sid = SentimentIntensityAnalyzer()

    # Initialize counters for positive and negative sentiment scores
    positive_count = 0
    negative_count = 0

    # Dictionary to store positivity and negativity percentages for each user
    user_sentiment_percentages = {}

    # Tokenize and analyze sentiment for each message
    for user, messages in selected_df.groupby('user')['message']:
        # Reset counters for each user
        positive_count = 0
        negative_count = 0

        # Calculate sentiment scores for each message
        for message in messages:
            sentiment_score = sid.polarity_scores(message)['compound']
            if sentiment_score > 0:
                positive_count += 1
            elif sentiment_score < 0:
                negative_count += 1

        # Calculate positivity and negativity percentages for the user
        total_messages = len(messages)
        positivity_percentage = (positive_count / total_messages) * 100
        negativity_percentage = (negative_count / total_messages) * 100

        # Format percentages as strings with two decimal places and a percentage sign
        formatted_positivity = f"{positivity_percentage:.2f}%"
        formatted_negativity = f"{negativity_percentage:.2f}%"

        # Store the percentages in the dictionary
        user_sentiment_percentages[user] = (formatted_positivity, formatted_negativity)

    # Find the most positive and most negative users
    most_positive_user = max(user_sentiment_percentages, key=lambda x: user_sentiment_percentages[x][0])
    most_negative_user = min(user_sentiment_percentages, key=lambda x: user_sentiment_percentages[x][1])

    return user_sentiment_percentages, most_positive_user, most_negative_user



import pandas as pd
import numpy as np
import plotly.express as px

import pandas as pd
import plotly.express as px
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import pandas as pd
import plotly.express as px
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def calculate_monthly_sentiment_trend(df):
    # Make a copy of the DataFrame to avoid modifying the original DataFrame
    df_copy = df.copy()
    nltk.download('vader_lexicon')

    # Initialize the sentiment analyzer outside the function
    sid = SentimentIntensityAnalyzer()

    # Tokenize and analyze sentiment for each message
    sentiment_scores = []
    for message in df_copy['message']:
        # Get sentiment score for the message
        sentiment_score = sid.polarity_scores(message)['compound']
        sentiment_scores.append(sentiment_score)

    # Add sentiment scores to the copied DataFrame
    df_copy['sentiment_score'] = sentiment_scores

    # Convert 'date' column to datetime if it's not already
    df_copy['date'] = pd.to_datetime(df_copy['date'])

    # Group data by month and calculate positivity and negativity percentages
    df_copy['month'] = df_copy['date'].dt.to_period('M')
    monthly_sentiment = df_copy.groupby('month').agg(
        positivity_percentage=('sentiment_score', lambda x: (x > 0).mean() * 100),
        negativity_percentage=('sentiment_score', lambda x: (x < 0).mean() * 100)
    )

    # Convert Period index to string for serialization
    monthly_sentiment.index = monthly_sentiment.index.astype(str)

    # Plot the trend
    fig = px.line(monthly_sentiment, x=monthly_sentiment.index, y=['positivity_percentage', 'negativity_percentage'],
                  title='Monthly Sentiment Trend',
                  labels={'month': 'Month', 'value': 'Percentage', 'variable': 'Sentiment'},
                  color_discrete_map={'positivity_percentage': 'blue', 'negativity_percentage': 'red'})
    fig.update_xaxes(type='category')  # Ensure x-axis is treated as categorical

    return fig


import pandas as pd
import plotly.express as px
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def create_messages_per_week_graph(df: pd.DataFrame):
    # Convert 'Date' column to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])

    # Makes the first graph
    date_df = df.groupby(df.index)[df['user']].sum().resample('W').sum()
    fig = _create_wide_area_fig(date_df)

    max_message_count = date_df[df['user']].sum(axis=1).max()
    max_message_count_date = date_df.index[date_df[df['user']].sum(axis=1).argmax()]
    return fig, max_message_count, max_message_count_date

def create_average_wpm_graph( df : pd.DataFrame):
    other_y_columns = [f"{subject}_mlength" for subject in df['user'].unique()]
    date_avg_df = df[other_y_columns].resample('W').mean()
    fig = _create_wide_area_fig(date_avg_df)
    return fig

# Function to plot Top Users
def plot_top_users(data):
    top_users = data['user'].value_counts().reset_index()
    top_users.columns = ['User', 'Message Count']
    fig = px.bar(top_users, x='User', y='Message Count', title='Top Users by Message Count')
    return fig

# Function to plot Hashtag and Mention Frequency
def plot_hashtag_mention_frequency(data):
    hashtags = data['hashtags'].explode().value_counts().reset_index()
    hashtags.columns = ['Hashtag', 'Frequency']
    mentions = data['mentions'].explode().value_counts().reset_index()
    mentions.columns = ['Mention', 'Frequency']

    hashtag_fig = px.bar(hashtags.head(10), x='Hashtag', y='Frequency', title='Top 10 Hashtags by Frequency')
    mention_fig = px.bar(mentions.head(10), x='Mention', y='Frequency', title='Top 10 Mentions by Frequency')

    return hashtag_fig, mention_fig

# Function to plot Media Type Distribution
def plot_media_type_distribution(data):
    media_distribution = data['media_type'].value_counts().reset_index()
    media_distribution.columns = ['Media Type', 'Count']
    fig = px.pie(media_distribution, values='Count', names='Media Type', title='Media Type Distribution')
    return fig

# Function to plot Word Frequency by User
def plot_word_frequency_by_user(data):
    word_frequency_by_user = data.groupby('user')['message'].apply(lambda x: ' '.join(x)).reset_index()
    word_frequency_by_user['word_count'] = word_frequency_by_user['message'].apply(lambda x: len(x.split()))

    fig = px.bar(word_frequency_by_user.sort_values(by='word_count', ascending=False).head(10),
                 x='user', y='word_count', title='Word Frequency by User (Top 10)')
    return fig
# Function to retrieve the user who has sent the most stories
def most_stories_user(data):
    stories_users = data[data['stories_link'] != '']['user'].value_counts()
    most_stories_user = stories_users.idxmax()
    most_stories_count = stories_users.max()
    return most_stories_user, most_stories_count

# Function to retrieve the user who has sent the most reels
def most_reels_user(data):
    reels_users = data[data['reel_link'] != '']['user'].value_counts()
    most_reels_user = reels_users.idxmax()
    most_reels_count = reels_users.max()
    return most_reels_user, most_reels_count

# Function to retrieve the user who has sent the most posts
def most_posts_user(data):
    posts_users = data[data['post_link'] != '']['user'].value_counts()
    most_posts_user = posts_users.idxmax()
    most_posts_count = posts_users.max()
    return most_posts_user, most_posts_count

# Function to create a bar chart
def create_plot_for_attachment_distribution(users_counts):
    fig = go.Figure(data=[
        go.Bar(name='Most Reels', x=[users_counts['most_reels_user']], y=[users_counts['most_reels_count']]),
        go.Bar(name='Most Posts', x=[users_counts['most_posts_user']], y=[users_counts['most_posts_count']]),
        go.Bar(name='Most Stories', x=[users_counts['most_stories_user']], y=[users_counts['most_stories_count']])
    ])

    # Update the layout
    fig.update_layout(title='Users with Most Reels, Posts, and Stories',
                      xaxis_title='User',
                      yaxis_title='Count')

    # Show the plot
    st.plotly_chart(fig)


# Function to categorize messages as story mentions or story replies and keep track of counts
def categorize_story_mentions_and_replies(data):
    # Initialize counts for story mentions and story replies
    story_mention_count = 0
    story_reply_count = 0

    # Filter the DataFrame to select rows that contain story links
    story_links = data[data['stories_link'].notna()]

    a = st.expander("View story replies!")
    # Iterate through each row containing a story link
    for index, row in story_links.iterrows():
        # Split the story link to extract the username
        story_link_parts = row['stories_link'].split('/')
        if len(story_link_parts) >= 3:
            story_username = story_link_parts[-2]

            # Compare the username in the story link with the username in the row
            if story_username == row['username']:
                # st.write("Story mention:", row['message'])
                # Increment the count of story mentions
                story_mention_count += 1
            else:
                with a:
                    st.write("Story reply:", row['message'])
                    # Increment the count of story replies
                    story_reply_count += 1


    # Print the counts of story mentions and story replies
    st.info(f"They replied to your stories: {story_reply_count} times to start a casual chit chat!")
    st.info(f"You mentioned them {story_mention_count } times in your memorable stories!")


import plotly.graph_objs as go

# Function to visualize attachments by user using Plotly
def visualize_attachments_by_user_plotly(data):
    # Group the data by user and count the number of attachments
    attachments_count = data[data['message_type'] == 'attachment'].groupby('user').size()

    # Group the data by user and count the types of attachments
    attachments_types_count = data[data['message_type'] == 'attachment'].groupby(['user', 'media_type']).size().unstack(fill_value=0)

    # Find the user who sent the most attachments
    most_attachments_user = attachments_count.idxmax()
    most_attachments_count = attachments_count.max()

    # Create bar chart for attachments count by user
    attachments_bar = go.Bar(
        x=attachments_count.index,
        y=attachments_count.values,
        name='Attachments Count',
        marker=dict(color='rgb(158,202,225)'),
        # Highlight the user who sent the most attachments
        marker_line_color='red' if attachments_count.index.isin([most_attachments_user]).any() else 'rgba(0,0,0,0)',
        marker_line_width=3
    )

    # Create bar chart for attachments types count by user
    attachments_types_bar = go.Bar(
        x=attachments_types_count.index,
        y=attachments_types_count.values,
        name='Attachments Types Count',
        marker=dict(color='rgb(49,130,189)'),
        hoverinfo='text',
        text=attachments_types_count.values.tolist(),
        textposition='auto'
    )

    # Create figure
    fig = go.Figure(data=[attachments_bar, attachments_types_bar])

    # Update layout
    fig.update_layout(
        title='Attachments Sent by User',
        xaxis_title='User',
        yaxis_title='Number of Attachments',
        barmode='group',
        legend=dict(title='Legend', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest'
    )

    return fig,most_attachments_user,most_attachments_count



