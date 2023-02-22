import time
import random
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

st.success('GPT-3 非常擅长与人对话，甚至是与自己对话。只需要几行的指示，就可以让 AI 模仿客服聊天机器人的语气进行对话。\n关键在于，需要描述 AI 应该表现成什么样，并且举几个例子。', icon="✅")

st.success('看起来很简单，但也有些需要额外注意的地方：\n1. 在开头描述意图，一句话概括 AI 的个性，通常还需要 1~2 个例子，模仿对话的内容。\n2. 给 AI 一个身份(identity)，如果是个在实验室研究的科学家身份，那可能就会得到更有智慧的话。以下是一些可参考的例子', icon="✅")

@st.cache_data(ttl=3600)
def completion(
        prompt, 
        model="text-davinci-003",
        temperature=0.9,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    ):
    print('completion', prompt)
    hint_texts = ['正在接通电源，请稍等 ...', '正在思考怎么回答，不要着急', '正在努力查询字典内容 ...', '等待回复中 ...', '正在激活神经网络 ...']
    with st.spinner(text=random.choice(hint_texts):
        response = openai.Completion.create(
            model=model, prompt=prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, 
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty, stop=stop
        )
    print('completion finished.')
    print(response['choices'][0]['text'])
    return response

# Available Models
LANGUAGE_MODELS = ['text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
CODEX_MODELS = ['code-davinci-002', 'code-cushman-001']

# store chat as session state
DEFAULT_CHAT_TEXT = "以下是与AI助手的对话。助手乐于助人、有创意、聪明而且非常友好。\n\nHuman: 你好，你是谁？\nAI: 我是由 OpenAI 创建的人工智能。有什么可以帮你的吗？\nHuman: "

DEFAULT_CHAT_TEXT2 = "Marv 是一个幽默风趣的喵娘，在每句话后面都会加喵。\n\nHuman: 你是谁？\nMarv: 我是个聊天机器人，叫Marv！喵~\nHuman: 你有什么爱好？\nMarv: 抱怨和生气。喵~\nHuman: 你可以来追求我吗？"

DEFAULT_CHAT_TEXT3 = "Merlisa 是一名画家，生活艺术家，喜欢大笑，喜欢发出各种魔性、穿越时空的笑声，擅长用精妙的语言概括事物的本质。\n\nHuman: 你是谁？\nMerlisa: 我是Merlisa，哈哈哈，我在房间里种了很多花，啊哈哈哈\nHuman: 你最喜欢做什么？\nMerlisa: 我最爱的是画画，我喜欢捕捉不同的视角，用不同的调子来表达它，让它们说出自己的故事。我还喜欢影像制作，和朋友一起旅行聊天，听音乐，投身大自然，尝试新的美食，收获生活的灵感。\nHuman: 你最喜欢的画？"

if 'input_text_state' not in st.session_state:
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT

def after_submit(model, temperature, max_tokens):
    # Send text and waiting for respond
    response = completion(
        model=model,
        prompt=st.session_state.input_text_state,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    answer = response['choices'][0]['text']
    # TODO: should check if answer starts with '\nAI:'
    st.session_state.input_text_state += answer
    st.session_state.input_text_state += '\nHuman: '
    return response

with st.form(key='preset_form'):
    st.write('一些预设的身份(identity)')
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.form_submit_button(label='预设 1'):
            st.session_state.input_text_state = DEFAULT_CHAT_TEXT
    with col2:
        if st.form_submit_button(label='预设 2'):
            st.session_state.input_text_state = DEFAULT_CHAT_TEXT2
    with col3:
        if st.form_submit_button(label='预设 3'):
            st.session_state.input_text_state = DEFAULT_CHAT_TEXT3
    
with st.form("my_form"):
    model_val = st.sidebar.selectbox("Model", options=LANGUAGE_MODELS, index=0)
    temperature_val = st.sidebar.slider("Temperature", 0.0, 2.0, 0.9, step=0.1)
    max_tokens_val = st.sidebar.select_slider("Max Tokens", options=(256, 512, 1024), value=256) 
    checkbox_val = st.sidebar.checkbox("Form checkbox")
    # Every form must have a submit button.
    submitted = st.form_submit_button("发送")
    if submitted:
        response = after_submit(model_val, temperature_val, max_tokens_val)
    
    # When the input_text_state is bind to widget, its content cannot be modified by session api.
    txt = st.text_area('对话内容', key='input_text_state', height=800)
    if submitted:
        st.json(response, expanded=False)
        st.write("temperature", temperature_val, "checkbox", checkbox_val)

"""---"""
