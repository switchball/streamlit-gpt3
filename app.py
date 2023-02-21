import streamlit as st

st.set_page_config(
    page_title="GPT-3 Playground", layout="wide", initial_sidebar_state="auto",
)

st.title("GPT-3 你问我答")
st.info('✨ 支持多轮对话 😉')
st.text("在下方文本框输入你的对话 \n点击发送后，稍等片刻，就会收到来自 GPT-3 的回复")

# store chat as session state
if 'input_text_state' not in st.session_state:
    st.session_state.input_text_state = "Human: Who are you?"


with st.spinner('Runing ...'):
    time.sleep(2)
    st.write('Sentiment:', st.session_state.input_text_state)
    st.session_state.input_text_state += '\nAI: <Respond>'
    st.session_state.input_text_state += '\nHuman: '

with st.form("my_form"):
    txt = st.text_area('对话内容', key='input_text_state')
    temperature_val = st.slider("Temperature")
    checkbox_val = st.checkbox("Form checkbox")
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("temperature", temperature_val, "checkbox", checkbox_val, 'text', txt)

"""---"""
