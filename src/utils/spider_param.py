import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import time
from selenium.webdriver.chrome.service import Service
from http_tools.proxy_request import get_proxy_item
import requests
from loguru import logger
from selenium.webdriver.common.by import By
from image.img_switch import find_images, image_exists
from image.spider_gif_url import spider_gif_images
from run import constants
from run.constants import proxy_flag, r18_mode, visit_url, all_show, detail_delta_time, allow_replace_domain_flag, \
    search_delta_time
from selenium import webdriver
from ui_event.get_url import open_look_all, slider_page_down, filter_not_use
from utils.http_utils import image_url_re
from file.user_agent import read_user_agent
from utils.spider_operate import filter_not_use_url, artwork_filter


@logger.catch
def user_save_artwork(driver):
    """

    :param driver:
    :return:
    """
    artwork_urls_list = []
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        for image_element in image_elements:
            if not constants.stop_spider_url_flag:
                image_url = image_element.get_attribute("href")
                if image_url is None:
                    break
                if filter_not_use_url(image_url) or artwork_filter(image_url):
                    continue
                driver.execute_script("return arguments[0].href;", image_element)
                artwork_urls_list.append(image_url)
        return artwork_urls_list
    except Exception as un_e:
        logger.error("Error, unknown error, detail:" + str(un_e))
        return None


@logger.catch
def is_keyword_num(driver, key_word):
    """

    :param driver:
    :param key_word:
    :return:
    """
    if "," not in key_word:
        logger.warning(f"you input keyword not contain ',' in spilt keyword: {key_word}.")
        return False
    key_word_list = key_word.split(',')
    keyword_content = key_word_list[0]
    keyword_cat = key_word_list[1]
    key_word = keyword_content
    if keyword_cat == 'pid':
        return spider_pid_image(driver, key_word)
    elif keyword_cat == 'users':
        return spider_users_images(driver, key_word, keyword_cat)


@logger.catch
def spider_users_images(driver, key_word, keyword_cat):
    """

    :param driver:
    :param key_word:
    :param keyword_cat:
    :return:
    """
    logger.info("input keyword is users, start process")
    while True:
        cur_page = 1
        url = "https://" + visit_url + "/users/" + key_word + "/artworks?p=" + str(cur_page)
        driver.get(url)
        time.sleep(search_delta_time)
        logger.info(f"cur spider users artwork cur_page: {cur_page}")
        artwork_list = user_save_artwork(driver)
        if constants.stop_spider_url_flag:
            logger.warning("stop spider url, get users url spider artwork url.")
            break
        if not artwork_list or driver.title == constants.ban_content or driver.title == constants.visit_url \
                or driver.title == '':
            logger.warning(
                f"users: {keyword_cat}, spider image no artwork or ban content:{driver.title}, skip loop")
            constants.firewall_flag = True
            break
        for artwork_url in artwork_list:
            image_list = artwork_single_image(key_word, driver, artwork_url)
            if not image_list:
                logger.warning(f"users: {keyword_cat}, spider image:{artwork_url}, no image.")
                continue
            else:
                logger.success("spider success, start download.")
                for image_url in image_list:
                    download_single_image(key_word, image_url)
        cur_page += 1
    logger.info("spider users end.")
    return True


@logger.catch
def spider_pid_image(driver, key_word):
    """

    :param driver:
    :param key_word:
    :return:
    """
    logger.info("input keyword is num, start process.")
    url = "https://" + visit_url + "/artworks/" + key_word
    image_list = artwork_single_image(key_word, driver, url)
    if not image_list:
        logger.warning("pid spider image no image.")
        return False
    else:
        logger.success("spider success, start download.")
        for image_url in image_list:
            download_single_image(key_word, image_url)
    return True


@logger.catch
def spider_param_config(key_word):
    """
    spider param config
    :param key_word:
    :return:
    """
    global driver
    proxy = {
        "proxyType": "manual",
        "httpProxy": "http://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),  # 代理服务器地址和端口
        "ftpProxy": "ftp://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "sslProxy": "https://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    options = webdriver.ChromeOptions()
    options = chrome_options(options)
    # 模拟不同浏览器访问页面 减少被封风险
    user_agents = read_user_agent()
    if not user_agents:
        # 没有txt 使用default value
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 '
            'Safari/537.36 '
        ]
        logger.warning(f"not found user-agent, use default user-agent: {user_agents[0]}")
    # 随机添加user-agent
    cur_user_agents = random.choice(user_agents).strip()
    # add user-agent
    if cur_user_agents:
        options.add_argument(
            f"user-agent={cur_user_agents}")
        logger.info(f"current use user-agent: {cur_user_agents}")
    if proxy_flag == 'True':
        if constants.proxy_mode == 'auto':
            logger.info("cur spider use proxy is auto select proxy model.")
            proxy_item = get_proxy_item()
            if not proxy_item:
                logger.error("proxy_item None, will quit spider image!")
                return None, None, None
            logger.debug(f"use proxy: {proxy_item}")
            proxy = {
                "proxyType": "manual",
                "httpProxy": "http://" + proxy_item,  # 代理服务器地址和端口
                "ftpProxy": "ftp://" + proxy_item,
                "sslProxy": "https://" + proxy_item,
                "noProxy": "",
                "proxyAutoconfigUrl": ""
            }
        # options.set_capability("proxy", proxy)
        options.add_argument("--proxy-server={}".format(proxy["httpProxy"]))
        logger.info("current use internal proxy, proxy content: " + str(proxy['httpProxy']))

    try:
        if constants.chrome_path != 'None':
            ser = Service()
            ser.path = constants.chrome_path
            # 连接Edge浏览器
            driver = webdriver.Chrome(service=ser, options=options)
            logger.debug("user self define chrome driver exe!")
        else:
            driver = webdriver.Chrome(options=options)
            logger.info("use system default web driver!")
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}.")

    mode = ''
    if r18_mode == 'True':
        mode = 'mode=r18&'
        logger.debug("current start use r18 mode!")

    if allow_replace_domain_flag:
        logger.debug(f"start replace image domain, flag value: {allow_replace_domain_flag}")

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
def chrome_options(options):
    """

    :param options:
    :return:
    """
    if constants.spider_mode == 'auto':
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-javascript")
        options.add_argument("--disable-plugins")
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-java')
        options.add_argument('--mute-audio')
        options.add_argument('--single-process')
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        logger.debug("current spider mode: auto spider image mode!")
    # open dev tools
    options.add_argument("--auto-open-devtools-for-tabs")
    # 接受不安全证书
    options.add_argument("--ignore-certificate-errors")
    # 设置日志偏好，禁用所有日志
    options = disabled_log_browser(options)
    # 去除 “Chrome正受到自动化测试软件的控制”
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 添加浏览器特征
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    random_boolean = random.choice([True, False])
    if random_boolean:
        # 无痕模式 减少被追踪风险
        options.add_argument("--incognito")  # 启动无痕模式
        logger.info("cur enable incognito mode spider image!")
    return options


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
    try:
        driver.get(url)
        if driver.title == constants.ban_content or driver.title == constants.visit_url \
                or driver.title == '':
            logger.warning(f"error! will exit: cur visit domain blocked, title: {driver.title}")
            constants.firewall_flag = True
            return False
    except Exception as e:
        logger.warning(f"unknown error: type: {type(e).__name__}.")
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
