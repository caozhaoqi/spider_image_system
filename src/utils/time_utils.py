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


@logger.catch
def random_fw_time(fire_wall_time):
    """

    :param fire_wall_time:
    :return:
    """
    random_delay = random.randint(1, fire_wall_time)
    return random_delay


@logger.catch
def sys_sleep_time(driver, sleep_time, img_flag):
    """

    :param driver:
    :param img_flag:
    :param sleep_time:
    :return:
    """
    try:
        if img_flag:
            time.sleep(sleep_time)
        else:
            driver.implicitly_wait(sleep_time)
    except Exception as e:
        logger.warning(f"sys_sleep_time unknown error, detail: {e} ")
        return False
    return True
