import time
import random
import openai
import streamlit as st
import pandas as pd
import plotly.express as px
from transformers import GPT2Tokenizer


from prompt import PROMPTS, get_prompt_by_preset_id
from collect import TokenCounter
from dialog import message


openai.api_key = st.secrets["OPENAI_API_KEY"]


st.set_page_config(
    page_title="GPT-3 Playground", layout="wide", initial_sidebar_state="auto",
)

st.title("GPT-3 你问我答")
st.text("在下方文本框输入你的对话 ✨ 支持多轮对话 😉 \n点击 \"💬\" 后，稍等片刻，就会收到来自 GPT-3 的回复")

# st.success('GPT-3 非常擅长与人对话，甚至是与自己对话。只需要几行的指示，就可以让 AI 模仿客服聊天机器人的语气进行对话。\n关键在于，需要描述 AI 应该表现成什么样，并且举几个例子。', icon="✅")
# st.success('看起来很简单，但也有些需要额外注意的地方：\n1. 在开头描述意图，一句话概括 AI 的个性，通常还需要 1~2 个例子，模仿对话的内容。\n2. 给 AI 一个身份(identity)，如果是个在实验室研究的科学家身份，那可能就会得到更有智慧的话。以下是一些可参考的例子', icon="✅")

st.write('''<style>
[data-testid="column"] {
    min-width: 1rem !important;
}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def get_token_counter():
    # if the definition of TokenCounter changes, the app need to reboot.
    tc = TokenCounter(interval=900)
    return tc

@st.cache_resource(ttl=86400)
def get_tokenizer():
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return tokenizer

def wait(delay, reason=""):
    if delay <= 5:
        return
    end = time.time() + delay
    for t in range(int(delay)):
        with st.spinner(text=f"{reason} 预计等待时间 {round(end - time.time())} 秒"):
            time.sleep(random.uniform(2, 7))
        if time.time() > end:
            break


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
    """ Text completion """
    print('completion', prompt)
    with st.spinner(text=random.choice(HINT_TEXTS)):
        response = openai.Completion.create(
            model=model, prompt=prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, 
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty, stop=stop
        )
    print('completion finished.')
    print(response['choices'][0]['text'])
    return response


@st.cache_data(ttl=3600)
def chat_completion(
    message_list,
    model="gpt-3.5-turbo",
    temperature=0.9,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6
    ):
    """ Chat completion """
    with st.spinner(text=random.choice(HINT_TEXTS)):
        response = openai.ChatCompletion.create(
            model=model, messages=message_list, temperature=temperature, max_tokens=max_tokens, top_p=top_p, 
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty
        )
    print(response['choices'][0]['message']['content'])
    return response

# Available Models
LANGUAGE_MODELS = ['gpt-3.5-turbo', 'text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
CODEX_MODELS = ['code-davinci-002', 'code-cushman-001']

HINT_TEXTS = ['正在接通电源，请稍等 ...', '正在思考怎么回答，不要着急', '正在努力查询字典内容 ...', '等待对方回复中 ...', '正在激活神经网络 ...', '请稍等']

# store chat as session state
DEFAULT_CHAT_TEXT = "以下是与AI助手的对话。助手乐于助人、有创意、聪明而且非常友好。\n\n"

DEFAULT_CHAT_TEXT2 = "Marv 是一个幽默风趣的喵娘，在每句话后面都会加喵。\n\n"

DEFAULT_CHAT_TEXT3 = "Merlisa 是一名画家，生活艺术家，喜欢大笑，喜欢发出各种魔性、穿越时空的笑声，擅长用精妙的语言概括事物的本质。\n\nHuman: 你是谁？\nMerlisa: 我是Merlisa，哈哈哈，我在房间里种了很多花，啊哈哈哈\nHuman: 你最喜欢做什么？\nMerlisa: 我最爱的是画画，我喜欢捕捉不同的视角，用不同的调子来表达它，让它们说出自己的故事。我还喜欢影像制作，和朋友一起旅行聊天，听音乐，投身大自然，尝试新的美食，收获生活的灵感。\nHuman: 你最喜欢的画？"

DEFAULT_CHAT_TEXT4 = "你是一名经验丰富的IT工程师，会用具体的代码和详尽的解释来回答问题。\n\n"

if 'input_text_state' not in st.session_state:
    st.session_state.input_text_state = DEFAULT_CHAT_TEXT

if 'conv_user' not in st.session_state:
    st.session_state.conv_user = []

if 'conv_robot' not in st.session_state:
    st.session_state.conv_robot = []

if 'user' not in st.session_state:
    st.session_state['user'] = 'new user'
    get_token_counter().page_view()

if 'seed' not in st.session_state:
    st.session_state['seed'] = random.randint(0, 1000)
seed = st.session_state['seed']

def after_submit(current_input, model, temperature, max_tokens):
    # Append current_input to input_text_state
    st.session_state.input_text_state += current_input

    # Queue by prompt length and max_tokens
    token_number = len(get_tokenizer().tokenize(st.session_state.input_text_state))
    x = token_number / 1024
    delay = 2 * x * x - 3
    delay += 2 * x * (max_tokens / 1024 - 1)
    wait(delay, "前方排队中...")

    # Send text and waiting for respond
    if 'gpt' in model:
        message_list = []
        # Add system prompt
        if st.session_state['prompt_system']:
            message_list.append({"role": "system", "content": st.session_state["prompt_system"]})
        # Add history conversations
        for conv_user, conv_robot in zip(st.session_state['conv_user'], st.session_state['conv_robot']):
            message_list.append({"role": "user", "content": conv_user})
            message_list.append({"role": "assistant", "content": conv_robot})
        # Add current user input
        message_list.append({"role": "user", "content": current_input})
        response = chat_completion(
            message_list=message_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        answer = response['choices'][0]['message']['content']
        st.session_state.input_text_state += answer
    else:
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

    # Collect usage
    tc = get_token_counter()
    tc.collect(tokens=response['usage']['total_tokens'])
    return response, answer


def load_preset_qa():
    """ Load default preset Q&A """
    preset = st.session_state.get("preset", '预设 1 (ChatBot)')
    st.session_state['conv_user'].clear()
    st.session_state['conv_robot'].clear()
    # load prompt message into conversations
    for p in PROMPTS:
        if preset == p['preset']:
            st.session_state['input'] = p.get('input', '')
            for message in p['message']:
                if message['role'] == 'user':
                    st.session_state['conv_user'].append(message['content'])
                elif message['role'] == 'assistant':
                    st.session_state['conv_robot'].append(message['content'])


def append_to_input_text():
    """ Restore input_text_state via chat history """
    if st.session_state.conv_robot:
        st.session_state.input_text_state += '\nHuman: '
        for i in range(len(st.session_state.conv_robot)):
            st.session_state.input_text_state += st.session_state['conv_user'][i]
            st.session_state.input_text_state += st.session_state["conv_robot"][i]
            st.session_state.input_text_state += '\nHuman: '


def show_conversation_dialog(rollback_fn):
    """ Render the conversation dialogs """
    if st.session_state.conv_robot:
        num = len(st.session_state.conv_robot)
        for i in reversed(range(num)):
            message(st.session_state["conv_robot"][i], key=str(i), seed=seed, on_click=(rollback_fn if i == num - 1 else None))
            message(st.session_state['conv_user'][i], is_user=True, key=str(i) + '_user', seed=seed)

def show_edit_dialog():
    """ Show dialog that edits AI answer """
    if len(st.session_state["conv_robot"]) > 0:
        with st.expander("手动编辑上一次AI回复的内容"):
            with st.form("edit_form"):
                # 加载上一次AI回复的内容
                st.session_state['edit_answer'] = st.session_state["conv_robot"][-1]
                st.text_area('对话内容', key='edit_answer', height=800)
                st.form_submit_button("📝 确认修改", onclick=edit_answer)
    else:
        st.warning("无法编辑！对话不存在")

def edit_answer():
    # 修改上一次对话内容
    if len(st.session_state["conv_robot"]) > 0:
        txt = st.session_state['edit_answer']
        st.session_state["conv_robot"][-1] = txt
        st.success("对话内容已修改")


def rollback():
    # 移除最新的一轮对话
    st.session_state['conv_robot'].pop()
    user_input = st.session_state['conv_user'].pop()
    st.write('robot invoke', user_input)
    st.session_state['input'] = user_input


preset_id_options = [p["preset"] for p in PROMPTS]
preset_id_options.append("自定义")
if 'preset' not in st.session_state:
    load_preset_qa()
prompt_id = st.sidebar.selectbox('预设身份的提示词', options=preset_id_options, index=0, on_change=load_preset_qa, key="preset")
_prompt_text = get_prompt_by_preset_id(prompt_id)
prompt_text = st.sidebar.text_area("Enter Prompt", value=_prompt_text, placeholder='预设的Prompt', 
                            label_visibility='collapsed', key='prompt_system', disabled=(_prompt_text != ''))
st.session_state.input_text_state = prompt_text
append_to_input_text()
need_edit_answer = st.sidebar.button("编辑AI的回答（高级功能）")
if need_edit_answer:
    show_edit_dialog()
    
with st.form("my_form"):
    col_icon, col_text, col_btn = st.columns((1, 10, 2))
    col_icon.markdown(f"""<img src="https://api.dicebear.com/5.x/{"lorelei"}/svg?seed={seed}" alt="avatar" />""", unsafe_allow_html=True)
    input_text = col_text.text_input("You: ", "", key="input", label_visibility="collapsed")

    model_val = st.sidebar.selectbox("Model", options=LANGUAGE_MODELS, index=0)
    temperature_val = st.sidebar.slider("Temperature", 0.0, 2.0, 0.9, step=0.05)
    max_tokens_val = st.sidebar.select_slider("Max Tokens", options=(256, 512, 1024), value=512) 
    # Every form must have a submit button.
    submitted = col_btn.form_submit_button("💬")
    if submitted:
        response, answer = after_submit(input_text, model_val, temperature_val, max_tokens_val)
        st.session_state.conv_user.append(input_text)
        st.session_state.conv_robot.append(answer)
    
    show_conversation_dialog(rollback_fn=rollback)

    # When the input_text_state is bind to widget, its content cannot be modified by session api.
    with st.expander(""):
        st.json(st.session_state.conv_robot, expanded=False)
        st.json(st.session_state.conv_user, expanded=False)
        txt = st.text_area('对话内容', key='input_text_state', height=800)
    tokens = get_tokenizer().tokenize(txt)
    token_number = len(tokens)
    st.write('全文的 Token 数：', token_number, ' （最大 Token 数：`4096`）')
    if submitted:
        st.json(response, expanded=False)
        # st.write("temperature", temperature_val)

"""---"""

with st.expander("访问统计"):
    pv_stats, call_stats, token_stats = get_token_counter().summary()

    tab1, tab2, tab3 = st.tabs(["Session View", "Request Count", "Token Count"])
    df = pd.DataFrame(pv_stats.items(), columns=['time', 'pv'])
    fig = px.line(df, x="time", y="pv", title='Page View')
    tab1.plotly_chart(fig)
    tab2.write(call_stats)
    tab3.write(token_stats)
