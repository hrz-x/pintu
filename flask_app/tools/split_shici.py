"""
请用python实现以下功能
输入为png格式的图片，基本上只有黑色或白色（透明）像素
我需要你将其中所有黑色连通区域提取出来，将连通块保存为透明图片，存到新建文件夹下，同时保存一个json文件，用来指示连通块中心相对于原图中心的偏移
"""

import json

from split_hanzi import extract_connected_components

# 使用示例
if __name__ == "__main__":

    shici = json.load(open("./data/shici_available.json", "r", encoding="utf-8"))
    for sc in shici:
        input_image = f"./data/shici_pics/{sc['title']}_{sc['author']}.png"  # 替换为你的输入图片路径
        output_dir = f"./data/shici_splited/{sc['title']}_{sc['author']}"  # 输出文件夹

        result = extract_connected_components(input_image, output_dir, erosion_radius=0)
        print(f"处理诗歌《{sc['title']}》完成，结果保存在 {output_dir}。")
