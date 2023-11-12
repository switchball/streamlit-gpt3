#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Reference: https://juejin.cn/post/7292781589477916726
# @Desc: { 讯飞星火大模型客户端 }
# @Date: 2023/10/19 14:56
import base64
import hashlib
import hmac
import json
import uuid
import streamlit as st
from datetime import datetime
from enum import Enum
from time import mktime
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import aiohttp
import websockets
from pydantic import BaseModel, Field


class SparkChatConfig(BaseModel):
    """星火聊天配置"""

    domain: str = Field(default="generalv2", description="api版本")
    temperature: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="取值为[0,1],默认为0.5, 核采样阈值。用于决定结果随机性，取值越高随机性越强即相同的问题得到的不同答案的可能性越高",
    )
    max_tokens: int = Field(default=2048, le=8192, ge=1, description="模型回答的tokens的最大长度")
    top_k: int = Field(default=4, le=6, ge=1, description="从k个候选中随机选择⼀个（⾮等概率）")


class SparkMessageStatus(Enum):
    """
    星火消息响应状态
    0-代表首个文本结果；1-代表中间文本结果；2-代表最后一个文本结果
    """

    FIRST_RET = 0
    MID_RET = 1
    END_RET = 2


SparkChatUsageInfo = dict


class SparkMsgInfo(BaseModel):
    """星火消息信息"""

    msg_sid: str = Field(default=uuid.uuid4().hex, description="消息id，用于唯一标识⼀条消息")
    msg_type: str = Field(default="text", description="消息类型，目前仅支持text")
    msg_content: str = Field(default="", description="消息内容")
    msg_status: SparkMessageStatus = Field(
        default=SparkMessageStatus.FIRST_RET, description="消息状态"
    )

    usage_info: Optional[SparkChatUsageInfo] = Field(default=None, description="消息使用信息")


class SparkClient:
    SERVER_URI_MAPPING = {
        "general": "ws://spark-api.xf-yun.com/v1.1/chat",
        "generalv2": "ws://spark-api.xf-yun.com/v2.1/chat",
        "generalv3": "ws://spark-api.xf-yun.com/v3.1/chat",
    }

    def __init__(
        self,
        app_id: str,
        api_secret: str,
        api_key: str,
        chat_conf: SparkChatConfig = None,
    ):
        self.app_id = app_id
        self.api_secret = api_secret
        self.api_key = api_key
        self.chat_conf = chat_conf or SparkChatConfig()
        self.server_uri = self.SERVER_URI_MAPPING[self.chat_conf.domain]
        self.answer_full_content = ""

    def build_chat_params(self, msg_context_list=None, uid: str = None):
        """构造请求参数"""
        return json.dumps(
            {
                "header": self._build_header(uid=uid),
                "parameter": self._build_parameter(),
                "payload": self._build_payload(msg_context_list),
            }
        )

    def _build_header(self, uid=None):
        return {"app_id": self.app_id, "uid": uid or uuid.uuid4().hex}

    def _build_parameter(self):
        return {
            "chat": {
                "domain": self.chat_conf.domain,
                "temperature": self.chat_conf.temperature,
                "max_tokens": self.chat_conf.max_tokens,
                "top_k": self.chat_conf.top_k,
            }
        }

    def _build_payload(self, msg_context_list: list):
        return {
            "message": {
                # 如果想获取结合上下文的回答，需要开发者每次将历史问答信息一起传给服务端，如下示例
                # 注意：text里面的所有content内容加一起的tokens需要控制在8192以内，开发者如有较长对话需求，需要适当裁剪历史信息
                "text": msg_context_list
            }
        }

    def _parse_chat_response(self, chat_resp: str) -> SparkMsgInfo:
        """解析chat响应"""
        chat_resp = json.loads(chat_resp)
        code = chat_resp["header"]["code"]
        if code != 0:
            raise ValueError(f"对话错误，{chat_resp}")

        text_list = chat_resp["payload"]["choices"]["text"]
        answer_content = text_list[0]["content"]
        self.answer_full_content += answer_content
        spark_msg_info = SparkMsgInfo()

        status = chat_resp["header"]["status"]
        sid = chat_resp["header"]["sid"]
        spark_msg_info.msg_sid = sid
        spark_msg_info.msg_status = status
        spark_msg_info.msg_content = answer_content

        if status == SparkMessageStatus.END_RET.value:
            usage_info = chat_resp["payload"]["usage"]["text"]
            spark_msg_info.usage_info = usage_info
            spark_msg_info.msg_content = self.answer_full_content
            self.answer_full_content = ""

        return spark_msg_info

    def get_sign_url(self, host=None, path=None):
        """获取鉴权后url"""
        host = host or urlparse(self.server_uri).hostname
        path = path or urlparse(self.server_uri).path

        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        # 将请求的鉴权参数组合为字典
        v = {"authorization": authorization, "date": date, "host": host}
        # 拼接鉴权参数，生成url
        sign_url = self.server_uri + "?" + urlencode(v)
        return sign_url

    async def aiohttp_chat(self, msg_context_list: list, uid: str = None):
        chat_params = self.build_chat_params(msg_context_list, uid)
        sign_url = self.get_sign_url()

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(sign_url) as ws:
                await ws.send_str(chat_params)
                async for chat_resp in ws:
                    spark_msg_info = self._parse_chat_response(chat_resp.data)
                    yield spark_msg_info

    async def achat(self, msg_context_list: list, uid: str = None):
        chat_params = self.build_chat_params(msg_context_list, uid)
        sign_url = self.get_sign_url()

        async with websockets.connect(sign_url) as ws:
            await ws.send(chat_params)
            async for chat_resp in ws:
                spark_msg_info = self._parse_chat_response(chat_resp)
                yield spark_msg_info

    # 测试中的方法，应该在基类中实现比较好
    async def chat_completion_async(self, message_list, stream=True):
        with st.spinner():
            slot = st.empty()
            async for msg_info in self.achat(message_list):
                slot.markdown(self.answer_full_content)
        return msg_info.msg_content
