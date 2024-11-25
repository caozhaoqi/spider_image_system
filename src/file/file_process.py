import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from model.ImageModel import ImageModel
from run import constants
from utils.http_utils import image_url_re, match_img_result
from utils.time_utils import time_to_utc
from loguru import logger
from model import SpiderKeywordModel


@logger.catch
def scan_directory(path: str) -> List[str]:
    """Scan directory for video files"""
    video_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(('.mp4', '.avi')):
                video_files.append(os.path.join(root, file))
    return video_files


@logger.catch
def scan_directory_zip_txt(path: str) -> List[str]:
    """Scan directory for zip txt files"""
    zip_txt_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.txt') and "_zip" in file:
                zip_txt_files.append(os.path.join(root, file))
    return zip_txt_files


@logger.catch
def scan_directory_zip(path: str) -> List[str]:
    """Scan directory for zip files"""
    zip_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.zip'):
                zip_files.append(os.path.join(root, file))
    return zip_files


@logger.catch
def count_lines(filename: str) -> int:
    """Count lines in text file"""
    with open(filename, 'r', encoding='utf-8', errors='replace') as file:
        return sum(1 for _ in file)


@logger.catch
def write_error_image(txt_path: str, image_path: str, filename: str) -> bool:
    """Write failed image download data to txt"""
    keyword = match_img_result(filename)
    error_file = os.path.join(txt_path, "download_fail_image.txt")
    with open(error_file, 'a', encoding='utf-8', errors='replace') as f:
        f.write(f"{image_path},{keyword}\n")
    return True


@logger.catch
def record_end_download_image(file_name: str, data: ImageModel) -> bool:
    """Record last download data"""
    with open(file_name, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(data.__dict__, f, ensure_ascii=False)
    return True


@logger.catch
def look_end_download_image(file_name: str) -> Optional[dict]:
    """Read last download record"""
    if not os.path.exists(file_name):
        logger.warning("Image record json data file not found!")
        return None
    
    with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
        return json.load(f)


@logger.catch
def read_end_download_image() -> Tuple[Optional[ImageModel], Optional[str], Optional[str], Optional[int], Optional[bool]]:
    """Get last download message"""
    download_final_flag = look_end_download_image(os.path.join(constants.data_path, "download_final_image.json"))
    
    if download_final_flag:
        model = ImageModel(
            download_final_flag['image_index'],
            download_final_flag['txt_name'],
            download_final_flag['image_url'],
            download_final_flag['image_name'],
            download_final_flag['download_date'],
            download_final_flag['txt_index'],
            download_final_flag['continue_flag']
        )
        return (
            model,
            model.txt_name,
            model.image_url,
            model.txt_index,
            model.continue_flag
        )
    return None, None, None, None, None


@logger.catch
def save_download_end(index: int, file_path: str, url: str, cdds_index: int) -> None:
    """Save download end data"""
    data = ImageModel(
        index, file_path, url,
        image_url_re(url),
        time_to_utc(time.time()),
        cdds_index, True
    )
    record_end_download_image(os.path.join(constants.data_path, "download_final_image.json"), data)
    logger.warning(f"Set stop image flag True! URL: {data.image_url}, txt: {file_path}")


@logger.catch
def update_download_continue_flag() -> None:
    """Update download continue flag"""
    data = ImageModel(None, None, None, None,
                     time_to_utc(time.time()), None, False)
    record_end_download_image(os.path.join(constants.data_path, "download_final_image.json"), data)
    logger.info("Download final image json continue_flag updated")


@logger.catch
def record_download_finish_txt(content: str) -> bool:
    """Record completed downloads"""
    if exists_txt_from_finish(content):
        return True
        
    file_name = os.path.join(constants.data_path, "download_finished_txt.txt")
    with open(file_name, 'a', encoding='utf-8', errors='replace') as f:
        f.write(f"{content}\n")
    logger.success(f"Download {content} finished")
    return True


@logger.catch
def exists_txt_from_finish(content: str) -> bool:
    """Check if download is already completed"""
    file_name = os.path.join(constants.data_path, "download_finished_txt.txt")
    
    if not os.path.exists(file_name):
        Path(file_name).write_text("", encoding='utf-8')
        return False
        
    with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
        if any(content in line for line in f):
            logger.warning(f"{content} already downloaded, skipping")
            return True
    return False


@logger.catch
def record_end_spider_image_keyword(key_word: str, cur_page: int) -> bool:
    """Record end spider image keyword"""
    spider_image_keyword, txt_file_list = get_image_keyword()
    cur_keyword_txt = find_keyword_txt(key_word, txt_file_list, spider_image_keyword)
    
    if cur_keyword_txt:
        data = SpiderKeywordModel(cur_keyword_txt, key_word, cur_page, True)
        file_name = os.path.join(constants.data_path, 'spider_img_keyword_final.json')
        with open(file_name, 'w', encoding='utf-8', errors='replace') as f:
            json.dump(data.__dict__, f, ensure_ascii=False)
        logger.success("Spider stopped, end keyword written")
        return True
    
    logger.warning("New keyword! txt not saved")
    return False


@logger.catch
def get_image_keyword() -> Tuple[List[str], List[str]]:
    """Get image keyword list"""
    auto_spider_path = os.path.join(constants.data_path, "auto_spider_img")
    os.makedirs(auto_spider_path, exist_ok=True)

    txt_files = [f for f in Path(auto_spider_path).rglob('*spider_img_keyword.txt')]
    
    default_file = os.path.join(auto_spider_path, 'spider_img_keyword.txt')
    if not os.path.exists(default_file):
        Path(default_file).touch()
        logger.warning(f"Created default file: {default_file}")

    if not txt_files:
        logger.warning("No spider_img_keyword txt files found")
        return [], []

    try:
        keywords = []
        for txt in txt_files:
            with open(txt, 'r', encoding='utf-8', errors='replace') as f:
                keywords.append(f.readlines())
        return keywords, [str(p) for p in txt_files]
    except Exception as e:
        logger.error(f"Error reading keywords: {e}")
        return [], []


@logger.catch
def find_keyword_txt(key_word: str, txt_file_list: List[str], spider_image_keyword: List[str]) -> Optional[str]:
    """Find keyword in txt files"""
    for txt_file in txt_file_list:
        with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
            if any(key_word in line for line in f):
                return txt_file
    return None


@logger.catch
def record_finish_keyword(keyword: str, cur_page: int) -> None:
    """Record finished spider keyword and page"""
    file_name = os.path.join(constants.data_path, "spider_finished_keyword.txt")
    content = f"{keyword},{cur_page}"

    if not os.path.exists(file_name):
        Path(file_name).write_text("", encoding='utf-8')
        return

    with open(file_name, "a", encoding='utf-8', errors='replace') as f:
        f.write(f"{content}\n")
    logger.success(f"Recorded finish: keyword={keyword}, page={cur_page}")


@logger.catch
def keyword_times(keyword: str, cur_page: int) -> int:
    """Count keyword occurrences"""
    file_name = os.path.join(constants.data_path, "spider_finished_keyword.txt")
    content = f"{keyword},{cur_page}"

    if not os.path.exists(file_name):
        Path(file_name).write_text("", encoding='utf-8')
        return 0

    with open(file_name, "r", encoding='utf-8', errors='replace') as f:
        return sum(1 for line in f if content in line)


@logger.catch
def exists_image_keyword(key_word: str) -> Tuple[bool, int]:
    """Check if image keyword exists"""
    file_name = os.path.join(constants.data_path, 'spider_finished_keyword.txt')
    
    try:
        if not os.path.exists(file_name):
            return False, 0
            
        pages = []
        with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                word, page = line.strip().split(',')
                if key_word in word:
                    pages.append(int(page))
                    
        return bool(pages), max(pages) if pages else 0
        
    except Exception as e:
        return False, 0
