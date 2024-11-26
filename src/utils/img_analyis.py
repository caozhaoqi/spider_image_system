"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import sys
from pathlib import Path
from typing import Tuple, List

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from run import constants
from image.img_switch import find_images
from utils.http_utils import match_img_result


@logger.catch
def img_analyze_data_output_new() -> Tuple[List[str], List[int]]:
    """分析图片数据并统计各类别数量
    
    Returns:
        Tuple[List[str], List[int]]: 包含类别名称列表和对应数量列表的元组
    """
    category_counts = {}
    
    # 获取所有图片路径
    image_paths = find_images(constants.data_path)
    
    # 统计各类别数量
    for img_path in image_paths:
        category = match_img_result(img_path)
        category_counts[category] = category_counts.get(category, 0) + 1

    # 分离类别和数量
    categories = list(category_counts.keys())
    counts = list(category_counts.values())

    return categories, counts


if __name__ == '__main__':
    categories, counts = img_analyze_data_output_new()
    logger.info(f"图片类别统计:\n{dict(zip(categories, counts))}")
