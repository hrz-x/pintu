import json
import os
from http import HTTPStatus
from io import BytesIO
from typing import List, Optional

import cv2
import dashscope
import numpy as np
import requests
from dashscope import ImageSynthesis, VideoSynthesis
from openai import OpenAI
from PIL import Image

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def wanx_i2v(pic_describe: str, img_url: str):
    # call sync api, will return the result
    print("please wait...")
    rsp = VideoSynthesis.call(
        model="wanx2.1-i2v-turbo", prompt=pic_describe, img_url=img_url
    )
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output.video_url)
    else:
        print(
            "Failed, status_code: %s, code: %s, message: %s"
            % (rsp.status_code, rsp.code, rsp.message)
        )


def wanx_t2i(pic_describe: str, img_url: str) -> str | None:

    print("----sync call, please wait a moment----")
    rsp = ImageSynthesis.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # type: ignore
        model=ImageSynthesis.Models.wanx_v1,
        prompt=pic_describe,
        n=1,
        style="<auto>",
        size="1024*1024",
        ref_mode="repaint",
        ref_strength=0.5,
        ref_img=img_url,
    )
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
        if not rsp.output.results or not rsp.output.results[0].url:
            return None
        return rsp.output.results[0].url
    else:
        print(
            "sync_call Failed, status_code: %s, code: %s, message: %s"
            % (rsp.status_code, rsp.code, rsp.message)
        )
        raise Exception(f"Error: {rsp.status_code}, {rsp.code}, {rsp.message}")


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


prompt = """你是一个生成提示词的Agent，你的输出会被另外一个图像生成的AI作为输入

我现在的工作是输入一个汉字图片，生成一张图片，完成从这个汉字到一个符合这个汉字的图片的转换，从而体现出象形文字的魅力。
现在，你拿到的汉字是“{zi}”这个字，原始的文字是{font}的。
我需要你给我一段图片的描述，可以很好地符合“{zi}”这个字的字义表达，同时，你需要发挥出你的想象，对“{zi}”进行拆解，把每个部分加上符合这个部分的特点，同时不破坏整体画面的美感。生成的图片以卡通、水墨、虚幻风格为主。

现在，请给出你的回答，不要回答无关的内容，你的输出将会被作为另外一个AI的输入
"""

prompt_v2 = "请以“{zi}”字展开一副画像，描述画面内容。"

prompt_v3 = (
    "请以“{zi}”字展开一副画像，描述画面内容，画面主体应当为“{zi}”，增加适当的修饰元素。"
)


def convert_to_browser_friendly(input_path, output_path):
    import subprocess

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-c:v",
        "libx264",
        "-profile:v",
        "main",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-crf",
        "23",
        output_path,
    ]
    subprocess.run(cmd, check=True)


def create_fade_video(
    img_urls: List[str],
    output_path: str = "output_video.mp4",
    fps: int = 30,
    hold_seconds: float = 1.0,
    transition_seconds: float = 0.5,
    temp_dir: str = "temp_frames",
    proxy: Optional[str] = None,
) -> str:
    """
    将图片URL列表生成带淡入淡出效果的视频

    参数:
        img_urls: 图片URL列表
        output_path: 输出视频路径（默认MP4格式）
        fps: 视频帧率（默认30帧/秒）
        hold_seconds: 每张图片静态展示时长（秒）
        transition_seconds: 过渡效果时长（秒）
        temp_dir: 临时存储下载图片的目录
        proxy: 代理设置（例如 "http://proxy.example.com:8080"）

    返回:
        生成的视频文件路径
    """
    # 创建临时目录
    os.makedirs(temp_dir, exist_ok=True)

    # 设置代理（如果需要）
    session = requests.Session()
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}

    def download_image(url: str) -> np.ndarray:
        """下载图片并转换为OpenCV格式"""
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise RuntimeError(f"下载图片失败: {url} | 错误: {str(e)}")

    def add_fade_frames(
        video_writer: cv2.VideoWriter,
        img1: np.ndarray,
        img2: np.ndarray,
        transition_frame_count: int,
    ):
        """生成淡入淡出过渡帧"""
        for i in range(transition_frame_count):
            alpha = i / transition_frame_count
            blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
            video_writer.write(blended)

    try:
        # 1. 下载所有图片并检查尺寸一致性
        print("正在下载图片...")
        images = []
        base_size = None
        for i, url in enumerate(img_urls):
            img = download_image(url)
            if base_size is None:
                base_size = (img.shape[1], img.shape[0])  # (width, height)
            elif (img.shape[1], img.shape[0]) != base_size:
                img = cv2.resize(img, base_size)
            images.append(img)
            print(f"已下载 {i+1}/{len(img_urls)}: {url}")

        # 2. 计算帧数
        hold_frames = int(fps * hold_seconds)
        transition_frames = int(fps * transition_seconds)

        # 3. 创建视频写入器
        # 修改视频写入部分
        fourcc = cv2.VideoWriter_fourcc(*"avc1")  # 改为 H.264 编码 # type: ignore
        video = cv2.VideoWriter(output_path, fourcc, fps, base_size)  # type: ignore

        if not video.isOpened():
            # 如果 H.264 不可用，尝试其他编码
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore
            video = cv2.VideoWriter(output_path, fourcc, fps, base_size)  # type: ignore
            if not video.isOpened():
                raise RuntimeError("无法创建视频文件，请检查输出路径和编码器")

        # 4. 生成视频内容
        print("正在生成视频...")
        for i in range(len(images)):
            # 写入静态帧
            for _ in range(hold_frames):
                video.write(images[i])

            # 如果不是最后一张图片，添加过渡效果
            if i < len(images) - 1:
                add_fade_frames(video, images[i], images[i + 1], transition_frames)

        # 5. 释放资源
        video.release()

        # 6. 验证输出文件
        if not os.path.exists(output_path):
            raise RuntimeError("视频文件生成失败")
            # 如果使用 mp4v 编码，可以添加后续转换步骤
        if fourcc == cv2.VideoWriter_fourcc(*"mp4v"):  # type: ignore
            temp_path = output_path.replace(".mp4", "_temp.mp4")
            os.rename(output_path, temp_path)
            convert_to_browser_friendly(temp_path, output_path)
            os.remove(temp_path)

        return output_path

    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)


def gen_hanzi_video(zi: str, font: str = "仿宋"):
    pic_describe = qa(prompt_v2.format(zi=zi, font=font))
    img_url = f"http://101.43.128.24:8000/hanzi_pic/{font}/{zi}_outline.jpg"
    urls = [img_url]
    for step in range(10):
        img_url = wanx_t2i(pic_describe=pic_describe, img_url=img_url)
        if not img_url:
            break
        urls.append(img_url)
        print(f"第{step+1}步生成的图片：{img_url}")

    # IPython.embed()
    if len(urls) < 2:
        print("生成的图片数量不足，无法创建视频")
        return
    output_video_path = create_fade_video(
        img_urls=urls,
        output_path=f"./data/hanzi_video/{zi}_{font}_video.mp4",
        fps=60,
        hold_seconds=0.0,
        transition_seconds=0.8,
        temp_dir="temp_frames",
    )
    print(f"视频已生成: {output_video_path}")


if __name__ == "__main__":

    # pic_describe = qa(prompt.format(zi='雨', font='仿宋'))
    # wanx_i2v(pic_describe=pic_describe, img_url='http://101.43.128.24:8000/hanzi_pic/仿宋/雨_outline.jpg')

    for font, zi, _ in json.load(open("./data/final.json")):
        if os.path.exists(f"./data/hanzi_video/{zi}_{font}_video.mp4"):
            print(f"视频已存在: {zi}_{font}_video.mp4")
            continue
        gen_hanzi_video(zi=zi, font=font)
