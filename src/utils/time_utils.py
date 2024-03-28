import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import time
from loguru import logger


@logger.catch
def id_generate_time():
    """
    生成随机id
    :return:随机后id
    """
    base_time = int(time.time())
    rad_num = random.randint(1, 10) * 1000 + random.randint(1, 10) * 100 + random.randint(1, 10) * 10 + random.randint(
        1, 10) * 1
    request_id = str(base_time) + str(rad_num)
    return str(request_id + "_")


@logger.catch
def time_to_utc(time_str):
    """

    :param time_str:
    :return:
    """
    mtime = time.localtime(time_str)
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", mtime)
    return formatted_time
