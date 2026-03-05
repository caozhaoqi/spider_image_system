"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService

sys.path.append(str(Path(__file__).parent.parent))

import random
import requests

from http_tools.proxy_request import get_proxy_item
from image.img_switch import find_images, image_exists
from image.spider_gif_url import spider_gif_images
from run import constants
from ui_event.get_url import open_look_all, slider_page_down, filter_not_use
from utils.http_utils import image_url_re
from utils.os_environment_check import get_system_info_sim
from file.user_agent import read_user_agent
from utils.spider_operate import filter_not_use_url, artwork_filter
from utils.time_utils import sys_sleep_time


@logger.catch
def user_save_artwork(driver: WebDriver) -> Optional[List[str]]:
    """获取用户作品URL列表
    
    Args:
        driver: WebDriver实例
        
    Returns:
        作品URL列表,失败返回None
    """
    artwork_urls = []
    try:
        for element in driver.find_elements(By.CSS_SELECTOR, "a"):
            if constants.SpiderConfig.stop_spider_url_flag:
                break
                
            url = element.get_attribute("href")
            if not url:
                break
                
            if filter_not_use_url(url) or artwork_filter(url):
                continue
                
            driver.execute_script("return arguments[0].href;", element)
            artwork_urls.append(url)
            
        return artwork_urls
        
    except Exception as e:
        logger.error(f"获取作品URL失败: {e}")
        return None


@logger.catch
def is_keyword_num(driver: WebDriver, keyword: str) -> bool:
    """检查关键词是否包含特殊标记
    
    Args:
        driver: WebDriver实例
        keyword: 搜索关键词
        
    Returns:
        是否包含特殊标记
    """
    if "," not in keyword:
        if constants.SpiderConfig.spider_mode == "manual":
            constants.scheduled_download_program_flag = False
            logger.warning(f"关键词不包含分隔符',': {keyword}")
        return False
        
    constants.scheduled_download_program_flag = False
    keyword_list = keyword.split(',')
    special_spider(driver, keyword_list)
    return True


@logger.catch
def special_spider(driver: WebDriver, keyword_list: List[str]) -> Optional[bool]:
    """处理特殊关键词爬取
    
    Args:
        driver: WebDriver实例
        keyword_list: 关键词列表
        
    Returns:
        爬取是否成功
    """
    content, category = keyword_list[0], keyword_list[1]
    
    if category == 'pid':
        return spider_pid_image(driver, content)
    elif category == 'users':
        return spider_users_images(driver, content, category)
    
    return None


@logger.catch
def spider_users_images(driver: WebDriver, keyword: str, category: str) -> bool:
    """爬取用户作品
    
    Args:
        driver: WebDriver实例
        keyword: 用户ID
        category: 类别标记
        
    Returns:
        爬取是否成功
    """
    logger.info("开始爬取用户作品")
    page = 1
    
    while True:
        url = f"https://{constants.visit_url}/users/{keyword}/artworks?p={page}"
        driver.get(url)
        sys_sleep_time(driver, constants.search_delta_time, True)
        logger.info(f"当前页码: {page}")
        
        artwork_list = user_save_artwork(driver)
        
        if constants.SpiderConfig.stop_spider_url_flag:
            logger.warning("停止爬取")
            break
            
        if not artwork_list or driver.title in [constants.ban_content, constants.visit_url, '']:
            logger.warning(f"用户 {category} 无作品或被禁止访问: {driver.title}")
            constants.ProcessingConfig.firewall_flag = True
            break
            
        for artwork_url in artwork_list:
            images = artwork_single_image(keyword, driver, artwork_url)
            if not images:
                logger.warning(f"作品 {artwork_url} 无图片")
                continue
                
            logger.success("爬取成功,开始下载")
            for image_url in images:
                download_single_image(keyword, image_url)
                
        page += 1
        
    logger.info("用户作品爬取完成")
    return True


@logger.catch
def spider_pid_image(driver: WebDriver, pid: str) -> bool:
    """爬取单个作品
    
    Args:
        driver: WebDriver实例
        pid: 作品ID
        
    Returns:
        爬取是否成功
    """
    logger.info("开始爬取单个作品")
    url = f"https://{constants.visit_url}/artworks/{pid}"
    
    images = artwork_single_image(pid, driver, url)
    if not images:
        logger.warning("作品无图片")
        return False
        
    logger.success("爬取成功,开始下载")
    for image_url in images:
        download_single_image(pid, image_url)
        
    return True


@logger.catch
def set_proxy(proxy_flag: str) -> Optional[Dict[str, str]]:
    """设置代理配置
    
    Args:
        proxy_flag: 是否启用代理
        
    Returns:
        代理配置字典
    """
    if proxy_flag != 'True':
        return None
        
    if constants.proxy_mode == 'auto':
        logger.info("使用自动代理模式")
        proxy_item = get_proxy_item()
        if not proxy_item:
            logger.error("获取代理失败")
            return None
            
        return {
            "proxyType": "manual",
            "httpProxy": f"http://{proxy_item}",
            "ftpProxy": f"ftp://{proxy_item}", 
            "sslProxy": f"https://{proxy_item}",
            "noProxy": "",
            "proxyAutoconfigUrl": ""
        }
        
    proxy = {
        "proxyType": "manual",
        "httpProxy": f"http://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "ftpProxy": f"ftp://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "sslProxy": f"https://{constants.proxy_server_ip}:{constants.proxy_server_port}",
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }
    
    logger.info(f"使用代理: {proxy['httpProxy']}")
    return proxy


@logger.catch
def configure_browser_options() -> webdriver.ChromeOptions:
    """配置浏览器选项
    
    Returns:
        浏览器选项对象
    """
    system_info = get_system_info_sim()
    user_agents = read_user_agent()

    if not user_agents:
        user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36']
        logger.warning("未找到user-agent文件,使用默认值")

    cur_user_agent = random.choice(user_agents).strip()
    logger.info(f"当前user-agent: {cur_user_agent}")

    options = {
        'Linux': webdriver.ChromeOptions,
        'Windows': webdriver.EdgeOptions,
        'Darwin': webdriver.ChromeOptions,
    }.get(system_info, webdriver.ChromeOptions)()
    
    logger.debug(f"使用{system_info}浏览器")

    # 为所有系统添加 user-agent
    options.add_argument(f"user-agent={cur_user_agent}")
    options = chrome_options(options)

    return options


@logger.catch
def initialize_driver(options: webdriver.ChromeOptions, system_info: str) -> Optional[WebDriver]:
    """初始化浏览器驱动
    
    Args:
        options: 浏览器选项
        system_info: 系统信息
        
    Returns:
        WebDriver实例
    """
    try:
        service = get_driver_service(system_info)
        if constants.chrome_path != 'None':
            service.path = constants.chrome_path
            options.binary_location = constants.chrome_exe_path
        driver = create_driver(system_info, options, service)

        logger.info(f"驱动初始化成功: {constants.chrome_path}, {constants.chrome_exe_path}")
        return driver
        
    except Exception as e:
        logger.warning(f"驱动初始化失败: {type(e).__name__}, {e}")
        # 尝试直接使用已安装的 ChromeDriver
        import os
        chromedriver_path = '/Users/caozhaoqi/.wdm/drivers/chromedriver/mac64/145.0.7632.117/chromedriver-mac-arm64/chromedriver'
        if os.path.exists(chromedriver_path):
            logger.info(f"尝试使用已安装的 ChromeDriver: {chromedriver_path}")
            try:
                service = Service(chromedriver_path)
                driver = create_driver(system_info, options, service)
                logger.info("驱动初始化成功: 使用已安装的 ChromeDriver")
                return driver
            except Exception as e2:
                logger.warning(f"使用已安装的 ChromeDriver 失败: {type(e2).__name__}, {e2}")
                return None
        return None


@logger.catch
def get_driver_service(system_info: str) -> Service:
    """获取驱动服务
    
    Args:
        system_info: 系统信息
        
    Returns:
        Service实例
    """
    try:
        if system_info == 'Linux' or system_info == 'Darwin':
            return Service(ChromeDriverManager().install())
        elif system_info == 'Windows':
            return Service(EdgeChromiumDriverManager().install())
        return Service()
    except PermissionError as e:
        logger.warning(f"设置 ChromeDriver 执行权限失败: {e}")
        # 尝试直接使用已安装的 ChromeDriver
        import os
        chromedriver_path = '/Users/caozhaoqi/.wdm/drivers/chromedriver/mac64/145.0.7632.117/chromedriver-mac-arm64/chromedriver'
        if os.path.exists(chromedriver_path):
            logger.info(f"使用已安装的 ChromeDriver: {chromedriver_path}")
            return Service(chromedriver_path)
        return Service()


@logger.catch
def create_driver(system_info: str, options: webdriver.ChromeOptions, service: Optional[Service] = None) -> WebDriver:
    """创建浏览器驱动
    
    Args:
        system_info: 系统信息
        options: 浏览器选项
        service: 驱动服务
        
    Returns:
        WebDriver实例
    """
    drivers = {
        'Linux': webdriver.Chrome,
        'Windows': webdriver.Edge,
        'Darwin': webdriver.Chrome,  # 改为使用 Chrome
        'default': webdriver.Chrome  # 改为使用 Chrome
    }
    
    driver_class = drivers.get(system_info, drivers['default'])
    return driver_class(service=service, options=options) if service else driver_class(options=options)


@logger.catch
def spider_param_config(keyword: str) -> Tuple[Optional[WebDriver], Optional[str], Optional[int]]:
    """配置爬虫参数
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        驱动实例、URL和页码
    """
    try:
        options = configure_browser_options()
        proxy = set_proxy(constants.proxy_flag)

        if proxy:
            options.add_argument(f"--proxy-server={proxy['httpProxy']}")
            logger.info(f"使用代理: {proxy['httpProxy']}")

        system_info = get_system_info_sim()
        driver = initialize_driver(options, system_info)

        if not driver:
            logger.warning("驱动初始化失败")
            return None, None, None

        mode = 'mode=r18&' if constants.r18_mode == 'True' else ''
        
        if constants.r18_mode == 'True':
            logger.debug("启用R18模式")

        if constants.allow_replace_domain_flag:
            logger.debug(f"替换图片域名: {constants.allow_replace_domain_flag}")

        if is_keyword_num(driver, keyword):
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"关闭驱动时出错: {type(e).__name__}")
            return None, None, None

        url = f"https://{constants.visit_url}/tags/{keyword}/artworks?{mode}"
        
        if constants.all_show != 'False':
            url = constants.all_show

        logger.info(f"配置完成，URL: {url}")
        return driver, url, 1
    except Exception as e:
        logger.error(f"配置爬虫参数时出错: {type(e).__name__}, {e}")
        return None, None, None


@logger.catch
def chrome_options(options: webdriver.ChromeOptions) -> webdriver.ChromeOptions:
    """配置Chrome选项
    
    Args:
        options: Chrome选项对象
        
    Returns:
        配置后的选项对象
    """
    if constants.SpiderConfig.spider_mode == 'auto':
        auto_options = [
            '--headless',
            '--disable-gpu',
            '--disable-javascript',
            '--disable-plugins',
            '--disable-extensions',
            '--disable-java',
            '--mute-audio',
            '--single-process',
            '--disable-software-rasterizer',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
        for opt in auto_options:
            options.add_argument(opt)
        logger.debug("自动爬取模式")

    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_argument("--ignore-certificate-errors")
    options = disabled_log_browser(options)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-cache')
    options.page_load_strategy = 'none'

    if random.choice([True, False]):
        options.add_argument("--incognito")
        logger.info("启用无痕模式")

    return options


@logger.catch
def download_single_image(keyword: str, url: str) -> None:
    """下载单张图片
    
    Args:
        keyword: 关键词
        url: 图片URL
    """
    image_list = find_images(constants.data_path)
    image_name = image_url_re(url)
    
    if image_list is None:
        image_exists_flag = False
    else:
        image_exists_flag = image_exists(image_name, image_list)
        
    if image_exists_flag:
        logger.warning("图片已存在,跳过")
        return

    file_dir = Path(constants.data_path) / "according_pid_download_image" / keyword / "images"
    file_dir.mkdir(parents=True, exist_ok=True)
    
    filename = file_dir / os.path.basename(url)
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.debug(f"图片保存成功: {filename}")
        else:
            logger.error("保存失败")
    except Exception as e:
        logger.error(f"保存出错: {e}")


@logger.catch
def artwork_single_image(keyword: str, driver: WebDriver, url: str) -> Optional[List[str]]:
    """获取单个作品的图片URL
    
    Args:
        keyword: 关键词
        driver: WebDriver实例
        url: 作品URL
        
    Returns:
        图片URL列表
    """
    try:
        driver.get(url)
        sys_sleep_time(driver, constants.detail_delta_time, True)
        
        if driver.title in [constants.ban_content, constants.visit_url, '']:
            logger.warning(f"访问受限: {driver.title}")
            constants.ProcessingConfig.firewall_flag = True
            return None
            
    except Exception as e:
        logger.warning(f"访问出错: {type(e).__name__}")
        return None

    if open_look_all(driver):
        logger.success(f"展开全部成功: {url[-9:]}")

    if constants.SpiderConfig.spider_mode == 'manual':
        slider_page_down(driver)

    spider_gif_images(keyword, driver)

    image_urls = []
    for element in driver.find_elements(By.CSS_SELECTOR, "img"):
        image_url = element.get_attribute("src")
        if not filter_not_use(image_url):
            driver.execute_script("return arguments[0].src;", element)
            image_urls.append(image_url)
            logger.debug(f"获取图片URL: {image_url}")

    return image_urls


@logger.catch
def disabled_log_browser(options: webdriver.ChromeOptions) -> webdriver.ChromeOptions:
    """禁用浏览器日志
    
    Args:
        options: Chrome选项对象
        
    Returns:
        配置后的选项对象
    """
    options.logging_prefs = {'performance': 'DISABLED', 'browser': 'DISABLED'}
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--silent")
    options.add_argument("--disable-performance-logging")
    return options
