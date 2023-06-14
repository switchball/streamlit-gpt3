import time
import random
import openai
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.common_resource import get_tokenizer


from prompt import PROMPTS, get_prompt_by_preset_id, get_suggestion_by_preset_id, get_description_by_preset_id
from collect import TokenCounter
from dialog import message
from share import generate_share_link, restore_from_share_link
from image import conversation2png


openai.api_key = st.secrets["OPENAI_API_KEY"]


st.set_page_config(
    page_title="GPT-3 Playground", layout="wide", initial_sidebar_state="auto",
)

st_tiltle_slot = st.empty()
st_tiltle_slot.title("GPT-3 你问我答")
st.markdown("""[![GitHub][github_badge]][github_link]\n\n[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label\n[github_link]: https://github.com/switchball/streamlit-gpt3""")
st_desc_solt = st.empty()
st_desc_solt.text("在下方文本框输入你的对话 ✨ 支持多轮对话 😉 \n点击 \"💬\" 后，稍等片刻，就会收到来自 GPT-3 的回复")

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


def wait(delay, reason=""):
    if delay <= 50:
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
    presence_penalty=0.6,
    stream=False
    ):
    """ Chat completion """
    with st.spinner(text=random.choice(HINT_TEXTS)):
        response = openai.ChatCompletion.create(
            model=model, messages=message_list, temperature=temperature, max_tokens=max_tokens, top_p=top_p, 
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty, stream=stream
        )
    if stream:
        reply_msg = ""
        finish_reason = ""

        # streaming chat with editable slot
        reply_edit_slot = st.empty()
        for chunk in response:
            c = chunk['choices'][0]
            delta = c.get('delta', {}).get('content', '')
            finish_reason = c.get('finish_reason', '')
            reply_msg += delta
            reply_edit_slot.markdown(reply_msg)
        reply_edit_slot.markdown("")

        # calculate message tokens
        txt = "".join(m["content"] for m in message_list)
        input_tokens = len(get_tokenizer().tokenize(txt))
        completion_tokens = len(get_tokenizer().tokenize(reply_msg))

        # mock response
        response = {
            'choices': [{
                'message': {
                    'content': reply_msg,
                    'role': 'assistant'
                },
                'finish_reason': finish_reason
            }],
            'usage': {
                'total_tokens': input_tokens + completion_tokens
            }
        }
        return response
    else:
        return response

# Available Models
LANGUAGE_MODELS = ['gpt-3.5-turbo', 'text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
CODEX_MODELS = ['code-davinci-002', 'code-cushman-001']

HINT_TEXTS = ['正在接通电源，请稍等 ...', '正在思考怎么回答，不要着急', '正在努力查询字典内容 ...', '等待对方回复中 ...', '正在激活神经网络 ...', '请稍等']
TOKEN_SAVING_HINT_THRESHOLD = 2000

# store chat as session state
DEFAULT_CHAT_TEXT = "以下是与AI助手的对话。助手乐于助人、有创意、聪明而且非常友好。\n\n"

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


class ConversationCompressConfig:
    def __init__(self, *, enabled, max_human_conv_reserve_count=None, max_robot_conv_reserve_count=None, enable_first_conv=None) -> None:
        self.enabled = enabled
        self.max_human_conv_reserve_count = max_human_conv_reserve_count
        self.max_robot_conv_reserve_count = max_robot_conv_reserve_count
        self.enable_first_conv = enable_first_conv
    
    def get_message_list(self):
        if self.enabled:
            return self._get_compressed_message_list()
        else:
            return self._get_full_message_list()
    
    @property
    def message_tokens(self):
        if self.enabled:
            return self.compressed_message_tokens
        else:
            return self.full_message_tokens
    
    @property
    def full_message_tokens(self):
        ms = self._get_full_message_list()
        txt = "".join(m["content"] for m in ms)
        tokens = get_tokenizer().tokenize(txt)
        return len(tokens)
    
    @property
    def compressed_message_tokens(self):
        ms = self._get_compressed_message_list()
        txt = "".join(m["content"] for m in ms)
        tokens = get_tokenizer().tokenize(txt)
        return len(tokens)

    def _get_full_message_list(self):
        """ Get full message list (for Chat Completion) """
        message_list = []
        # Add system prompt
        if st.session_state['prompt_system']:
            message_list.append({"role": "system", "content": st.session_state["prompt_system"]})
        # Add history conversations
        for conv_user, conv_robot in zip(st.session_state['conv_user'], st.session_state['conv_robot']):
            message_list.append({"role": "user", "content": conv_user})
            message_list.append({"role": "assistant", "content": conv_robot})
        return message_list

    def _get_compressed_message_list(self):
        """ Get compressed message list (for Chat Completion) """
        message_list = []
        # Add system prompt
        if st.session_state['prompt_system']:
            message_list.append({"role": "system", "content": st.session_state["prompt_system"]})
        # Add history conversations but compressed
        turns_count = min(len(st.session_state['conv_user']), len(st.session_state['conv_robot']))
        for turn_idx in range(turns_count):
            should_keep_human = False   # should keep human conversations at this turn
            should_keep_robot = False   # should keep robot conversations at this turn
            if turn_idx == 0 and self.enable_first_conv:
                should_keep_human, should_keep_robot = True, True
            if turn_idx + self.max_human_conv_reserve_count >= turns_count:
                should_keep_human = True
            if turn_idx + self.max_robot_conv_reserve_count >= turns_count:
                should_keep_robot = True
            # Add conversations to message_list
            if should_keep_human or should_keep_robot:
                conv_user = st.session_state['conv_user'][turn_idx] if should_keep_human else ""
                conv_robot = st.session_state['conv_robot'][turn_idx] if should_keep_robot else ""
                message_list.append({"role": "user", "content": conv_user})
                message_list.append({"role": "assistant", "content": conv_robot})
            
        return message_list

def after_submit(current_input, model, temperature, max_tokens, cc_config: ConversationCompressConfig, stream=False):
    # Append current_input to input_text_state
    st.session_state.input_text_state += current_input

    # Queue by prompt length and max_tokens
    if 'gpt' in model:
        token_number = cc_config.message_tokens
    else:
        token_number = len(get_tokenizer().tokenize(st.session_state.input_text_state))
    x = token_number / 1024
    delay = 2 * x * x - 3
    delay += 2 * x * (max_tokens / 1024 - 1)
    wait(delay, "前方排队中...")

    # Send text and waiting for respond
    if 'gpt' in model:
        # Get system prompt + history conversations
        message_list = cc_config.get_message_list()
        # Add current user input
        message_list.append({"role": "user", "content": current_input})
        response = chat_completion(
            message_list=message_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stream=stream
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
        # TODO: non chat model also need stream function
        answer = response['choices'][0]['text']
        # TODO: should check if answer starts with '\nAI:'
        st.session_state.input_text_state += answer
        st.session_state.input_text_state += '\nHuman: '

    print(answer)
    # Collect usage
    tc = get_token_counter()
    tc.collect(tokens=response['usage']['total_tokens'])
    return response, answer


def load_preset_id_from_url_link():
    """ Load preset if it is provided in url link """
    query = st.experimental_get_query_params()
    preset_id = query.get("preset", [""])[0]
    if preset_id:
        for p in PROMPTS:
            if preset_id == p['preset']:
                return preset_id
    return None

def load_preset_qa(candidate=None):
    """ Load default preset Q&A """
    preset = st.session_state.get("preset", candidate or 'GPT-3 你问我答 (ChatBot)')
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


def show_conversation_dialog(slot_list, rollback_fn, reverse_order=False):
    """ Render the conversation dialogs """
    just_loaded_from_share = False
    if 'loaded_from_share' in st.session_state and st.session_state['loaded_from_share']:
        just_loaded_from_share = True
        st.session_state['loaded_from_share'] = False
    if not slot_list:
        reverse_order = True
    if st.session_state.conv_robot:
        num = len(st.session_state.conv_robot)
        # From user0, robot0, ..., user_{n-1}, robot_{n-1} in normal order
        order_indexes = reversed(range(2*num)) if reverse_order else range(2*num)
        for j in order_indexes:
            slot = st.empty() if reverse_order else slot_list[j]
            with slot:
                is_user = j % 2 == 0
                text = st.session_state['conv_user'][j//2] if is_user else st.session_state["conv_robot"][j//2]
                message(text, is_user=is_user, key=str(j), seed=seed, on_click=(rollback_fn if j == 2 * num - 1 else None))
            if just_loaded_from_share:
                time.sleep(1)
                
def show_edit_dialog(slot):
    """ Show dialog that edits AI answer """
    with slot:
        if len(st.session_state["conv_robot"]) > 0:
            with st.expander("⭐ 手动编辑上一次AI回复的内容", expanded=True):
                with st.form("edit_form"):
                    # 加载上一次AI回复的内容
                    st.session_state['edit_answer'] = st.session_state["conv_robot"][-1]
                    st.form_submit_button("📝 确认修改", on_click=edit_answer)
                    st.text_area('对话内容', key='edit_answer', height=800)
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


# 恢复 / 保存
restore_from_share_link()

st.sidebar.title("✨ GPT Interface")
with st.sidebar.expander('🎈 预设身份的提示词 (Preset Prompts)', expanded=False):
    preset_id_options = [p["preset"] for p in PROMPTS]
    preset_id_options.append("自定义")
    if 'preset' not in st.session_state:
        load_preset_qa(candidate=load_preset_id_from_url_link())
    prompt_id = st.selectbox('预设身份的提示词', options=preset_id_options, index=0, on_change=load_preset_qa, key="preset", label_visibility="collapsed")
    # 动态更改标题和说明
    st_tiltle_slot.title(prompt_id)
    if get_description_by_preset_id(prompt_id) is not None:
        st_desc_solt.text(get_description_by_preset_id(prompt_id))
    _prompt_text = get_prompt_by_preset_id(prompt_id)
    prompt_text = st.text_area("Enter Prompt", value=_prompt_text, placeholder='预设的Prompt', 
                                label_visibility='collapsed', key='prompt_system', disabled=(_prompt_text != ''))
    _suggestion = get_suggestion_by_preset_id(prompt_id)
    if _suggestion:
        st.warning(_suggestion, icon="⚠️")
    st.session_state.input_text_state = prompt_text
    append_to_input_text()

edit_answer_slot = st.empty()

# 对话保留设置
with st.sidebar.expander('⭐ 对话设置'):
    enbale_conv_reserve = st.checkbox("开启对话压缩", value=False, help="若开启，仅会发送对话中的特定部分作为上下文\n\n若关闭，所有聊天内容都会作为上下文发送")
    if enbale_conv_reserve:
        max_robot_conv_reserve_count = st.number_input(':hash: 仅保留最近AI回复对话数', 0, None, 3, help="设定最多保留多少次 AI 最近的回复内容")
        max_human_conv_reserve_count = st.number_input(':hash: 仅保留最近输入对话数', 0, None, 10, help="设定最多保留多少次最近输入的提问内容")
        enable_first_conv = st.checkbox('必定保留第一轮对话', help="推荐在第一轮对话包含特殊设定时开启")

        cc_config = ConversationCompressConfig(
            enabled=True,
            max_human_conv_reserve_count=max_human_conv_reserve_count,
            max_robot_conv_reserve_count=max_robot_conv_reserve_count,
            enable_first_conv=enable_first_conv)
        full_tokens = cc_config.full_message_tokens
        active_tokens = cc_config.compressed_message_tokens
        st.caption(f"预估压缩前/后： `{active_tokens}`/ `{full_tokens}` tokens")
    else:
        cc_config = ConversationCompressConfig(enabled=False)
    enable_reverse_order = st.checkbox("对话倒序显示", value=False, help="开启后，输入框在上方，最近的对话在最上方\n\n关闭后，输入框在下方，最早的对话在上方")
    enable_stream_chat = st.checkbox("对话流式显示", value=True, help="开启后，以流式方式传输对话，无需等待")

if st.session_state['input_text_state'] and not enbale_conv_reserve:
    tokens = get_tokenizer().tokenize(st.session_state['input_text_state'])
    if len(tokens) > TOKEN_SAVING_HINT_THRESHOLD:
        st.sidebar.info(f"👆 全文 Token 数 >= {TOKEN_SAVING_HINT_THRESHOLD}，可考虑开启对话压缩功能")


with st.form("my_form"):
    dialog_slot_list = None if enable_reverse_order else [st.empty() for _ in range(2 + 2 * len(st.session_state['conv_user']))]
    col_icon, col_text, col_btn = st.columns((1, 10, 2))
    col_icon.markdown(f"""<img src="https://api.dicebear.com/5.x/{"lorelei"}/svg?seed={seed}" alt="avatar" />""", unsafe_allow_html=True)
    input_text = col_text.text_input("You: ", "", key="input", label_visibility="collapsed")

    with st.sidebar.expander('🧩 模型参数 (Model Parameters)'):
        model_val = st.selectbox("Model", options=LANGUAGE_MODELS, index=0)
        temperature_val = st.slider("Temperature", 0.0, 2.0, 0.9, step=0.05)
        max_tokens_val = st.select_slider("Max Tokens", options=(256, 512, 1024), value=512) 
    # Every form must have a submit button.
    submitted = col_btn.form_submit_button("💬")
    if submitted:
        response, answer = after_submit(input_text, model_val, temperature_val, max_tokens_val, cc_config, stream=enable_stream_chat)
        st.session_state.conv_user.append(input_text)
        st.session_state.conv_robot.append(answer)
        finish_reason = response['choices'][0].get('finish_reason', '')
        if finish_reason == 'length':
            st.sidebar.info("👆 上次输入因长度被截断，可考虑撤回该消息，并调大该参数后重试")
    
    show_conversation_dialog(dialog_slot_list, rollback_fn=rollback, reverse_order=enable_reverse_order)

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

need_edit_answer = st.sidebar.button("🔬 编辑AI的回答（高级功能）")
if need_edit_answer:
    show_edit_dialog(slot=edit_answer_slot)
    
# 恢复 / 保存
if st.sidebar.button("🔗 生成分享链接"):
    share_link = generate_share_link()
    st.sidebar.success(f"链接已生成 [右键复制]({share_link}) 有效期7天")

is_generate_image = st.sidebar.button("🖼️ 生成分享图片", key="image_button")
if is_generate_image:
    image = conversation2png(st.session_state['preset'], st.session_state['conv_user'], st.session_state['conv_robot'], seed=seed)
    st.image(image, caption='已生成图片，长按或右键保存')

"""---"""

with st.expander("访问统计"):
    pv_stats, call_stats, token_stats = get_token_counter().summary()

    tab1, tab2, tab3 = st.tabs(["Session View", "Request Count", "Token Count"])
    df = pd.DataFrame(pv_stats.items(), columns=['time', 'pv'])
    fig = px.line(df, x="time", y="pv", title='Page View')
    tab1.plotly_chart(fig)
    tab2.write(call_stats)
    tab3.write(token_stats)
