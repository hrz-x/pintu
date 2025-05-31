"""
请用python实现以下功能
输入为png格式的图片，基本上只有黑色或白色（透明）像素
我需要你将其中所有黑色连通区域提取出来，将连通块保存为透明图片，存到新建文件夹下，同时保存一个json文件，用来指示连通块中心相对于原图中心的偏移
"""


import os
import json
import numpy as np
from PIL import Image
from skimage.measure import label, regionprops
from skimage.morphology import binary_erosion, binary_dilation, disk

def extract_connected_components(input_path, output_folder, erosion_radius=5, dilation_radius=None):
    """
    通过形态学操作断开薄弱连接后提取连通区域
    
    参数:
        input_path: 输入图片路径
        output_folder: 输出文件夹
        erosion_radius: 腐蚀操作的半径(像素)
        dilation_radius: 膨胀操作的半径(如为None则等于erosion_radius)
    """
    if dilation_radius is None:
        dilation_radius = erosion_radius
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 打开原始图像并转换为RGBA模式
    try:
        original_img = Image.open(input_path).convert('RGBA')
    except Exception as e:
        print(f"无法打开图像文件: {e}")
        return None
    
    original_width, original_height = original_img.size
    original_center = np.array([original_width / 2, original_height / 2])
    
    # 转换为numpy数组进行处理
    img_array = np.array(original_img)
    
    # 创建二值图像（黑色为1，其他为0）
    is_black = np.all(img_array[:, :, :3] == [0, 0, 0], axis=2)
    is_opaque = img_array[:, :, 3] > 0
    binary = (is_black & is_opaque).astype(np.uint8)
    
    # 形态学操作断开薄弱连接
    footprint = disk(erosion_radius)  # 创建圆形结构元素
    
    try:
        eroded = binary_erosion(binary, footprint=footprint)  # 先腐蚀断开连接
        footprint = disk(dilation_radius)
        dilated = binary_dilation(eroded, footprint=footprint)  # 再膨胀恢复大致形状
    except Exception as e:
        print(f"形态学操作出错: {e}")
        return None
    
    # 标记连通区域
    labeled = label(dilated)
    regions = regionprops(labeled)
    
    # 准备存储结果
    result_data = {
        "original_size": {"width": original_width, "height": original_height},
        "original_center": {"x": original_center[0], "y": original_center[1]},
        "morphology_params": {
            "erosion_radius": erosion_radius,
            "dilation_radius": dilation_radius
        },
        "components": []
    }
    
    # 为每个连通区域创建图像(使用原始图像中的像素)
    component_index = 0
    for region in regions:
        component_index += 1
        
        # 创建透明背景的图像
        component_img = Image.new('RGBA', (original_width, original_height), (0, 0, 0, 0)) # type: ignore
        component_pixels = component_img.load()
        
        # 获取连通区域的坐标(使用处理后的区域标记)
        min_row, min_col, max_row, max_col = region.bbox
        for y in range(min_row, max_row):
            for x in range(min_col, max_col):
                if labeled[y, x] == region.label and binary[y, x]:  # 只保留原始图像中的黑色像素 # type: ignore
                    component_pixels[x, y] = (0, 0, 0, 255) # type: ignore
        
        # 裁剪图像到最小尺寸
        bbox = component_img.getbbox()
        if bbox:
            cropped_img = component_img.crop(bbox)
            output_filename = f"component_{component_index}.png"
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                cropped_img.save(output_path, format='PNG')
            except Exception as e:
                print(f"无法保存组件 {component_index}: {e}")
                continue
            
            # 计算连通区域的中心坐标
            center_y, center_x = region.centroid
            center_offset = [round(center_x - original_center[0], 2), 
                            round(center_y - original_center[1], 2)]
            
            # 存储组件信息
            component_info = {
                "filename": output_filename,
                "offset_from_center": center_offset,
                "area": region.area,
                "size": {
                    "width": cropped_img.width,
                    "height": cropped_img.height
                },
                "bbox": {
                    "x": min_col,
                    "y": min_row,
                    "width": max_col - min_col,
                    "height": max_row - min_row
                }
            }
            result_data["components"].append(component_info)
    
    # 保存JSON文件
    json_path = os.path.join(output_folder, "components_info.json")
    try:
        with open(json_path, 'w') as f:
            json.dump(result_data, f, indent=4)
    except Exception as e:
        print(f"无法保存JSON文件: {e}")
        return None
    
    print(f"提取完成，共找到 {component_index} 个连通区域")
    print(f"形态学参数: 腐蚀半径={erosion_radius}, 膨胀半径={dilation_radius}")
    return result_data

# 使用示例
if __name__ == "__main__":
    input_image = "/home/ubuntu/pintu/data/hanzi_pic/仿宋/雨.png"  # 替换为你的输入图片路径
    output_dir = "/home/ubuntu/pintu/data/hanzi_splited/仿宋/雨"  # 输出文件夹
    
    extract_connected_components(input_image, output_dir)
    print(f"处理完成，结果已保存到 {output_dir} 文件夹")
