import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from loguru import logger
from selenium.webdriver import ActionChains, Keys
from run import constants
from run.constants import detail_delta_time


@logger.catch
def filter_not_use(url):
    """
    filter not need url
    :param url:
    :return:
    """
    filter_url_http = constants.filter_http_url.split(',')
    try:
        for filter_url_http_content in filter_url_http:
            if filter_url_http_content in url:
                return True
    except Exception as e:
        # 遇到异常跳过该url
        logger.warning("unknown error, detail: " + str(e))
        return True


@logger.catch
def filter_not_use_url(image_url):
    """
    filter not need http_tools url
    :param image_url: filter url
    :return:
    """
    filter_url_image = constants.filter_image_url.split(',')
    try:
        for filter_url_image_content in filter_url_image:
            if filter_url_image_content in image_url or "artworks" not in image_url:
                return True
    except Exception as e:
        logger.warning("unknown error, detail: " + str(e))
        return True


@logger.catch
def artwork_filter(url):
    """
    artwork url filter for users image spider
    :param url: spider url
    :return: compare result
    """
    parts = url.split("/artworks/")
    if len(parts) > 1:
        content_after_artworks = parts[1]
        if content_after_artworks.isdigit():
            return False
    return True


@logger.catch
def url_process_page(url, current_page):
    """
    split page from point url
    :param current_page:
    :param url:
    :return:
    """
    page_url = url + "p=" + str(current_page) + "&s_mode=s_tag"
    return page_url


@logger.catch
def open_look_all(driver):
    """
    点击查看全部 按钮模拟点击
    :param driver:
    :return:
    """
    """
    """

    try:
        button = driver.execute_script("""
        var buttons = document.getElementsByTagName('button');
        for (var i = 0; i < buttons.length; i++) {
          var button = buttons[i];
          if (button.textContent.includes('查看全部') || button.textContent.includes('阅读作品')) {
            return button;
          }
        }
        """)
        if button:
            button.click()
            driver.implicitly_wait(detail_delta_time)
            random_action(driver)
            return True
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")
        # driver.quit()
    return False


@logger.catch
def slider_page_down(driver):
    """

    :param driver:
    :return:
    """
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")

        actions = ActionChains(driver)
        actions.send_keys(Keys.END).perform()
        actions.send_keys(Keys.PAGE_DOWN).perform()
        driver.implicitly_wait(detail_delta_time)
        actions.send_keys(Keys.HOME).perform()
        actions.send_keys(Keys.PAGE_DOWN).perform()
        driver.implicitly_wait(detail_delta_time)
        logger.info(f"slider page down! page height {page_height}px")
        random_action(driver)
        driver.implicitly_wait(detail_delta_time)
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")


@logger.catch
def random_action(driver):
    """

    :param driver:
    :return:
    """
    # # 假设 driver 已经初始化
    try:
        # 获取页面高度
        page_height = driver.execute_script("return document.body.scrollHeight")

        # 定义一些随机时间和动作
        random_delay = random.randint(1, 5)  # 随机延迟1到3秒
        random_keys = [Keys.END, Keys.PAGE_DOWN, Keys.HOME]  # 可能的按键列表
        random_key_order = random.sample(random_keys, len(random_keys))  # 随机选择按键顺序
        random_key_repeats = random.randint(1, 5)  # 每个按键随机重复1到3次

        # 执行随机动作
        actions = ActionChains(driver)
        for key in random_key_order:
            for _ in range(random_key_repeats):
                actions.send_keys(key).perform()
                driver.implicitly_wait(random.random() * random_delay)  # 在每个动作之间添加随机延迟

        # 执行最终的页面滚动和延迟
        driver.implicitly_wait(random.random() * random_delay)
        actions.send_keys(Keys.HOME).perform()
        actions.send_keys(Keys.PAGE_DOWN).perform()
        driver.implicitly_wait(random.random() * random_delay)

        # 记录日志
        logger.info(f"Random slider page down! page height {page_height}px")
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")

