# encoding=utf8

import streamlit as st
from typing import List

from st_click_detector import click_detector as did_click


def clickable_select(choices: List[str], label="", *, key=None, index=0, sidebar=False, css_style=None):
    """
    通过点选来单选的 Html 组件
    Params:
        choices: List[str] 选项列表
        label: str 提示文字
        key: str 存储在 st.session_state 中的唯一键值（不能重名）
        index: int 默认选中的索引
        sidebar: bool 组件是否展示在侧边栏
        css_style: css 设置选中组件的 CSS 样式

    Return:
        str 用户选择的选项名称
    """
    css_content = (
        css_style
        or """{
        display: inline-block; /* 将链接元素转换为块级元素，以便设置宽度和高度 */
        text-decoration: none; /* 去除下划线 */
        font-weight: bold; /* 加粗文字 */
        color: white; /* 将文字颜色设置为白色 */
        background-color: #FFA500; /* 设置背景颜色为亮橙色 */ /* 设置背景颜色 #f1f1f1;  */
        border-radius: 15px; /* 圆角矩形的圆角半径 */
        padding: 5px 10px; /* 设置内边距，增加一些空间 */
    }"""
    )
    if len(choices) == 0:
        return None
    label_code = f"<span>{label}</span>"
    html_code = " / ".join(
        f'<a id="idx{k}" href="javascript:void(0)">{choice}</a>'
        for k, choice in enumerate(choices)
    )
    key = key or f'clickable_select_{"_".join(choices)}'
    last_selection = st.session_state.get(key, "")
    # st.info(f'last_selection = {last_selection}')
    slot = st.sidebar.empty() if sidebar else st.empty()
    with slot:
        html = f"""<style>#{last_selection} {css_content}</style>"""
        html += label_code + html_code
        # html += f'<a href="#" id="{choice1}">{choice1}</a> / <a href="#" id="{choice2}">{choice2}</a>'
        x = did_click(html, last_selection)
    # bypass value when page is reloaded
    if x == "":
        x = last_selection
    # inject deafult value
    if x == "":
        # st.success(f"inject {index}")
        x = f"idx{index}"
    if x == last_selection:
        # st.warning('no change')
        st.session_state[key] = x
    else:
        if last_selection != "":
            st.success(f'{_cvt(choices, last_selection)} => {_cvt(choices, x)}')
        st.session_state[key] = x
        with slot:  # Re-Render
            html = f"""<style>#{x} {css_content}</style>"""
            html += label_code + html_code
            # html += f'<a href="#" id="{choice1}">{choice1}</a> / <a href="#" id="{choice2}">{choice2}</a>'
            x = did_click(html, x)  # default value passing
    # st.info('session_state=' + st.session_state[key])

    # convert index to choice
    return _cvt(choices, st.session_state[key])

def _cvt(choices, idx_str):
    idx = idx_str.replace("idx", "")
    if idx == "":
        return ""
    return choices[int(idx)]
