import json
import re

import numpy as np
import pandas as pd
from datetime import datetime

import streamlit as st
from sklearn.preprocessing import OrdinalEncoder


def remove_entries(df, value):
    # Count the initial number of rows
    initial_rows = len(df)

    # Filter out rows containing the specified value in the "message" column
    df = df[df['message'] != value]

    # Count the remaining number of rows
    remaining_rows = len(df)

    # Calculate the amount of data removed
    data_removed = initial_rows - remaining_rows

    return df, data_removed


def add_username_column(data):
    # Mapping of values in 'user' column to usernames
    username_mapping = {
        "𝐀𝐛𝐝𝐮𝐥 𝐒𝐡𝐚𝐢𝐤𝐡": "abduldotexe",
        "Aquarius": "mahek21_._"
        # Add more mappings as needed
    }

    # Add a new column 'username' based on the mapping
    data['username'] = data['user'].map(username_mapping)

    return data

# Function to process the uploaded file
def process_file(uploaded_file):
    # Load JSON data from the uploaded file
    json_data = json.load(uploaded_file)

    # Initialize lists to store data
    data_rows = []

    # Iterate through messages
    for message in json_data['messages']:
        # Convert timestamp to datetime object
        timestamp_ms = message['timestamp_ms'] / 1000
        date = datetime.utcfromtimestamp(timestamp_ms).strftime('%Y-%m-%d %H:%M:%S')
        date_only = datetime.utcfromtimestamp(timestamp_ms).strftime('%Y-%m-%d')
        year = datetime.utcfromtimestamp(timestamp_ms).strftime('%Y')
        month = datetime.utcfromtimestamp(timestamp_ms).strftime('%B')
        month_num = datetime.utcfromtimestamp(timestamp_ms).strftime('%m')
        day = datetime.utcfromtimestamp(timestamp_ms).strftime('%d')
        day_name = datetime.utcfromtimestamp(timestamp_ms).strftime('%A')
        hour = datetime.utcfromtimestamp(timestamp_ms).strftime('%H')
        minute = datetime.utcfromtimestamp(timestamp_ms).strftime('%M')

        # Get message content or set it to an empty string if not present
        message_content = message.get('content', '')
        photos_link = []

        if  message_content.encode("Latin1").decode("UTF-8").startswith ("तुमच्या मॅसेज  ला "):
            message_content = "reacted"

        # Determine message type
        if 'share' in message:
            message_type = 'attachment'
            # Check if the attachment contains a link
            if 'link' in message['share']:
                attachment_link = message['share']['link']
                # Check the type of link and append it to the appropriate list
                if attachment_link.startswith('https://www.instagram.com/reel/'):
                    reel_link = attachment_link
                    stories_link = ''
                    post_link = ''
                elif attachment_link.startswith('https://instagram.com/stories/'):
                    reel_link = ''
                    stories_link = attachment_link
                    post_link = ''
                elif attachment_link.startswith('https://www.instagram.com/p/'):
                    reel_link = ''
                    stories_link = ''
                    post_link = attachment_link
                else:
                    reel_link = ''
                    stories_link = ''
                    post_link = ''
            else:
                # If the 'link' key is not present, set all link columns to empty strings
                reel_link = ''
                stories_link = ''
                post_link = ''
        elif 'reactions' in message:
            message_type = 'reaction'
            reel_link = ''
            stories_link = ''
            post_link = ''

        elif 'photos' in message:
            message_type = 'media'
            # Extract URIs of photos
            photos_uris = [photo['uri'] for photo in message['photos']]
            # photos_link.extend(photo['uri'] for photo in message['photos'])
            # print("length of ",len(photos_link))





            # # Set message content to be the URIs of photos
            # message_content = ', '.join(photos_uris)
        else:
            message_type = 'text'
            reel_link = ''
            stories_link = ''
            post_link = ''

        # Count reactions
        reactions_count = len(message.get('reactions', []))
        # Calculate word count and average word length

        words = message_content.split()

        word_count = len(words)
        if word_count > 0:
            avg_word_length = sum(len(word) for word in words) / word_count
        else:
            avg_word_length = 0

        # Extract hashtags, mentions, and URLs
        hashtags = extract_hashtags(message_content)
        mentions = extract_mentions(message_content)
        urls = extract_urls(message_content)

        # Categorize media type
        media_type = categorize_media_type(message)

        # Append data row to list
        data_rows.append(
            [date, date_only, year, month, month_num, day, day_name, hour, minute,
             message['sender_name'].encode("Latin1").decode("UTF-8"), message_content.encode("Latin1").decode("UTF-8"),
             len(message_content), message_type, reactions_count, word_count, avg_word_length, hashtags, mentions,
             media_type, reel_link, stories_link, post_link,photos_link])

    # Create DataFrame
    columns = ['date', 'only_date', 'year', 'month', 'month_num', 'day', 'day_name', 'hour', 'minute', 'user',
               'message',
               'message_length', 'message_type', 'reactions_count', 'word_count', 'avg_word_length', 'hashtags',
               'mentions',
               'media_type', 'reel_link', 'stories_link', 'post_link',"photos_link"]
    df = pd.DataFrame(data_rows, columns=columns)
    df['Message Length'] = df['message'].apply(lambda x: len(x.split(' ')))


    conv_codes, conv_changes = cluster_into_conversations(df)
    df['Conv code'] = conv_codes
    df['Conv change'] = conv_changes

    is_reply, sender_changes = find_replies(df)
    df['Is reply'] = is_reply
    df['Sender change'] = sender_changes

    for subject in df['user'].unique():
        df[subject] = df['user'].apply(lambda x: 1 if x == subject else 0)
        df[f"{subject}_mlength"] = df[subject].values * df['Message Length']

    df = add_username_column(df)

    # Add logic for finding replies and calculating times
    df = add_reply_logic(df)

    # Calculate times based on replies
    reply_times, indices = calculate_times_on_trues(df, 'Is Reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index += 1
        else:
            reply_times_df_list.append(0)

    df['Reply Time'] = reply_times_df_list

    inter_conv_times, indices = calculate_times_on_trues(df, 'Conv change')
    inter_conv_times_df_list = []
    inter_conv_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            inter_conv_times_df_list.append(
                inter_conv_times[inter_conv_time_index].astype("timedelta64[m]").astype("float"))
            inter_conv_time_index = inter_conv_time_index + 1
        else:
            inter_conv_times_df_list.append(0)

    df.index = df['date']

    df['Inter conv time'] = inter_conv_times_df_list
    #
    # value_to_remove = "तुमच्या मॅसेज  ला 😂 अशी प्रतिक्रिया दिली"
    # df, data_removed = remove_entries(df, value_to_remove)
    # print("renoved data columns: ",data_removed)

    return df



def add_reply_logic(df):
    # Ordinal encoders will encode each user with its own number
    user_encoder = OrdinalEncoder()
    df['User Code'] = user_encoder.fit_transform(df['user'].values.reshape(-1, 1))

    # Find replies
    message_senders = df['User Code'].values
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['user'].eq('group_notification')

    df['Is Reply'] = is_reply

    return df

def calculate_times_on_trues(df : pd.DataFrame, column : str):
    assert(column in df.columns)
    true_indices = np.where(df[column])[0]
    inter_conv_time = [df.index.values[ind] - df.index.values[ind-1] for ind in true_indices]
    return inter_conv_time, true_indices


####Working fine till here####

##Section to get the conversation changes data not working here

def cluster_into_conversations(df: pd.DataFrame, inter_conversation_threshold_time: int = 60):
    threshold_time_mins = np.timedelta64(inter_conversation_threshold_time, 'm')

    # This calculates the time between the current message and the previous one
    conv_delta = df.index.values - np.roll(df.index.values, 1)
    conv_delta[0] = 0

    # This detects where the time between messages is higher than the threshold
    conv_changes = conv_delta > threshold_time_mins
    conv_changes_indices = np.where(conv_changes)[0]
    conv_codes = []

    if len(conv_changes_indices) == 0:
        # If there are no changes in conversation, assign all messages to a single conversation
        conv_codes = [0] * len(df)
    else:
        # Otherwise, assign conversation codes based on the detected changes
        last_conv_change = 0
        for i, conv_change in enumerate(conv_changes_indices):
            conv_codes.extend([i] * (conv_change - last_conv_change))
            last_conv_change = conv_change
        conv_codes.extend([len(conv_changes_indices)] * (len(df) - conv_changes_indices[-1]))

    # This serves to ensure that the conversation codes and the number of messages are aligned
    conv_codes = pad_list_to_value(conv_codes, len(df), conv_codes[-1])
    conv_changes = pad_list_to_value(conv_changes, len(df), False)

    return conv_codes, conv_changes


def pad_list_to_value(input_list : list, length : int, value):
    assert(length >= len(input_list))
    output_list = list(input_list)
    padding = [value]*(length - len(output_list))
    output_list.extend(padding)
    return np.array(output_list)


def find_replies(df : pd.DataFrame):
    # These are sanity checks in order to see if I made any ordering mistakes
    assert('Conv code' in df.columns)
    assert('Conv change' in df.columns)
    assert('user' in df.columns)
    # Ordinal encoders will encode each subject with its own number
    message_senders = OrdinalEncoder().fit_transform(df['user'].values.reshape(-1,1))
    # This compares the current subject with the previous subject
    # In a way that computers can optimize
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    # This checks if the reply isn't within a different conversation
    is_reply = sender_changed & ~df['Conv change']
    return is_reply, sender_changed



# Define functions for data processing

def extract_hashtags(message):
    hashtags = re.findall(r'#(\w+)', message)
    return hashtags


def extract_mentions(message):
    mentions = re.findall(r'@(\w+)', message)
    return mentions


def extract_urls(message):
    urls = re.findall(r'(https?://\S+)', message)
    return urls


def categorize_media_type(message):
    if 'share' in message and 'link' in message['share']:
        attachment_url = message['share']['link']
        if attachment_url.endswith('.jpg') or attachment_url.endswith('.png'):
            return 'image'
        elif attachment_url.endswith('.mp4') or attachment_url.endswith('.mov'):
            return 'video'
    return 'other'
