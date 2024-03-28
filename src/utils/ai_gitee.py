import os
import sys

from run import constants

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from loguru import logger
from ui_event.get_url import spider_artworks_url

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
    # if response.status_code != '200':
    #     logger.info(response.content)
    #     return None
    return response.json()


@logger.catch
def auto_detect():
    """

    :return:
    """
    constants.stop_spider_url_flag = False
    while True:
        spider_artworks_url(None, 'klee')


# @logger.catch
# def en_to_cn(output):
#     """
# 
#     :param output:
#     :return:
#     """
#     from googletrans import Translator
#
#     # 假设这是你的原始列表
#     labels_with_scores = [
#         {'label': 'comic book', 'score': 0.27064889669418335},
#         {'label': 'gown', 'score': 0.17459899187088013},
#         {'label': 'flagpole, flagstaff', 'score': 0.13303591310977936},
#         {'label': 'cloak', 'score': 0.1200503334403038},
#         {'label': 'mask', 'score': 0.05657108873128891}
#     ]
#
#     # 创建一个Translator实例
#     translator = Translator()
#
#     # 遍历列表，翻译并打印中文标签
#     for item in labels_with_scores:
#         # 使用translator.translate()方法来翻译标签
#         translated_label = translator.translate(item['label'], dest='zh-cn').text
#         print(f"英文标签: {item['label']}, 得分: {item['score']}, 中文标签: {translated_label}")


if __name__ == '__main__':
    # img_list = find_images(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data")
    # for img in img_list:
    #     output = query(
    #         img)
    #     logger.info(img + ": " + output)
    auto_detect()
    # en_to_cn('')
