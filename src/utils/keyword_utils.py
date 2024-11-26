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

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from pypinyin import lazy_pinyin, Style
from run import constants


@logger.catch
def exists_keyword_finish_txt(keyword: str) -> bool:
    """检查并删除下载完成文件中的关键词
    
    Args:
        keyword: 要检查的关键词
        
    Returns:
        bool: 关键词是否存在并已删除
    """
    # 转换关键词为拼音
    keyword_pinyin = ''.join(lazy_pinyin(keyword, style=Style.TONE3))
    txt_keyword = f"{keyword_pinyin}_img.txt"
    
    # 获取文件路径
    file_path = Path(constants.data_path) / "download_finished_txt.txt"
    
    try:
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8', errors='replace').splitlines()
        
        # 检查关键词是否存在
        if any(txt_keyword in line for line in content):
            # 过滤掉包含关键词的行
            filtered_content = [line for line in content if txt_keyword not in line]
            
            # 写回文件
            file_path.write_text('\n'.join(filtered_content) + '\n', 
                               encoding='utf-8', errors='replace')
                               
            logger.debug(f"已从download_finish_txt.txt删除关键词: {txt_keyword}")
            return True
            
        logger.info(f"在download_finish_txt.txt中未找到关键词: {keyword}")
        return False
        
    except Exception as e:
        logger.warning(f"读取文件失败: {e}")
        return False
