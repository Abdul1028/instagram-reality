import html
import re

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

gemini_url = "https://www.gstatic.com/lamda/images/gemini_favicon_b0ca051193f92ba9f912679dcf95b0efa9f201b6.svg"
mistral_url =  "mistral-ai-icon-logo-B3319DCA6B-seeklogo.com.png"
openai_url = "data:image/jpeg;base64,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"

def get_model_url(model_name):
    if "gpt" in model_name.lower():
        return openai_url
    elif "gemini" in model_name.lower():
        return gemini_url
    elif "mistral" in model_name.lower():
        return mistral_url
    return mistral_url


def format_message(text):
    """
    This function is used to format the messages in the chatbot UI.

    Parameters:
    text (str): The text to be formatted.
    """
    text_blocks = re.split(r"```[\s\S]*?```", text)
    code_blocks = re.findall(r"```([\s\S]*?)```", text)

    text_blocks = [html.escape(block) for block in text_blocks]

    formatted_text = ""
    for i in range(len(text_blocks)):
        formatted_text += text_blocks[i].replace("\n", "<br>")
        if i < len(code_blocks):
            formatted_text += f'<pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{html.escape(code_blocks[i])}</code></pre>'

    return formatted_text


def message_func(text, is_user=False, is_df=False, model="gpt"):
    """
    This function is used to display the messages in the chatbot UI.

    Parameters:
    text (str): The text to be displayed.
    is_user (bool): Whether the message is from the user or not.
    is_df (bool): Whether the message is a dataframe or not.
    """
    model_url = get_model_url(model)

    avatar_url = model_url
    if is_user:
        avatar_url = "https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription01&hairColor=Auburn&facialHairType=BeardLight&facialHairColor=Black&clotheType=Hoodie&clotheColor=PastelBlue&eyeType=Squint&eyebrowType=DefaultNatural&mouthType=Smile&skinColor=Tanned"
        message_alignment = "flex-end"
        message_bg_color = "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)"
        avatar_class = "user-avatar"
        st.write(
            f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%; font-size: 14px;">
                        {text} \n </div>
                    <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width: 40px; height: 40px;" />
                </div>
                """,
            unsafe_allow_html=True,
        )
    else:
        message_alignment = "flex-start"
        message_bg_color = "#71797E"
        avatar_class = "bot-avatar"

        if is_df:
            st.write(
                f"""
                    <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                        <img src="{model_url}" class="{avatar_class}" alt="avatar" style="width: 50px; height: 50px;" />
                    </div>
                    """,
                unsafe_allow_html=True,
            )
            st.write(text)
            return
        else:
            text = format_message(text)

        st.write(
            f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width: 30px; height: 30px;" />
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; margin-left: 5px; max-width: 75%; font-size: 14px;">
                        {text} \n </div>
                </div>
                """,
            unsafe_allow_html=True,
        )


class StreamlitUICallbackHandler(BaseCallbackHandler):
    def __init__(self, model):
        self.token_buffer = []
        self.placeholder = st.empty()
        self.has_streaming_ended = False
        self.has_streaming_started = False
        self.model = model
        self.avatar_url = get_model_url(model)

    def start_loading_message(self):
        loading_message_content = self._get_bot_message_container("Thinking...")
        self.placeholder.markdown(loading_message_content, unsafe_allow_html=True)

    def on_llm_new_token(self, token, run_id, parent_run_id=None, **kwargs):
        if not self.has_streaming_started:
            self.has_streaming_started = True

        self.token_buffer.append(token)
        complete_message = "".join(self.token_buffer)
        container_content = self._get_bot_message_container(complete_message)
        self.placeholder.markdown(container_content, unsafe_allow_html=True)

    def on_llm_end(self, response, run_id, parent_run_id=None, **kwargs):
        self.token_buffer = []
        self.has_streaming_ended = True
        self.has_streaming_started = False

    def _get_bot_message_container(self, text):
        """Generate the bot's message container style for the given text."""
        formatted_text = format_message(text)
        container_content = f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: flex-start;">
                <img src="{self.avatar_url}" class="bot-avatar" alt="avatar" style="width: 30px; height: 30px;" />
                <div style="background: #71797E; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; margin-left: 5px; max-width: 75%; font-size: 14px;">
                    {formatted_text} \n </div>
            </div>
        """
        return container_content

    def display_dataframe(self, df):
        """
        Display the dataframe in Streamlit UI within the chat container.
        """
        message_alignment = "flex-start"
        avatar_class = "bot-avatar"

        st.write(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                <img src="{self.avatar_url}" class="{avatar_class}" alt="avatar" style="width: 30px; height: 30px;" />
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(df)

    def __call__(self, *args, **kwargs):
        pass
