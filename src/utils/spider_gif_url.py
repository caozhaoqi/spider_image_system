import os

from loguru import logger
from gui import constants
from utils.gif_img_process import read_gif_url


@logger.catch
def spider_gif_images(keyword, chrome_driver):
    """
    抓取动态资源
    :param keyword:
    :param chrome_driver:  chrome驱动
    :return:
    """
    api_urls = []

    # 切换到开发者工具窗口并获取网络请求的API地址
    requests = chrome_driver.execute_script("return window.performance.getEntriesByType('resource')")
    for request in requests:
        if request['initiatorType'] == 'fetch' and "img-zip-ugoira" in request['name']:
            api_urls.append(request['name'])
            logger.success(f"spider gif zip url: {request['name']}")
    # logger.info("write url to txt!")
    txt_path_name = os.path.join(constants.data_path, "href_url")
    # 'https://sd.2021.host/artworks/115574488'
    if not os.path.exists(txt_path_name):
        os.makedirs(txt_path_name)
    if len(api_urls) == 0:
        logger.warning("no zip gif images data!")
        return False
    if read_gif_url(txt_path_name + "/" + keyword + "_zip.txt", api_urls):
        return True
    return False

# if __name__ == '__main__':
#     # spider_gif_url()
#     url = 'https://sd.2021.host/artworks/115574488'
#     # api_spider_link('https://sd.2021.host/artworks/115574488')
#     options = webdriver.ChromeOptions()
#     options.add_argument("--auto-open-devtools-for-tabs")
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)  # 替换为实际的网页URL
#
#     # 等待网页加载完成
#     time.sleep(7)  # 等待5秒钟，确保网页上的资源完全加载完成
#     spider_gif_images("lisa", driver)
