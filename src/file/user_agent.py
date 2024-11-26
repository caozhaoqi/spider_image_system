"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

# 配置文件路径
INI_PATH = os.path.join(os.getcwd(), 'config')
AGENT_FILE_PATH = os.path.join(INI_PATH, 'user-agent.txt')

# 默认User-Agent列表
DEFAULT_USER_AGENTS = [
    # Chrome Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    
    # Chrome Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    
    # Firefox Linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
    
    # Safari iOS
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1',
    
    # Edge Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/18.18362',
    
    # Chrome Windows Alternative
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    
    # Chrome Mac Alternative
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    
    # Firefox Linux Alternative
    'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
]


@logger.catch
def create_agent_init(file_path: str) -> None:
    """
    创建并初始化User-Agent文件
    
    Args:
        file_path: User-Agent文件路径
    """
    os.makedirs(INI_PATH, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write('\n'.join(DEFAULT_USER_AGENTS))
        
    logger.success("User agent file created successfully!")


@logger.catch
def read_user_agent() -> List[str]:
    """
    读取User-Agent列表
    
    Returns:
        List[str]: User-Agent字符串列表
    """
    if not os.path.exists(AGENT_FILE_PATH):
        create_agent_init(AGENT_FILE_PATH)
        
    with open(AGENT_FILE_PATH, 'r', encoding='utf-8', errors='replace') as f:
        return [line.strip() for line in f if line.strip()]
