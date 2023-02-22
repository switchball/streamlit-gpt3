import time
import openai
import streamlit as st
import pandas as pd

openai.api_key = st.secrets["OPENAI_API_KEY"]


st.set_page_config(
    page_title="GPT-3 Playground", layout="wide", initial_sidebar_state="auto",
)

st.title("GPT-3 你问我答")
st.info('✨ 支持多轮对话 😉')
st.text("在下方文本框输入你的对话 \n点击发送后，稍等片刻，就会收到来自 GPT-3 的回复")

@st.cache_data
def completion(
        prompt, 
        model="text-davinci-003",
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    ):
    print('completion', prompt)
    with st.spinner('Running...'):
        response = openai.Completion.create(
            model=model, prompt=prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, 
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty, stop=stop
        )
    print('completion finished.')
    print(response['choices'][0]['text'])
    return response


# store chat as session state
DEFAULT_CHAT_TEXT = "以下是与AI助手的对话。助手乐于助人、有创意、聪明而且非常友好。\n\nHuman: 你好，你是谁？\nAI: 我是由 OpenAI 创建的人工智能。有什么可以帮你的吗？\nHuman: "
if 'input_text_state' not in st.session_state:
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT

def after_submit():
    # Send text and waiting for respond
    response = completion(
        model="text-davinci-003",
        prompt=st.session_state.input_text_state,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    answer = response['choices'][0]['text']
    st.session_state.input_text_state += '\nAI: ' + answer
    st.session_state.input_text_state += '\nHuman: '
    return response

if st.button('Reset'):
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT
    
with st.form("my_form"):
    # Every form must have a submit button.
    submitted = st.form_submit_button("发送")
    if submitted:
        response = after_submit()
        st.write(response)
    
    # When the input_text_state is bind to widget, its content cannot be modified by session api.
    txt = st.text_area('对话内容', key='input_text_state', height=800)
    temperature_val = st.slider("Temperature")
    checkbox_val = st.checkbox("Form checkbox")
    if submitted:
        st.write("temperature", temperature_val, "checkbox", checkbox_val, 'text', txt)

"""---"""
