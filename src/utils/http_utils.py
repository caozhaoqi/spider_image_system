import os
import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent.parent))
import re
from loguru import logger


@logger.catch
def is_valid_url(http_url: str) -> bool:
    """检查URL是否有效
    
    Args:
        http_url: 要检查的URL
        
    Returns:
        bool: URL是否有效
    """
    pattern = r'^https?://.+$'
    return bool(re.match(pattern, http_url))


@logger.catch
def image_url_re(image_url: str) -> str:
    """从URL中提取图片文件名
    
    Args:
        image_url: 图片URL
        
    Returns:
        str: 图片文件名或原始URL
    """
    result_url = image_url.split('/')[-1]
    if result_url.endswith(('.jpg', '.png')):
        return result_url
        
    try:
        result_url = re.search(r'/([^/?#]+)$', image_url).group(1)
        if result_url.endswith(('.jpg', '.png', '.gif')):
            return result_url
            
        logger.warning(f"解析错误,返回源URL: {image_url}")
        return image_url
        
    except AttributeError:
        logger.error(f"图片URL无法分割,源URL: {image_url}, 请检查config.ini配置并添加项目!")
        return image_url
    except Exception as e:
        logger.error(f"未知错误,请检查日志,源URL: {image_url}")
        return image_url


@logger.catch
def match_img_result(file_name: str) -> str:
    """从文件名中提取关键词
    
    Args:
        file_name: 文件名
        
    Returns:
        str: 提取的关键词或'unknown'
    """
    pattern = r'.*[\\/]([^_]+)_img_result.*'
    matches = re.findall(pattern, file_name)
    if matches:
        return matches[0]
    return "unknown"
