"""
exe execute os environment
"""
import os
import platform
import subprocess

from loguru import logger
from selenium import webdriver

# 定义下载和安装函数，这些函数将根据平台进行调整
from selenium.webdriver.chrome.service import Service

from run import constants


# 主程序
@logger.catch
def detect_installed():
    """

    :return:
    """

    # 检查并安装selenium和chromedriver
    logger.info("start detect current os installed webdriver.")
    if not is_chromedriver_installed():
        logger.error("you hasn't install selenium for chrome explore or chrome webdriver, please visit website "
                     "download.")
        logger.warning("visit: https://googlechromelabs.github.io/chrome-for-testing/#stable")
        return False
    # logger.info("detect finish.")
    return True


# 检测selenium和chromedriver是否已安装的函数
# @logger.catch
# def is_selenium_installed():
#     """
#
#     :return:
#     """
#     try:
#         import selenium  # 尝试导入selenium库
#         return True
#     except ImportError:
#         return False


@logger.catch
def is_chromedriver_installed():
    """

    :return:
    """

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if constants.chrome_path != 'None':
            ser = Service()
            ser.path = constants.chrome_path
            # 连接Edge浏览器
            driver = webdriver.Chrome(service=ser, options=options)
            logger.warning("user self define chrome driver exe!")
        else:
            driver = webdriver.Chrome(options=options)
            logger.info("use system default web driver!")
        logger.success("ChromeDriver is installed and working correctly.")
        driver.quit()
        return True
    except Exception as e:
        logger.error("ChromeDriver is not installed or not configured correctly.")
        logger.error("Error message:", str(e))
        return False


if __name__ == '__main__':
    detect_installed()
