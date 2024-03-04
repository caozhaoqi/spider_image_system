import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

import requests
from loguru import logger
from selenium.webdriver.common.by import By

from image.img_switch import find_images, image_exists
from image.spider_gif_url import spider_gif_images
from run import constants
from run.constants import proxy_flag, r18_mode, visit_url, all_show, detail_delta_time, allow_replace_domain_flag
from selenium import webdriver

from ui_event.get_url import open_look_all, slider_page_down, filter_not_use
from utils.http_tools import image_url_re
from file.user_agent import read_user_agent


@logger.catch
def is_keyword_num(driver, key_word):
    """

    :param driver:
    :param key_word:
    :return:
    """
    if key_word.isdigit():
        logger.info("input keyword is num, start process.")
        url = "https://" + visit_url + "/artworks/" + key_word
        image_list = artwork_single_image(key_word, driver, url)
        if not image_list:
            return True
        else:
            logger.success("spider success, start download.")
            for image_url in image_list:
                download_single_image(key_word, image_url)
        return True


@logger.catch
def spider_param_config(key_word):
    """
    spider param config
    :param webdriver:
    :param key_word:
    :return:
    """
    proxy = {
        "proxyType": "manual",
        "httpProxy": "http_tools://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),  # 代理服务器地址和端口
        "ftpProxy": "http_tools://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "sslProxy": "http_tools://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    options = webdriver.ChromeOptions()
    if constants.spider_mode == 'auto':
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        logger.warning("current spider mode: auto spider image mode!")

    # open dev tools
    options.add_argument("--auto-open-devtools-for-tabs")
    # 接受不安全证书
    options.add_argument("--ignore-certificate-errors")
    # 设置日志偏好，禁用所有日志
    options = disabled_log_browser(options)
    # 模拟不同浏览器访问页面 减少被封风险
    user_agents = read_user_agent()
    if not user_agents:
        # 没有txt 使用default value
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 '
            'Safari/537.36 '
        ]
        logger.warning(f"not user-agent, use default user-agent: {user_agents[0]}")
    # 随机添加user-agent
    cur_user_agents = random.choice(user_agents)
    # add user-agent
    if cur_user_agents:
        options.add_argument(
            f"user-agent={cur_user_agents}")
        logger.info(f"current use user-agent: {cur_user_agents}")
    if proxy_flag == 'True':
        options.set_capability("proxy", proxy)
        logger.info("current use internal proxy, proxy content: " + str(proxy['httpProxy']))

    driver = webdriver.Chrome(options=options)
    mode = ''
    if r18_mode == 'True':
        mode = 'mode=r18&'
        logger.warning("current start use r18 mode!")

    if allow_replace_domain_flag:
        logger.warning(f"start replace image domain, flag value: {allow_replace_domain_flag}")

    cur_page = 1
    if is_keyword_num(driver, key_word):
        driver.quit()
        return None, None, None
    url = "https://" + visit_url + "/tags/" + key_word + "/artworks?" + mode
    if all_show != 'False':
        # self define url by config file
        url = all_show
    return driver, url, cur_page


@logger.catch
def download_single_image(key_word, url):
    """
    download single image
    :param key_word:
    :param url:
    :return:
    """
    now_image_list = find_images(constants.data_path)
    image_name = image_url_re(url)
    if now_image_list is None:
        # 无数据 自动置位false
        image_exists_flag = False
    else:
        image_exists_flag = image_exists(image_name, now_image_list)
    if not image_exists_flag:
        file_dir = constants.data_path + "/according_pid_download_image/" + key_word + "/images"
        if not os.path.exists(file_dir):
            logger.warning("single save dir not exists, will create!")
            os.makedirs(file_dir)
        filename = os.path.join(file_dir, f"{os.path.basename(url)}")
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Image saved as {filename} success! ")
            else:
                logger.error("save fail!")
        except Exception as e:
            logger.error(f"save error, detail: {e}.")
    else:
        logger.warning("image already exists, will skip!")


@logger.catch
def artwork_single_image(key_word_pinyin, driver, url):
    """
    spider point url image from url
    :param key_word_pinyin:
    :param driver:
    :param url:
    :return:
    """
    image_url_list = []
    driver.get(url)
    if driver.title == '【国家反诈中心、工信部反诈中心、中国电信、中国联通、中国移动联合提醒】':
        logger.warning("error! will exit: cur visit domain blocked.")
        constants.firewall_flag = True
        return False
    if open_look_all(driver):
        logger.success(f"click look all success! pid: {url[-9:]}")
    # 抓取动图link
    if constants.spider_mode == 'manual':
        # 手动模式滑动页面 自动模式不滑动
        slider_page_down(driver)
    time.sleep(detail_delta_time)
    spider_gif_images(key_word_pinyin, driver)
    # logger.success("gif url txt save success!")
    image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
    for image_element in image_elements:
        image_url = image_element.get_attribute("src")
        if filter_not_use(image_url):
            continue
        else:
            driver.execute_script("return arguments[0].src;", image_element)
            image_url_list.append(image_url)
            logger.debug(f"single pid spider, save: {image_url}.")
    return image_url_list


@logger.catch
def disabled_log_browser(options):
    """

    """
    options.logging_prefs = {'performance': 'DISABLED', 'browser': 'DISABLED'}
    # 尝试减少日志输出的命令行参数
    options.add_argument("--log-level=3")  # 设置日志级别为最低（0-3），3表示最少日志
    options.add_argument("--disable-gpu")  # 在无头模式下通常使用
    options.add_argument("--silent")  # 尝试使Chrome更安静，但此参数可能不被所有版本支持

    # 如果你确定不需要性能日志，也可以尝试禁用它
    options.add_argument("--disable-performance-logging")
    return options