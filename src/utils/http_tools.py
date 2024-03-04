import os
import sys
import urllib

import urllib3.util
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re


@logger.catch
def is_valid_url(http_url):
    """
    url valid
    :param http_url:
    :return: True or False
    """
    pattern = r'^https?://.+$'
    if re.match(pattern, http_url):
        return True
    else:
        return False


@logger.catch
def image_url_re(image_url):
    """
    filename = urllib.parse.urlsplit(url).path.split('/')[-1]
    提取link中的图片name
    :param image_url:
    :return:
    """
    import re

    result_url = image_url.split('/')[-1]
    if result_url.endswith('.jpg') or result_url.endswith('.png'):
        return result_url
    else:
        result_url = re.search(r'/([^/?#]+)$', image_url).group(1)
        if result_url.endswith('.jpg') or result_url.endswith('.png'):
            return result_url
        else:
            logger.warning(f"parser error, return source url:{image_url}")
            return image_url



if __name__ == '__main__':
    url = "https://pixiv.srpr.cc/img-master/img/2024/01/29/15/41/31/115584905_p1_master1200.jpg"
    image_url_re(url)
