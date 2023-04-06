# coding=utf8
# LLM Wrapper
import requests
import json

class RemoteLLM:
    def __init__(self, model_end_point) -> None:
        self.model_end_point = model_end_point

    def completion(self, input_text, **kwargs):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = '{ "input": "" }'
        data = {
            "input": f"TL;dr 总结这段话：{input_text} 上文总结：",
            "config": kwargs
        }

        response = requests.post(self.model_end_point, headers=headers, data=json.dumps(data))
        print(response.status_code)
        result =  response.json()
        # success if result['code'] == 0
        return result

    def summary(self):
        pass


# RemoteLLM(prompts).summary