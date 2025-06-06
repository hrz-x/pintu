import json
import os
import random
from http import HTTPStatus

import requests
from dashscope import ImageSynthesis
from openai import OpenAI


def qa(question: str) -> str:
    client = OpenAI(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv(
            "DASHSCOPE_API_KEY"
        ),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="deepseek-r1",  # 此处以 deepseek-r1 为例，可按需更换模型名称。
        messages=[{"role": "user", "content": question}],
    )

    # 通过reasoning_content字段打印思考过程
    print("思考过程：")
    print(completion.choices[0].message.reasoning_content)  # type: ignore

    # 通过content字段打印最终答案
    print("最终答案：")
    print(completion.choices[0].message.content)

    assert completion.choices[0].message.content, "请检查模型输出，确保有内容返回"
    return completion.choices[0].message.content


prompt = """
{shici}

请为上面的诗词写一段具有意境的简短现代诗，请生动一点，不超过100字，不要有多余的输出。
"""


def wanx_t2i(prompt: str, output_path: str) -> None:

    print("----sync call, please wait a moment----")
    rsp = ImageSynthesis.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # type: ignore
        model="wanx2.1-t2i-plus",
        prompt=prompt,
        n=1,
        size="1440*800",
    )
    print("response: %s" % rsp)
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in rsp.output.results:
            with open(output_path, "wb+") as f:
                f.write(requests.get(result.url).content)
    else:
        print(
            "sync_call Failed, status_code: %s, code: %s, message: %s"
            % (rsp.status_code, rsp.code, rsp.message)
        )


if __name__ == "__main__":

    shici = json.load(open("./data/shici_available.json", "r", encoding="utf-8"))

    shici_final = []
    if os.path.exists("./data/shici_final.json"):
        # 如果存在 shici_final.json，则读取已有数据
        shici_final = json.load(open("./data/shici_final.json", "r", encoding="utf-8"))
    for sc in random.sample(shici, k=100):
        if sc["title"] in [s["title"] for s in shici_final]:
            print(f"诗词 {sc['title']} 已经存在，跳过")
            continue
        print(f"正在处理诗词：{sc['title']} - {sc['author']}")
        print(sc["title"])
        print(sc["author"])
        print(sc["content"])
        comment = qa(prompt.format(shici="\n".join(sc["content"])))
        print(comment)
        wanx_t2i(comment, f'./data/shici_bg/{sc["title"]}_{sc["author"]}.png')
        sc["comment"] = comment
        shici_final.append(sc)
        json.dump(
            shici_final,
            open("./data/shici_final.json", "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2,
        )
    print("生成诗词背景图片成功，保存在 ./data/shici_bg/ 目录下")
    print("已有诗词数量：%s" % len(shici_final))
