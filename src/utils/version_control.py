"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import requests
from loguru import logger
from run import constants


@logger.catch
def compare_versions(version1: str, version2: str) -> int:
    """比较两个版本号字符串
    
    Args:
        version1: 第一个版本号
        version2: 第二个版本号
        
    Returns:
        -1: version1 < version2
         0: version1 == version2 
         1: version1 > version2
    """
    # 移除'v'前缀
    version1 = version1.lstrip('v')
    version2 = version2.lstrip('v')

    # 将版本号分割为整数列表
    v1 = [int(part) for part in version1.split('.')]
    v2 = [int(part) for part in version2.split('.')]

    # 用0填充较短的列表
    max_length = max(len(v1), len(v2))
    v1.extend([0] * (max_length - len(v1)))
    v2.extend([0] * (max_length - len(v2)))

    # 逐位比较版本号
    for i in range(max_length):
        if v1[i] < v2[i]:
            return -1
        elif v1[i] > v2[i]:
            return 1

    return 0


@logger.catch
def compare_versions_with_pre_release(version1: str, version2: str) -> int:
    """比较带预发布标签的版本号
    
    Args:
        version1: 第一个版本号
        version2: 第二个版本号
        
    Returns:
        -1: version1 < version2
         0: version1 == version2
         1: version1 > version2
        None: 版本号格式错误
    """
    pattern = r'^v?(\d+(\.\d+)*)(.*?)$'

    match1 = re.match(pattern, version1)
    match2 = re.match(pattern, version2)

    if not match1:
        logger.warning(f"版本号格式错误: {version1}")
        return None

    if not match2:
        logger.warning(f"版本号格式错误: {version2}")
        return None

    main_version1, pre_release1 = match1.group(1), match1.group(3)
    main_version2, pre_release2 = match2.group(1), match2.group(3)

    # 如果都没有预发布标签,直接比较主版本号
    if not pre_release1 and not pre_release2:
        return compare_versions(main_version1, main_version2)

    # 有预发布标签的版本小于无预发布标签的版本
    if not pre_release1:
        return 1
    if not pre_release2:
        return -1

    # 主版本号相同时,比较预发布标签
    if main_version1 == main_version2:
        return -1 if pre_release1 < pre_release2 else 1

    return compare_versions(main_version1, main_version2)


@logger.catch
def download_new_version(version: str) -> bool:
    """下载新版本
    
    Args:
        version: 版本号
        
    Returns:
        bool: 下载是否成功
    """
    url = f'https://gitee.com/caozhaoqi/spider_image_system/releases/download/{version}/sis_{version}.exe'
    save_path = constants.basic_path

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                
        logger.success(f"新版本下载完成: {save_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败: {e}")
        return False
