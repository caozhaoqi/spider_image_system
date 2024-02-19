import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from run import constants
from image.gif_img_process import read_gif_url


@logger.catch
def spider_gif_images(keyword, chrome_driver):
    """
    抓取动态资源
    :param keyword:
    :param chrome_driver:  chrome驱动
    :return:
    """
    api_urls = []
    requests = chrome_driver.execute_script("return window.performance.getEntriesByType('resource')")
    for request in requests:
        if request['initiatorType'] == 'fetch' and "img-zip-ugoira" in request['name']:
            api_urls.append(request['name'])
            logger.success(f"spider gif zip url: {request['name']}")
            break
    txt_path_name = os.path.join(constants.data_path, "href_url")
    if not os.path.exists(txt_path_name):
        os.makedirs(txt_path_name)
    if len(api_urls) == 0:
        logger.warning("no zip gif images data!")
        return False
    if read_gif_url(txt_path_name + "/" + keyword + "_zip.txt", api_urls):
        return True
    return False

