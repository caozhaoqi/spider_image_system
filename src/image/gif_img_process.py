import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


@logger.catch
def read_gif_url(zip_txt_path, url_list):
    """
    from txt read url download zip to unzip img return img path
    :param url_list:
    :param zip_txt_path: zip url txt save
    :return:
    """
    for url_detail in url_list:
        with open(zip_txt_path, "a") as f:
            f.write(url_detail + "\n")
    return True
