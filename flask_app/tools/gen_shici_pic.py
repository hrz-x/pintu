import json
import os

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont


def check_font_coverage(font_path, text):
    """检查字体是否能显示所有字符"""
    try:
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        for char in text:
            if ord(char) not in cmap and char not in ["\n", "\r", "\t"]:
                return False
        return True
    except Exception as e:
        print(f"字体分析错误: {e}")
        return False


def render_poem_to_png(
    poem_lines,
    output_file,
    font_path,
    font_size=30,
    line_spacing=10,
    margin=20,
    text_color=(0, 0, 0),
    background_color=(255, 255, 255),
):
    """
    将诗歌列表渲染为行楷字体的PNG图片

    参数:
        poem_lines: 诗歌列表，每个元素是一行诗
        output_file: 输出文件路径（不含扩展名）
        font_path: 行楷字体文件路径
        font_size: 字体大小（默认30）
        line_spacing: 行间距（默认10）
        margin: 页边距（默认20）
        text_color: 文字颜色（默认黑色）
        background_color: 背景颜色（默认白色）
    """
    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"无法加载字体文件: {font_path}")
        return False

    # 计算图片尺寸
    max_line_width = 0
    total_height = 0

    # 临时创建一个绘图对象来测量文本尺寸
    temp_img = Image.new("RGB", (1, 1), background_color)
    temp_draw = ImageDraw.Draw(temp_img)

    for line in poem_lines:
        line_width = temp_draw.textlength(line, font=font)
        max_line_width = max(max_line_width, line_width)
        total_height += font_size + line_spacing

    # 调整图片尺寸（加上边距）
    img_width = int(max_line_width) + 2 * margin
    img_height = total_height + 2 * margin

    # 创建图片
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # 绘制诗歌
    y = margin
    for line in poem_lines:
        # 计算水平居中位置
        line_width = draw.textlength(line, font=font)
        x = (img_width - line_width) / 2

        draw.text((x, y), line, font=font, fill=text_color)
        y += font_size + line_spacing

    # 保存图片
    img.save(output_file + ".png")
    print(f"诗歌图片已保存到: {output_file}.png")
    return True


# 示例使用
if __name__ == "__main__":
    font_path = "data/fonts/STXINGKA.TTF"
    output_folder = "./data/shici_pics/"
    os.makedirs(output_folder, exist_ok=True)

    shici = json.load(open("./data/shici.json", "r", encoding="utf-8"))
    available_shici = []

    for sc in shici:
        # 合并所有诗句检查字体覆盖
        full_text = "\n".join(sc["content"])
        if not check_font_coverage(font_path, full_text):
            print(f"跳过诗歌《{sc['title']}》：包含行楷字体不支持的字符")
            continue

        # 尝试渲染
        output_file = os.path.join(output_folder, f"{sc['title']}_{sc['author']}")
        if render_poem_to_png(
            sc["content"],
            output_file,
            font_path,
            font_size=120,
            line_spacing=40,
            text_color=(0, 0, 0),
            background_color=(255, 255, 255),
        ):
            available_shici.append(sc)

    # 保存可渲染的诗歌
    with open("./data/shici_available.json", "w", encoding="utf-8") as f:
        json.dump(available_shici, f, ensure_ascii=False, indent=2)
    print(f"\n共处理{len(shici)}首诗歌，其中{len(available_shici)}首可用行楷完整渲染")
    print(f"可用诗歌列表已保存到: ./data/shici_available.json")
