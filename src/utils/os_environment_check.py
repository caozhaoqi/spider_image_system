"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

"""
检查和配置操作系统环境
"""
import os
import platform
import sys
from pathlib import Path
from typing import Optional

import requests
import zipfile
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from utils.download_driver import ChromeDriverDownloader

sys.path.append(str(Path(__file__).parent.parent))

from run import constants


@logger.catch
def auto_download_webdriver() -> None:
    """自动下载Chrome WebDriver"""
    chrome = ChromeDriverDownloader.download_chrome_drive()
    chrome.start()


@logger.catch
def auto_download_chrome() -> bool:
    """自动下载Chrome浏览器
    
    Returns:
        下载是否成功
    """
    dest_path = Path(constants.basic_path) / "chrome.exe"
    url = search_chrome_download_link(constants.chrome_version)
    
    if not url:
        logger.error("未找到对应Chrome版本,终止后续操作")
        return False
        
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        logger.error(f"下载失败,状态码: {response.status_code}")
        return False
        
    with open(dest_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            
    logger.info(f"文件已下载到: {dest_path}")
    extract_zip(dest_path, dest_path)
    logger.success("解压成功,请打开chrome.exe安装!")
    return True


@logger.catch
def extract_zip(zip_path: Path, extract_to: Path) -> None:
    """解压zip文件
    
    Args:
        zip_path: zip文件路径
        extract_to: 解压目标路径
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"文件已解压到: {extract_to}")


@logger.catch
def search_chrome_download_link(version: str) -> Optional[str]:
    """搜索Chrome下载链接
    
    Args:
        version: Chrome版本号
        
    Returns:
        下载链接,未找到则返回None
    """
    search_url = "https://registry.npmmirror.com/-/binary/chromedriver/"
    response = requests.get(search_url)
    
    if response.status_code != 200:
        return None
        
    search_results = response.json()
    version_link = next(
        (item['url'] for item in search_results 
         if version in item['url'] and "LATEST_RELEASE" not in item['url']),
        None
    )
    
    if not version_link:
        return None
        
    response_link = requests.get(version_link)
    if response_link.status_code != 200:
        return None
        
    link_results = response_link.json()
    return next(
        (item['url'] for item in link_results
         if "win" in item['name'] or "win" in item['url']),
        None
    )


@logger.catch
def detect_installed() -> bool:
    """检测Chrome和WebDriver是否安装
    
    Returns:
        是否已正确安装
    """
    if is_chromedriver_installed():
        return True
        
    logger.error("未安装Chrome浏览器或WebDriver,请访问以下网址下载:")
    logger.warning(
        "网址: https://googlechromelabs.github.io/chrome-for-testing/#stable "
        "选择正确版本下载,并在./config/config.ini文件中配置chrome_path"
    )
    
    chrome_version = ChromeDriverDownloader.get_chromedriver_urls()
    if chrome_version:
        logger.info(f"当前Chrome版本: {chrome_version}")
        auto_download_webdriver()
    else:
        logger.warning("未检测到Chrome浏览器,将自动下载并解压,请手动安装!")
        auto_download_chrome()
    return False


@logger.catch
def is_chromedriver_installed() -> bool:
    """检查ChromeDriver是否正确安装
    
    Returns:
        是否已正确安装
    """
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if constants.chrome_path != 'None':
            service = Service(constants.chrome_path)
            driver = webdriver.Chrome(service=service, options=options)
            logger.warning("使用用户自定义ChromeDriver路径")
        else:
            driver = webdriver.Chrome(options=options)
            logger.info("使用系统默认WebDriver")
            
        logger.success("ChromeDriver安装并工作正常")
        driver.quit()
        return True
        
    except Exception as e:
        logger.error("ChromeDriver未安装或配置错误")
        logger.error(f"错误信息: {e}")
        return False


@logger.catch
def get_system_info_sim() -> str:
    """获取系统信息
    
    Returns:
        操作系统名称
    """
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    architecture = platform.architecture()
    
    windows_version = platform.win32_ver() if os_name == "Windows" else None
    
    system_info = {
        "操作系统名称": os_name,
        "操作系统版本": os_version,
        "操作系统发布版本": os_release,
        "系统架构": architecture,
        "Windows版本": windows_version
    }
    
    return os_name