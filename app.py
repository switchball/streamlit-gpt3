import time
import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="GPT-3 Playground", layout="wide", initial_sidebar_state="auto",
)

st.title("GPT-3 你问我答")
st.info('✨ 支持多轮对话 😉')
st.text("在下方文本框输入你的对话 \n点击发送后，稍等片刻，就会收到来自 GPT-3 的回复")

# store chat as session state
DEFAULT_CHAT_TEXT = "Human: Who are you?"
if 'input_text_state' not in st.session_state:
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT

def after_submit():
    # Send text and waiting for respond
    with st.spinner('Runing ...'):
        time.sleep(2)
        st.write('Sentiment:', st.session_state.input_text_state)
        st.session_state.input_text_state += '\nAI: <Respond>'
        st.session_state.input_text_state += '\nHuman: '

if st.button('Reset'):
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT
    
with st.form("my_form"):
    # Every form must have a submit button.
    submitted = st.form_submit_button("发送")
    if submitted:
        after_submit()
    
    # When the input_text_state is bind to widget, its content cannot be modified by session api.
    txt = st.text_area('对话内容', key='input_text_state')
    temperature_val = st.slider("Temperature")
    checkbox_val = st.checkbox("Form checkbox")
    if submitted:
        st.write("temperature", temperature_val, "checkbox", checkbox_val, 'text', txt)

"""---"""
