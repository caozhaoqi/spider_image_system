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
def read_gif_url(zip_txt_path: str, url_list: List[str]) -> bool:
    """Write GIF URLs to a text file
    
    Args:
        zip_txt_path: Path to save the URL text file
        url_list: List of URLs to write
        
    Returns:
        bool: True if successful
    """
    try:
        with open(zip_txt_path, "a", encoding='utf-8') as f:
            f.writelines(f"{url}\n" for url in url_list)
        logger.success(f"Wrote {len(url_list)} URLs to {zip_txt_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write URLs to {zip_txt_path}: {e}")
        return False
