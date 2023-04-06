# Read Article from WeChat

# Here is a Python code that can scrape articles from a WeChat public account and return the title and content of the article.

import streamlit as st
import requests
import math
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from utils.remote_llm import RemoteLLM

MODEL_END_POINT = st.secrets["MODEL_END_POINT"]

enable_feature = st.experimental_get_query_params().get("feature", None)
if enable_feature is None or enable_feature[0] == "0":
    st.warning("该功能正在内测中 ... 敬请期待 ...")
    st.stop()

# 遍历 content 内部的所有标签，输出每个标签的内容
def traverse(element, level=0, file=None, suffix=""):
    # Set suffix = "\n" to save one paragraph to one line
    # NOTE: auto detect is more helpful
    for child in element.children:
        if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            file.write("\n" + "#" * int(child.name[1:]) + " " + child.get_text() + " " + suffix)
        elif child.name in ('p', 'span') and child.get_text().strip():
            file.write(child.get_text() + suffix)
        elif child.name == 'blockquote':
            file.write("> " + child.get_text() + suffix)
        elif child.name in ('section', 'body'):
            traverse(child, level+1, file)


def get_wechat_article(url, mode="simple"):
    headers = {
        'authority': 'mp.weixin.qq.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': 'pgv_pvid=1671376372258898; pgv_info=ssid=s1676372252078899; rewardsn=; wxtokenkey=777; wwapp.vid=; wwapp.cst=; wwapp.deviceid=; pac_uid=0_c4389ea7df8a1; ua_id=gJg4qg8cQpPkI9EfAAAAAIsLmLsCl4-U1_dIZ_VSF9M=; wxuin=76776862684849; uuid=2d4bf4f402427e3d1420f31c4d34852f; xid=506520fe2d89a0dfebec1da6fa33858c; mm_lang=zh_CN; ptui_loginuin=348988792; RK=dUWpQ/vZe8; ptcz=af8c4396797d39d05f3f87cf61e40f6eeb4186c4882654ede0e74c3e267d0932; skey=@B6Wq9TTyU; uin=o348988792; wedrive_uin=1688850523224148; wedrive_sid=AFRrWAD4U1YGg05CACc2YwAA; wedrive_sids=1688850523224148&AFRrWAD4U1YGg05CACc2YwAA; wedrive_skey=1688850523224148&c801ed3af1acc734f97529cf7b383368; wedrive_ticket=1688850523224148&CAESIMBDOqQ03uWl0BE7Ch4r5qssvqj1wsEO-AJiHjceff_R; xm_disk_vid=1688850523224148; xm_disk_corp_id=1970325010981265',
        'if-modified-since': 'Fri, 17 Mar 2023 23:47:25 +0800',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content.decode("utf8"), 'html.parser')
    title = soup.find('h1', {'class': 'rich_media_title'}).text.strip()
    content = soup.find('div', {'class': 'rich_media_content'})
    if mode == 'simple':
        content_text = content.text.strip()
    else:
        with NamedTemporaryFile(mode="w+", delete=True) as temp_file:
            traverse(content, file=temp_file)
            temp_file.seek(0)
            print(temp_file.name)
            content_text = temp_file.read()
            temp_file.close()

    return title, content_text


def test(text, temperature):
    result = RemoteLLM(MODEL_END_POINT).completion(input_text=text, temperature=temperature)
    st.markdown(result)
    

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == '__main__':
    t = st.number_input("temperature", 0.0, 1.0, value=0.01)
    url = st.text_input("Enter the URL:")
    if url.startswith("https://mp.weixin.qq.com"):
        title, content = get_wechat_article(url, mode="line")
        st.write("## " + title)
        for ctc in content.split('\n'):
            # st.markdown(ctc)
            # st.write("====>", len(ctc))
            
            if len(ctc) >= 500:
                chunk_num = math.ceil(len(ctc) / 500)
                chunk_size = math.ceil(len(ctc) / chunk_num)
                for i, c in enumerate(chunks(ctc, chunk_size)):
                    st.markdown(c)
                    st.write(i, "==>", len(c))

                    test(c, t)
                    st.markdown("\n\n---\n")

            else:
                test(ctc, t)
    else:
        st.write("URL should start with `https://mp.weixin.qq.com`")