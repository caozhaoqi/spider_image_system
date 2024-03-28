import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


@logger.catch
def scan_img_txt(path):
    """
    sacn img txt from point path
    :param path:
    :return:
    """

    # txt
    img_txt_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('_img.txt') or file.endswith('_img_result.txt'):
                img_txt_files.append(os.path.join(root, file))
    # single txt
    img_list_set = []
    for img_txt in img_txt_files:
        with open(img_txt, 'r', encoding='utf-8', errors='replace') as f:
            img_list_set.append(f.readlines())
    # img
    img_list = []
    for img in img_list_set:
        for img_detail in img:
            img_list.append(img_detail)
    return list(set(img_list))
