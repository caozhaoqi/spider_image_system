"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, List

import requests
from loguru import logger

from image.img_switch import find_images
from run import constants


@logger.catch
def detect_img_py_v1(img_path: str) -> Optional[str]:
    """使用Python服务器进行图片检测分类
    
    Args:
        img_path: 图片路径
        
    Returns:
        Optional[str]: 检测结果和分数,失败返回None
    """
    url = f"http://{constants.proxy_server_ip}:{constants.proxy_server_port}/detect"
    result_server = "Default response"
    
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            result = response.json()
            result_server = result
            
            if result['code'] == 200:
                score = result['score']
                categories = ['porn', 'drawings', 'hentai', 'neutral', 'sexy']
                max_score = max(score[cat] for cat in categories)
                
                for category in categories:
                    if score[category] == max_score:
                        move_detect_img(img_path, category)
                        return f"{category}: {max_score}"
                        
                move_detect_img(img_path, "other")
                return f"other: {max_score}"
                
            logger.warning(f"Unknown error, server result: {result_server}, detail: {img_path}, skipped.")
            return None
            
    except Exception as e:
        logger.warning(f"Unknown error, server result: {result_server}, detail: {e}, error image_path: {img_path}, skipped.")
        return None


@logger.catch
def detect_img_py_local(img_path: str) -> None:
    """使用本地API进行图片检测
    
    Args:
        img_path: 图片路径
    """
    user_id = "q52O3c1717064554705xtiQBlHfRQ"
    key_api = "68V6BNlZRnMKB61717064554705xvLYwelki0"
    link_https = "https://luckycola.com.cn/tools/checkImg"
    
    try:
        with open(img_path, 'rb') as file:
            files = {'file': ('file.jpg', file, 'image/jpeg')}
            response = requests.post(link_https, files=files)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                logger.info("Upload successful: %s", data)
            else:
                logger.error("Upload failed with code %s: %s", data.get("code"), 
                           data.get("message", "No message provided"))
        else:
            logger.error("Request failed with status code %s", response.status_code)
            
    except Exception as e:
        logger.error("Upload failed: %s", e)


SAFE_CONTENT = ['Drawing', 'Neutral']

IMG_TYPE_MAP = {
    "Drawing": '艺术性的',
    "Neutral": '中性的', 
    "Sexy": '性感的',
    "Porn": '色情的',
    "Hentai": '变态的',
}


@logger.catch
def model_detect_img_java_v1(img_path: str) -> Optional[str]:
    """使用Java服务器进行图片检测分类
    
    Args:
        img_path: 图片路径
        
    Returns:
        Optional[str]: 检测结果和分数,失败返回None
    """
    url = f"http://{constants.dmi_api_server}/check"
    result_server = "Default response"
    
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            result = response.json()
            result_server = result
            
            if result['code'] == 200:
                score = result['score']
                categories = ['porn', 'drawings', 'hentai', 'neutral', 'sexy']
                max_score = max(score[cat] for cat in categories)
                
                for category in categories:
                    if score[category] == max_score:
                        move_detect_img(img_path, category)
                        return f"{category}: {max_score}"
                        
                move_detect_img(img_path, "other")
                return f"other: {max_score}"
                
            logger.warning(f"Unknown error, server result: {result_server}, detail: {img_path}, skipped.")
            return None
            
    except Exception as e:
        logger.warning(f"Unknown error, server result: {result_server}, detail: {e}, error image_path: {img_path}, skipped.")
        return None


@logger.catch
def move_detect_img(img_path: str, folder_name: str) -> bool:
    """移动检测后的图片到对应分类文件夹
    
    Args:
        img_path: 图片路径
        folder_name: 目标文件夹名
        
    Returns:
        bool: 是否移动成功
    """
    path = Path(img_path)
    target_dir = path.parent / folder_name
    target_dir.mkdir(exist_ok=True)
    
    try:
        txt_file = path.parent / f'{folder_name}_image_txt.txt'
        with open(txt_file, 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"{img_path}\n")
            
        shutil.move(img_path, target_dir / path.name)
        return True
        
    except Exception:
        return False


@logger.catch
def all_img_detect(path: str) -> None:
    """检测目录下所有图片
    
    Args:
        path: 图片目录路径
    """
    img_list = find_images(path)
    count = len(img_list)
    
    for i, img_path in enumerate(img_list, 1):
        if any(cat in img_path for cat in ['porn', 'sexy', 'other', 'neutral', 'drawings', 'hentai']):
            continue
            
        if constants.detect_img_model == "python":
            ret = detect_img_py_v1(img_path)
        else:
            ret = model_detect_img_java_v1(img_path)
            
        logger.debug(f"{constants.detect_img_model} detect img: {img_path}, cur {i}/{count}, server response: {ret}")
        
    constants.ProcessingConfig.detect_model_flag = False
    logger.success("Model detect image all success!")
