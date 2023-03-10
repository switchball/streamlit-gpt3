import string
import random
import streamlit as st
from typing import Union

def generate_share_link():
    # Put conversations into a random link
    share_word = random_words()
    conversations = {
        "preset": st.session_state['preset'],
        "prompt": st.session_state['prompt_system'],
        "conv_user": st.session_state["conv_user"],
        "conv_robot": st.session_state["conv_robot"],
        "input": st.session_state['input']
    }
    # Call save mode
    _load_conversations(_mode="save", _conversation=conversations, key=share_word)
    return f"/?share={share_word}"

def restore_from_share_link():
    # Restore from link
    query = st.experimental_get_query_params()
    share_key = query.get("share", [""])[0]
    if share_key and ('loaded_from_share' not in st.session_state):
        conversation = _load_conversations(key=share_key)
        if conversation is None:
            return 
        st.session_state['preset'] = conversation['preset']
        st.session_state['prompt_system'] = conversation['prompt']
        st.session_state['conv_user'] = conversation['conv_user']
        st.session_state['conv_robot'] = conversation['conv_robot']
        st.session_state['input'] = conversation['input']
        st.session_state['loaded_from_share'] = True
        st.success("已自动加载分享的聊天内容")
    

def random_words(length=8):
    letters_and_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))



@st.cache_data(ttl=86400*7)
def _load_conversations(_mode="load", _conversation=None, key=None):
    if _conversation is None and key is None:
        return None
    if _mode == "save":
        return _conversation
    if _mode == "load":
        st.warning(f"分享链接已失效 key = {key}")
    return None
