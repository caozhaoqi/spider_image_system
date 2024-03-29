"""
exe execute os environment
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from run import constants


# 主程序
@logger.catch
def detect_installed():
    """

    :return:
    """

    # 检查并安装selenium和chromedriver
    if not is_chromedriver_installed():
        logger.error("you hasn't install selenium for chrome explore or chrome webdriver, please visit follow website "
                     "download:")
        logger.warning("url: https://googlechromelabs.github.io/chrome-for-testing/#stable select correct version to"
                       " download, finish config download webdriver.exe path to chrome_path from "
                       "./config/config.ini file.")
        return False
    return True


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

#
# if __name__ == '__main__':
#     detect_installed()
