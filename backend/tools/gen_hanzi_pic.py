"""
我希望你实现一个python代码，输入某个汉字，和字体，输出png图片
"""

from PIL import Image, ImageDraw, ImageFont
import traceback
import json
import os

def generate_hanzi_image(hanzi, font_path, output_path="output.png", size=200, bg_color="white", text_color="black", transparent=False):
    """
    生成汉字图片
    
    参数:
        hanzi (str): 要生成的汉字
        font_path (str): 字体文件路径 (.ttf/.otf)
        output_path (str): 输出图片路径
        size (int): 图片尺寸（正方形）
        bg_color (str): 背景颜色
        text_color (str): 文字颜色
    """
    try:
        # 创建空白图片
        if transparent:
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # 透明背景
        else:
            img = Image.new("RGB", (size, size), bg_color)  # 白色背景
        draw = ImageDraw.Draw(img)
        
        # 加载字体（自动调整字体大小）
        font_size = int(size * 0.8)
        font = ImageFont.truetype(font_path, font_size)
        
        # 计算文字位置（居中） - 使用 textbbox 替代 textsize
        bbox = draw.textbbox((0, 0), hanzi, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        
        # 绘制文字
        draw.text(position, hanzi, fill=text_color, font=font)
        
        # 保存图片
        img.save(output_path)
        print(f"图片已生成: {os.path.abspath(output_path)}")
        return True
    
    except Exception as e:
        # 打印错误信息
        print("生成汉字图片时发生错误:")
        traceback.print_exc()
        print(f"生成失败: {e}")
        return False

# 示例使用
if __name__ == "__main__":
    
    fronts_dir = './data/fronts'
    fronts = {
        '行楷': f'{fronts_dir}/STXINGKA.TTF',
        '宋体': f'{fronts_dir}/simsun.ttc',
        '黑体': f'{fronts_dir}/simhei.ttf',
        '楷体': f'{fronts_dir}/simkai.ttf',
        '仿宋': f'{fronts_dir}/simfang.ttf',
        '隶书': f'{fronts_dir}/simli.ttf',
        '华文彩云': f'{fronts_dir}/STCAIYUN.TTF',
    }

    hanzi = json.load(open('data/hanzi.json', 'r', encoding='utf-8'))

    for font, font_file in fronts.items():
        if not os.path.exists(f'data/hanzi_pic/{font}'):
            os.makedirs(f'data/hanzi_pic/{font}')   
        # for zi in list(hanzi.keys()):
        zi = '雨'
        generate_hanzi_image(zi, font_file, f'data/hanzi_pic/{font}/{zi}.jpg', size=720, text_color="black", transparent=False)
        generate_hanzi_image(zi, font_file, f'data/hanzi_pic/{font}/{zi}.png', size=720, text_color="black", transparent=True)

