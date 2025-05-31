"""
我希望你实现一个python代码，输入某个汉字，和字体，输出png图片
"""

from PIL import Image, ImageDraw, ImageFont
import traceback
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageColor
import traceback
import os
import math
 
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
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # type: ignore
        else:
            img = Image.new("RGB", (size, size), bg_color)  # type: ignore
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
    
def generate_outline(input_pic: str, output_pic: str, 
                          outline_color: str = "black", 
                          outline_width: int = 5,
                          dash_length: int = 10,
                          gap_length: int = 5):
    """
    为输入图片添加虚线轮廓线并保存为输出图片
    
    参数:
        input_pic (str): 输入图片路径
        output_pic (str): 输出图片路径
        outline_color (str): 轮廓线颜色
        outline_width (int): 轮廓线宽度
        dash_length (int): 虚线每段长度
        gap_length (int): 虚线间隔长度
    """
    try:
        # 打开原始图片
        img = Image.open(input_pic)
        
        # 转换为RGBA模式以便处理透明度
        if img.mode != 'RGBA':
            # 对于非透明图片，我们假设黑色文字在白色背景上
            img = img.convert('RGBA')
            datas = img.getdata()
            
            new_data = []
            for item in datas:
                # 将非白色像素改为黑色全透明
                if item[0] < 50 and item[1] < 50 and item[2] < 50:  # 认为是文字部分
                    new_data.append((0, 0, 0, 255))  # 黑色不透明
                else:
                    new_data.append((255, 255, 255, 0))  # 白色全透明
            img.putdata(new_data)
        
        # 获取原始图像的alpha通道
        original_alpha = img.split()[3]
        
        # 对alpha通道进行膨胀操作来创建轮廓
        alpha = original_alpha.copy()
        for _ in range(outline_width):
            alpha = alpha.filter(ImageFilter.MaxFilter(3))
        
        # 创建轮廓alpha通道
        outline_alpha = ImageChops.subtract(alpha, original_alpha)
        
        # 创建虚线轮廓图像
        outline = Image.new('RGBA', img.size, (0, 0, 0, 0)) # type: ignore
        draw = ImageDraw.Draw(outline)
        
        # 获取轮廓的边界框
        bbox = outline_alpha.getbbox()
        if not bbox:
            print("警告: 未检测到轮廓")
            outline.save(output_pic)
            return False
        
        # 创建虚线模式
        pattern = []
        for _ in range(dash_length):
            pattern.append(255)  # 虚线部分
        for _ in range(gap_length):
            pattern.append(0)    # 间隔部分
        
        # 在整个图像范围内应用虚线模式
        width, height = img.size
        for y in range(bbox[1], bbox[3]):
            for x in range(bbox[0], bbox[2]):
                if outline_alpha.getpixel((x, y)) > 0:
                    # 计算当前像素在虚线模式中的位置
                    pos = (x + y) % (dash_length + gap_length)
                    if pos < dash_length:
                        outline.putpixel((x, y), (*ImageColor.getrgb(outline_color), 255))
        
        # 保存结果
        if output_pic.endswith('.png'):
            outline.save(output_pic)
        else:
            background = Image.new('RGB', outline.size, (255, 255, 255)) # type: ignore
            background.paste(outline, mask=outline.split()[3])  # 用Alpha通道混合
            background.save(output_pic)
        print(f"虚线轮廓图片已生成: {os.path.abspath(output_pic)}")
        return True
    
    except Exception as e:
        print("生成虚线轮廓时发生错误:")
        traceback.print_exc()
        print(f"生成失败: {e}")
        return False
    
# 示例使用
if __name__ == "__main__":
    
    fonts_dir = './data/fonts'
    fonts = {
        '行楷': f'{fonts_dir}/STXINGKA.TTF',
        '宋体': f'{fonts_dir}/SIMSUN.TTC',
        '黑体': f'{fonts_dir}/SIMHEI.TTF',
        '楷体': f'{fonts_dir}/SIMKAI.TTF',
        '仿宋': f'{fonts_dir}/SIMFANG.TTF',
        '隶书': f'{fonts_dir}/SIMLI.TTF',
        # '华文彩云': f'{fronts_dir}/STCAIYUN.TTF',
    }

    hanzi = json.load(open('data/hanzi.json', 'r', encoding='utf-8'))

    for font, font_file in fonts.items():
        if not os.path.exists(f'data/hanzi_pic/{font}'):
            os.makedirs(f'data/hanzi_pic/{font}')   
        for zi in list(hanzi.keys()):
            generate_hanzi_image(zi, font_file, f'data/hanzi_pic/{font}/{zi}.jpg', size=720, text_color="black", transparent=False)
            generate_hanzi_image(zi, font_file, f'data/hanzi_pic/{font}/{zi}.png', size=720, text_color="black", transparent=True)
            generate_outline(f'data/hanzi_pic/{font}/{zi}.png', f'data/hanzi_pic/{font}/{zi}_outline.jpg', outline_color="black", outline_width=1, dash_length=20, gap_length=0)