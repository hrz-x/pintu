import os
import dashscope
from openai import OpenAI
from http import HTTPStatus
from dashscope import VideoSynthesis

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

def sample_call_i2v():
    # call sync api, will return the result
    print('please wait...')
    rsp = VideoSynthesis.call(model='wanx2.1-i2v-turbo',
                              prompt='一只猫在草地上奔跑',
                              img_url='https://cdn.translate.alibaba.com/r/wanx-demo-1.png')
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output.video_url)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


client = OpenAI(
    # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

completion = client.chat.completions.create(
    model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
    messages=[
        {'role': 'user', 'content': '9.9和9.11谁大'}
    ]
)

# 通过reasoning_content字段打印思考过程
print("思考过程：")
print(completion.choices[0].message.reasoning_content)

# 通过content字段打印最终答案
print("最终答案：")
print(completion.choices[0].message.content)


if __name__ == '__main__':
    pass
    # sample_call_i2v()