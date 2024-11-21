import os
import sys

from selenium.webdriver.edge.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.os_environment_check import get_system_info_sim

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from webdriver_manager.microsoft import  EdgeChromiumDriverManager
from http_tools.proxy_request import get_proxy_item
import requests
from loguru import logger
from selenium.webdriver.common.by import By
from image.img_switch import find_images, image_exists
from image.spider_gif_url import spider_gif_images
from run import constants
from run.constants import proxy_flag, r18_mode, visit_url, all_show, allow_replace_domain_flag, \
    search_delta_time
from selenium import webdriver
from ui_event.get_url import open_look_all, slider_page_down, filter_not_use
from utils.http_utils import image_url_re
from file.user_agent import read_user_agent
from utils.spider_operate import filter_not_use_url, artwork_filter
from utils.time_utils import sys_sleep_time


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
def is_keyword_num(driver_keyword, key_word):
    """

    :param driver_keyword:
    :param key_word:
    :return:
    """
    if "," not in key_word:
        if constants.spider_mode == "manual":
            constants.scheduled_download_program_flag = False
            logger.warning(f"You input keyword not contain ',' in spilt keyword: {key_word}.")
        return False
    constants.scheduled_download_program_flag = False
    key_word_list = key_word.split(',')
    special_spider(driver_keyword, key_word_list)
    return True


@logger.catch
def special_spider(driver_keyword, key_word_list):
    """

    :param driver_keyword:
    :param key_word_list:
    :return:
    """
    keyword_content = key_word_list[0]
    keyword_cat = key_word_list[1]
    # key_word = keyword_content
    if keyword_cat == 'pid':
        return spider_pid_image(driver_keyword, keyword_content)
    elif keyword_cat == 'users':
        return spider_users_images(driver_keyword, keyword_content, keyword_cat)


@logger.catch
def spider_users_images(driver_user, key_word, keyword_cat):
    """

    :param driver_user:
    :param key_word:
    :param keyword_cat:
    :return:
    """
    logger.info("Input keyword is users, start process")
    while True:
        cur_page = 1
        url = "https://" + visit_url + "/users/" + key_word + "/artworks?p=" + str(cur_page)
        driver_user.get(url)
        # driver_user.implicitly_wait(search_delta_time)
        sys_sleep_time(driver_user, search_delta_time, True)
        logger.info(f"Cur spider users artwork cur_page: {cur_page}")
        artwork_list = user_save_artwork(driver_user)
        if constants.stop_spider_url_flag:
            logger.warning("Stop spider url, get users url spider artwork url.")
            break
        if not artwork_list or driver_user.title == constants.ban_content or driver_user.title == constants.visit_url \
                or driver_user.title == '':
            logger.warning(
                f"Users: {keyword_cat}, spider image no artwork or ban content:{driver_user.title}, skip loop")
            constants.firewall_flag = True
            break
        for artwork_url in artwork_list:
            image_list = artwork_single_image(key_word, driver_user, artwork_url)
            if not image_list:
                logger.warning(f"Users: {keyword_cat}, spider image:{artwork_url}, no image.")
                continue
            else:
                logger.success("Spider success, start download.")
                for image_url in image_list:
                    download_single_image(key_word, image_url)
        cur_page += 1
    logger.info("Spider users end.")
    return True


@logger.catch
def spider_pid_image(driver_pid, key_word):
    """

    :param driver_pid:
    :param key_word:
    :return:
    """
    logger.info("Input keyword is num, start process.")
    url = "https://" + visit_url + "/artworks/" + key_word
    image_list = artwork_single_image(key_word, driver_pid, url)
    if not image_list:
        logger.warning("Pid spider image no image.")
        return False
    else:
        logger.success("Spider success, start download.")
        for image_url in image_list:
            download_single_image(key_word, image_url)
    return True


@logger.catch
def set_proxy(proxy_flag):
    """

    """
    """设置代理"""
    proxy = {
        "proxyType": "manual",
        "httpProxy": f"http://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "ftpProxy": f"ftp://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "sslProxy": f"https://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    if proxy_flag == 'True':
        if constants.proxy_mode == 'auto':
            logger.info("Using auto select proxy model.")
            proxy_item = get_proxy_item()
            if not proxy_item:
                logger.error("Proxy item is None, quitting spider.")
                return None
            proxy = {
                "proxyType": "manual",
                "httpProxy": f"http://{proxy_item}",
                "ftpProxy": f"ftp://{proxy_item}",
                "sslProxy": f"https://{proxy_item}",
                "noProxy": "",
                "proxyAutoconfigUrl": ""
            }
        logger.info(f"Using proxy: {proxy['httpProxy']}")
        return proxy
    return None


@logger.catch
def configure_browser_options():
    """根据操作系统配置浏览器选项"""
    system_info = get_system_info_sim()  # 获取系统信息
    user_agents = read_user_agent()

    if not user_agents:
        # 如果没有用户代理文件，使用默认值
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36']
        logger.warning("No user-agent file found, using default user-agent.")

    # 随机选择一个 user-agent
    cur_user_agents = random.choice(user_agents).strip()
    logger.info(f"Current user-agent: {cur_user_agents}")

    # 根据系统设置浏览器选项
    if system_info == 'Linux':
        options = webdriver.ChromeOptions()
        logger.debug("Using Chrome browser on Linux.")
    elif system_info == 'Windows':
        options = webdriver.EdgeOptions()
        logger.debug("Using Edge browser on Windows.")
    else:
        options = webdriver.SafariOptions()
        logger.debug("Using Safari browser.")

    # 配置浏览器选项
    options.add_argument(f"user-agent={cur_user_agents}")
    options = chrome_options(options)  # 应用任何额外的浏览器配置

    return options


@logger.catch
def initialize_driver(options_explore, system_info):
    """初始化并返回浏览器驱动"""
    try:
        # 如果有自定义的浏览器路径
        if constants.chrome_path != 'None':
            driver_service = get_driver_service(system_info)
            driver_service.path = constants.chrome_path
            options_explore.binary_location = constants.chrome_exe_path
            driver = create_driver(system_info, options_explore, driver_service)
        else:
            driver = create_driver(system_info, options_explore)

        logger.info(
            f"Driver initialized with executable path: {constants.chrome_path}, exe path: {constants.chrome_exe_path}")
        return driver
    except Exception as e:
        logger.warning(f"Error initializing driver: {type(e).__name__}, {e}")
        return None


@logger.catch
def get_driver_service(system_info):
    """根据操作系统返回相应的驱动服务"""
    if system_info == 'Linux':
        return Service(ChromeDriverManager().install())
    elif system_info == 'Windows':
        return Service(EdgeChromiumDriverManager().install())
    else:
        return Service()


@logger.catch
def create_driver(system_info, options_explore, service=None):
    """根据操作系统创建相应的浏览器驱动"""
    if system_info == 'Linux':
        return webdriver.Chrome(service=service, options=options_explore) if service else webdriver.Chrome(
            options=options_explore)
    elif system_info == 'Windows':
        return webdriver.Edge(service=service, options=options_explore) if service else webdriver.Edge(
            options=options_explore)
    else:
        return webdriver.Safari(service=service, options=options_explore) if service else webdriver.Safari(
            options=options_explore)


@logger.catch
def spider_param_config(key_word):
    """
    Spider param configuration for initializing the driver and handling proxy setup
    :param key_word: Keyword to be used in the search
    :return: driver, url, cur_page
    """
    driver = None
    options_explore = configure_browser_options()  # 配置浏览器选项

    # 设置代理
    proxy = set_proxy(proxy_flag)

    if proxy:
        options_explore.add_argument(f"--proxy-server={proxy['httpProxy']}")
        logger.info(f"Using internal proxy: {proxy['httpProxy']}")

    # 初始化浏览器驱动
    system_info = get_system_info_sim()
    driver = initialize_driver(options_explore, system_info)

    if driver is None:
        return None, None, None

    mode = ''
    if r18_mode == 'True':
        mode = 'mode=r18&'
        logger.debug("R18 mode enabled.")

    if allow_replace_domain_flag:
        logger.debug(f"Replacing image domain, flag: {allow_replace_domain_flag}")

    cur_page = 1
    if is_keyword_num(driver, key_word):
        driver.quit()
        return None, None, None
    else:
        url = f"https://{visit_url}/tags/{key_word}/artworks?{mode}"

    if all_show != 'False':
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
        logger.debug("Current spider mode: auto spider image mode!")
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
    options.add_argument('--disable-application-cache')  # 禁用应用程序缓存
    options.add_argument('--disable-cache')  # 禁用浏览器缓存
    options.page_load_strategy = 'none'  # 加载策略
    random_boolean = random.choice([True, False])
    if random_boolean:
        # 无痕模式 减少被追踪风险
        options.add_argument("--incognito")  # 启动无痕模式
        logger.info("Cur enable incognito mode spider image!")
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
            logger.warning("Single save dir not exists, will create!")
            os.makedirs(file_dir)
        filename = os.path.join(file_dir, f"{os.path.basename(url)}")
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Image saved as {filename} success! ")
            else:
                logger.error("Save fail!")
        except Exception as e:
            logger.error(f"Save error, detail: {e}.")
    else:
        logger.warning("Image already exists, will skip!")


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
        sys_sleep_time(driver, constants.detail_delta_time, True)
        if driver.title == constants.ban_content or driver.title == constants.visit_url \
                or driver.title == '':
            logger.warning(f"Error! will exit: cur visit domain blocked, title: {driver.title}")
            constants.firewall_flag = True
            return False
    except Exception as e:
        logger.warning(f"Unknown error: type: {type(e).__name__}.")
    if open_look_all(driver):
        logger.success(f"Click look all success! pid: {url[-9:]}")
    # 抓取动图link
    if constants.spider_mode == 'manual':
        # 手动模式滑动页面 自动模式不滑动
        slider_page_down(driver)
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
            logger.debug(f"Single pid spider, save: {image_url}.")
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
