#!/usr/bin/env python3
"""
统计采集到的图片数据及分布情况
"""

import os
import sys
from pathlib import Path

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

# 配置路径
DATA_PATH = Path('./data').resolve()
IMG_URL_PATH = DATA_PATH / 'img_url'


def count_image_urls():
    """统计每个角色的图片URL数量"""
    logger.info("开始统计图片数据...")
    
    # 检查img_url目录是否存在
    if not IMG_URL_PATH.exists():
        logger.error(f"img_url目录不存在: {IMG_URL_PATH}")
        return
    
    # 统计结果
    total_urls = 0
    role_stats = {}
    
    # 遍历所有img.txt文件
    for file_path in IMG_URL_PATH.glob('*_img.txt'):
        role_name = file_path.stem.replace('_img', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                count = len(urls)
                role_stats[role_name] = count
                total_urls += count
                logger.info(f"角色 {role_name}: {count} 个图片URL")
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {e}")
    
    # 输出统计结果
    logger.info("\n=== 图片数据统计结果 ===")
    logger.info(f"总角色数: {len(role_stats)}")
    logger.info(f"总图片URL数: {total_urls}")
    
    # 按图片数量排序
    sorted_roles = sorted(role_stats.items(), key=lambda x: x[1], reverse=True)
    
    logger.info("\n角色图片数量排名:")
    for i, (role, count) in enumerate(sorted_roles, 1):
        logger.info(f"{i}. {role}: {count}")
    
    return role_stats


if __name__ == "__main__":
    count_image_urls()
