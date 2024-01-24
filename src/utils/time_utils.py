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
