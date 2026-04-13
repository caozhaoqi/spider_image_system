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

from loguru import logger
from run import constants
from image.gif_img_process import read_gif_url


@logger.catch
def spider_gif_images(keyword: str, chrome_driver) -> bool:
    """Extract GIF/animation URLs from browser resources
    
    Args:
        keyword: Search keyword for naming output file
        chrome_driver: Selenium Chrome WebDriver instance
        
    Returns:
        bool: True if URLs were found and saved successfully
    """
    try:
        # Get network requests from browser performance data
        requests = chrome_driver.execute_script(
            "return window.performance.getEntriesByType('resource')"
        )
        
        # Find animation zip file URLs
        api_urls = []
        for request in requests:
            if request['initiatorType'] == 'fetch' and "img-zip-ugoira" in request['name']:
                api_urls.append(request['name'])
                logger.success(f"Found gif url: {request['name'][-27:]}")
                break
                
        if not api_urls:
            return False
            
        # Create output directory
        txt_path_name = os.path.join(constants.data_path, "href_url")
        os.makedirs(txt_path_name, exist_ok=True)
        
        # Save URLs to file
        zip_txt_path = os.path.join(txt_path_name, f"{keyword}_zip.txt")
        return read_gif_url(zip_txt_path, api_urls)
        
    except Exception as e:
        logger.warning(f"Failed to extract GIF URLs: {type(e).__name__}")
        return False
