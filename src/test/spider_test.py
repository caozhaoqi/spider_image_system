import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from loguru import logger
from ui_event.get_url import spider_artworks_url
from run import constants

API_URL = "https://ai.gitee.com/api/inference-api/models/hf-models/resnet-50"
headers = {
    "Authorization": "Bearer eyJpc3MiOiJodHRwczovL2FpLmdpdGVlLmNvbSIsInN1YiI6IjQ3OSJ9"
                     ".rxFDc0Vv5ZoJWdxgpuvsWakiUg_zlE_Ypxc1Gc4LvWrZlI7wBVX5gIB8O_N8gE58w5U0np8L4lKH2d5PYNU6Bg",
    "Content-Type": "image/jpeg"
}


@logger.catch
def query(filename):
    """

    :param filename:
    :return:
    """
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()


@logger.catch
def auto_detect():
    """

    :return:
    """
    # constants.spider_mode = 'auto'
    while True:
        constants.stop_spider_url_flag = False
        spider_artworks_url(None, 'teriri')


if __name__ == '__main__':
    # img_list = find_images(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data")
    # for img in img_list:
    #     output = query(
    #         img)
    #     logger.info(img + ": " + output)
    auto_detect()
