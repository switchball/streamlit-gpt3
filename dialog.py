import streamlit as st
from typing import Any, Optional, Union

ALL_AVATAR_STYLES = [ 
    "adventurer", 
    "adventurer-neutral", 
    "avataaars",
    "big-ears",
    "big-ears-neutral",
    "big-smile",
    "bottts", 
    "croodles",
    "croodles-neutral",
    "female",
    "gridy",
    "human",
    "identicon",
    "initials",
    "jdenticon",
    "male",
    "micah",
    "miniavs",
    "pixel-art",
    "pixel-art-neutral",
    "personas",
]


def message(msg: str,
            is_user: Optional[bool] = False, 
            avatar_style: Optional[str] = None,
            seed: Optional[Union[int, str]] = 42,
            key: Optional[str] = None,
            on_click = None):
    """
    Creates a new instance of streamlit-chat component

    Parameters
    ----------
    msg: str
        The message to be displayed in the component
    is_user: bool 
        if the sender of the message is user, if `True` will align the 
        message to right, default is False.
    avatar_style: Literal or None
        The style for the avatar of the sender of message, default is bottts
        for not user, and identicon for user.
        st-chat uses https://avatars.dicebear.com/styles for the avatar
    seed: int or str
        The seed for choosing the avatar to be used, default is 42.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    on_click: WidgetCallback
        Callback function when message button is clicked

    Returns: None
    """
    if not avatar_style:
        avatar_style = "lorelei" if is_user else "bottts"
    
    if is_user:
        col_icon, col_text, col_action, _ = st.columns((1, 10, 1.5, 2))
    else:
        _, col_action, col_text, col_icon = st.columns((2, 1.5, 10, 1))
    col_icon.markdown(f"""<img src="https://api.dicebear.com/5.x/{avatar_style}/svg?seed={seed}" alt="avatar" style="max-height: 2rem;"/>""", unsafe_allow_html=True)
    if len(msg) <= 5:
        col_text.text_input("Message", msg, key=key, disabled=True, label_visibility='collapsed')
    else:
        col_text.markdown(msg)
    if is_user:
        if on_click:
            col_action.form_submit_button("✏️", on_click=on_click)     # edit
    else:
        if on_click:
            col_action.form_submit_button("↩️", on_click=on_click, help='撤回当前消息，可编辑后重新发送')     # revoke
