import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
from typing import List
from loguru import logger


@logger.catch
def convert_txt(input_file_path: str, output_file_path: str) -> None:
    """将文本文件从GBK和UTF-8编码合并转换为UTF-8编码
    
    Args:
        input_file_path: 输入文件路径
        output_file_path: 输出文件路径
    """
    read_lines = []
    try:
        # 读取GBK编码内容
        with codecs.open(input_file_path, 'r', encoding='gbk', errors='replace') as file:
            read_lines = file.readlines()
            
        # 读取UTF-8编码内容
        with codecs.open(input_file_path, 'r', encoding='utf-8', errors='replace') as file:
            read_lines.extend(file.readlines())
            
        # 写入合并后的UTF-8文件
        with codecs.open(output_file_path, 'w', encoding='utf-8', errors='replace') as cleaned_file:
            cleaned_file.writelines(read_lines)
            
        logger.debug(f"文件清理完成: {output_file_path}")
            
    except Exception as e:
        logger.error(f"文件转换出错: {e}")


@logger.catch
def scan_txt_file_all(path: str) -> None:
    """扫描目录下所有txt文件并转换编码
    
    Args:
        path: 要扫描的目录路径
    """
    for txt_file in scan_txt(path):
        file_path_front, file_name = os.path.split(txt_file)
        file_name_front, _ = os.path.splitext(file_name)
        output_file_path = os.path.join(file_path_front, f"{file_name_front}_utf8.txt")
        convert_txt(txt_file, output_file_path)


@logger.catch
def scan_txt(path: str) -> List[str]:
    """扫描指定目录下的特定txt文件
    
    Args:
        path: 要扫描的目录路径
        
    Returns:
        包含所有匹配txt文件路径的列表
    """
    txt_files = []
    target_suffixes = ('Spider_finished_keyword.txt', 'download_finished_txt.txt')
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(target_suffixes):
                txt_files.append(os.path.join(root, file))
                
    return txt_files
