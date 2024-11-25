import os
import sys
from pathlib import Path
from typing import List, Optional

sys.path.append(str(Path(__file__).parent.parent))

import re
from loguru import logger
from pypinyin import lazy_pinyin, Style
import shutil

from run import constants
from run.constants import data_path
from utils.http_utils import image_url_re
import run


@logger.catch
def write_url_txt(path: str, file_name: str, url: str) -> None:
    """将URL写入文本文件
    
    Args:
        path: 文件路径
        file_name: 文件名
        url: 要写入的URL
    """
    file_path = Path(path) / f"{file_name}.txt"
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "a", encoding='utf-8', errors='replace') as f:
            f.write(f"{url}\n")
    except Exception as e:
        logger.error(f"写入URL失败: {e}")


@logger.catch
def filter_exists_images(key_word: str, image_url: str, txt_name: str) -> bool:
    """过滤已存在的图片或URL
    
    Args:
        key_word: 关键词
        image_url: 图片URL
        txt_name: 文件类型(_url或_img)
        
    Returns:
        bool: URL是否已存在
    """
    if txt_name not in ('_url', '_img'):
        return False
        
    file_path = Path(data_path)
    if txt_name == '_url':
        file_path = file_path / "href_url" / f"{key_word}_url.txt"
        check_url = f"{image_url}\n"
    else:
        file_path = file_path / "img_url" / f"{key_word}_img.txt"
        check_url = f"{image_url_re(image_url)}\n"
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return check_url in f.readlines()
    except Exception:
        return False


@logger.catch
def url_list_save(key_word: str, image_urls_list: List[str]) -> bool:
    """保存URL列表到文件
    
    Args:
        key_word: 关键词
        image_urls_list: URL列表
        
    Returns:
        bool: 是否保存成功
    """
    if constants.stop_spider_url_flag:
        logger.warning("停止爬取URL,URL列表保存将退出")
        return False
        
    if not image_urls_list:
        logger.warning("没有图片URL,不保存到文件")
        return False
        
    href_path = Path(data_path) / "href_url"
    url_file = href_path / f"{key_word}_url.txt"
    result_file = href_path / f"{key_word}_result_url.txt"
    
    try:
        href_path.mkdir(parents=True, exist_ok=True)
        
        for url in image_urls_list:
            write_url_txt(str(href_path), f"{key_word}_url", url)
            
        remove_duplicates_from_txt(str(url_file), str(result_file))
        return True
        
    except Exception as e:
        logger.error(f"保存URL列表失败: {e}")
        return False


@logger.catch
def remove_duplicates_from_txt(input_file: str, output_file: str) -> None:
    """移除文本文件中的重复内容
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        input_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = set(line for line in f.readlines() if line.strip())
            
        with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
            f.writelines(lines)
            
    except Exception as e:
        logger.error(f"移除重复内容失败: {e}")


@logger.catch
def get_data_file(filename: str) -> str:
    """获取数据文件的路径
    
    Args:
        filename: 文件名
        
    Returns:
        str: 完整的文件路径
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.getcwd() if run.__compiled__ else sys._MEIPASS
    else:
        base_dir = str(Path(__file__).parent)
        
    return str(Path(base_dir) / filename)


@logger.catch
def get_all_folders(directory: str) -> List[str]:
    """获取目录下所有文件夹
    
    Args:
        directory: 目录路径
        
    Returns:
        List[str]: 文件夹名称列表
    """
    return [d for d in os.listdir(directory) 
            if os.path.isdir(os.path.join(directory, d))]


@logger.catch
def contains_special_chars(input_string: str) -> bool:
    """检查字符串是否包含特殊字符
    
    Args:
        input_string: 输入字符串
        
    Returns:
        bool: 是否包含特殊字符
    """
    pattern = r'[^\u4e00-\u9fffa-zA-Z0-9]'
    return bool(re.search(pattern, input_string))


@logger.catch
def replace_special_chars(input_string: str) -> str:
    """替换字符串中的特殊字符为下划线
    
    Args:
        input_string: 输入字符串
        
    Returns:
        str: 替换后的字符串
    """
    pattern = r'[^\u4e00-\u9fffa-zA-Z0-9]'
    return re.sub(pattern, '_', input_string)


@logger.catch
def convert_and_move_folder(folder_path: str) -> None:
    """转换并移动文件夹
    
    Args:
        folder_path: 文件夹路径
    """
    try:
        for folder in get_all_folders(folder_path):
            if contains_chinese(folder):
                pinyin_convert(folder, folder_path, folder, True)
            elif contains_special_chars(folder):
                pinyin_convert(folder, folder_path, folder, False)
                
        constants.convert_folder_name_flag = False
        logger.success("所有文件夹转换完成!")
        
    except Exception as e:
        logger.error(f"转换文件夹失败: {e}")


@logger.catch
def pinyin_convert(folder_name: str, folder_path: str, folder: str, pinyin_flag: bool) -> bool:
    """转换文件夹名称
    
    Args:
        folder_name: 文件夹名
        folder_path: 文件夹路径
        folder: 文件夹
        pinyin_flag: 是否转换为拼音
        
    Returns:
        bool: 是否转换成功
    """
    new_name = (''.join(lazy_pinyin(folder_name, style=Style.TONE3)) 
                if pinyin_flag else replace_special_chars(folder_name))
                
    new_path = Path(folder_path) / new_name
    old_path = Path(folder_path) / folder
    
    try:
        if new_path.exists():
            logger.warning(f"文件夹 '{new_name}' 已存在,移动内容到已存在的文件夹")
            move_folder_contents(str(old_path), str(new_path))
        else:
            new_path.mkdir(parents=True, exist_ok=True)
            if not old_path.exists():
                logger.warning(f"目录 {old_path} 不存在!")
                return False
                
            for item in old_path.iterdir():
                shutil.move(str(item), str(new_path))
                
            logger.success(f"文件夹 '{folder_name}' 已转换为 '{new_name}' 并成功移动")
        return True
        
    except Exception as e:
        logger.error(f"转换文件夹名称失败: {e}")
        return False


@logger.catch
def move_folder_contents(source_path: str, target_path: str) -> bool:
    """移动文件夹内容
    
    Args:
        source_path: 源路径
        target_path: 目标路径
        
    Returns:
        bool: 是否移动成功
    """
    source = Path(source_path)
    target = Path(target_path)
    
    if not source.exists():
        logger.warning(f"源文件夹不存在: {source}")
        return False
        
    try:
        target.mkdir(parents=True, exist_ok=True)
        
        for item in source.iterdir():
            dest = target / item.name
            if item.is_dir():
                dest.mkdir(exist_ok=True)
                move_folder_contents(str(item), str(dest))
            else:
                shutil.move(str(item), str(dest))
                logger.info(f"已移动文件: {item.name}")
        return True
        
    except Exception as e:
        logger.error(f"移动文件夹内容失败: {e}")
        return False


@logger.catch
def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符
    
    Args:
        text: 输入文本
        
    Returns:
        bool: 是否包含中文
    """
    return bool(re.search(r'[\u4e00-\u9fa5]', text))


@logger.catch
def find_img_result(path: str) -> Optional[str]:
    """查找图片结果文件夹
    
    Args:
        path: 文件路径
        
    Returns:
        Optional[str]: 找到的文件夹名或None
    """
    parts = Path(path).parts
    
    for part in reversed(parts):
        if "_img_result" in part:
            return part
    return None
