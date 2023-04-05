# coding=utf8
# LLM Wrapper
import requests
import json

class RemoteLLM:
    def __init__(self, model_end_point) -> None:
        self.model_end_point = model_end_point

    def completion(self, input_text, config=None):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = '{ "input": "" }'
        data = {"input": f"TL;dr 中文总结 {input_text}"}

        response = requests.post(self.model_end_point, headers=headers, data=json.dumps(data))
        print(response.status_code)
        msg =  response.json()['msg']
        return msg.split("Assistant:")[-1]

    def summary(self):
        pass


# RemoteLLM(prompts).summary