import psutil
import os

from loguru import logger


@logger.catch
def get_memory_usage():
    """
    get memory info
    :return:
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)


@logger.catch
def get_cpu_usage():
    """
    get cpu info
    :return:
    """
    process = psutil.Process(os.getpid())
    cpu_times = process.cpu_times()
    return cpu_times.user.__str__()  # 返回用户态CPU时间，单位为秒


@logger.catch
def look_sys_info():
    """

    :return:
    """
    # 获取当前Python脚本的内存占用
    memory_usage = get_memory_usage()
    logger.info(f"当前内存占用: {memory_usage:.2f} MB")
    cpu_usage = get_cpu_usage()
    logger.info(f"当前CPU占用: {cpu_usage} 秒")


def ensure_list_of_floats(data):
    if isinstance(data, list):
        return [float(item) for item in data]
    elif isinstance(data, float):
        return [data]
    else:
        raise ValueError("Input must be a list of floats or a single float.")
