import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

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
        return True
    return False


@logger.catch
def slider_page_down(driver):
    """

    :param driver:
    :return:
    """
    page_height = driver.execute_script("return document.body.scrollHeight")

    actions = ActionChains(driver)
    actions.send_keys(Keys.END).perform()
    actions.send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(detail_delta_time)
    actions.send_keys(Keys.HOME).perform()
    actions.send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(detail_delta_time)
    logger.info(f"slider page down! page height {page_height}px")
