"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


@logger.catch
def scan_img_txt(path: str) -> List[str]:
    """
    Scan image text files from given path and return unique image URLs
    
    Args:
        path: Directory path to scan for image text files
        
    Returns:
        List[str]: List of unique image URLs found in text files
    """
    # Find all image text files
    img_txt_files = []
    for root, _, files in os.walk(path):
        img_txt_files.extend(
            os.path.join(root, file) for file in files
            if file.endswith(('_img.txt', '_img_result.txt'))
        )

    # Read all image URLs from files
    img_urls = set()
    for img_txt in img_txt_files:
        try:
            with open(img_txt, 'r', encoding='utf-8', errors='replace') as f:
                img_urls.update(f.readlines())
        except Exception as e:
            logger.error(f"Failed to read {img_txt}: {e}")
            continue

    return list(img_urls)
