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
import zipfile
import requests
from utils.download_driver import get_chrome_version_from_executable, AutoDownloadChromeDrive


@logger.catch
def auto_download_webdriver():
    """

    :return:
    """
    chrome = AutoDownloadChromeDrive()
    chrome.start()
    # logger.warning(
    #     "Because exe more larger(>100MB), so cancel AutoDownloadChromeDrive, please manual download webdriver!")


@logger.catch
def auto_download_chrome():
    """

    :return:
    """
    dest_path = constants.basic_path + "/chrome.exe"  # 对于Windows系统
    url = search_chrome_download_link(constants.chrome_version)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logger.info(f"File downloaded to {dest_path}")
        extract_zip(dest_path, dest_path)
        logger.success("unzip success, please open chrome.exe install!")
    else:
        logger.error(f"Failed to download file. Status code: {response.status_code}")


@logger.catch
def extract_zip(zip_path, extract_to):
    """

    :param zip_path:
    :param extract_to:
    :return:
    """

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"File extracted to {extract_to}")


@logger.catch
def search_chrome_download_link(version):
    """

    :param version:
    :return:
    """

    search_url = f"https://registry.npmmirror.com/-/binary/chromedriver/"

    response = requests.get(search_url)
    # get version url
    version_link = None
    if response.status_code == 200:
        search_results = response.json()
        for item in search_results:
            if version in item['url'] and "LATEST_RELEASE" not in item['url']:
                version_link = item['url']
    if version_link:
        # get win version download link
        response_link = requests.get(version_link)
        if response_link.status_code == 200:
            link_results = response_link.json()
            for item_link in link_results:
                if "win" in item_link['name'] or "win" in item_link['url']:
                    return item_link['url']
            return None
    else:
        return None


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
        chrome_version = get_chrome_version_from_executable()
        logger.info(f"current google chrome version: {chrome_version}.")
        if chrome_version:
            auto_download_webdriver()
        else:
            logger.warning("WARNING! you pc not google chrome, will auto download and unzip, please manual install!")
            auto_download_chrome()
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
