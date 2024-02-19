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
def get_cpu_usage_percentage():
    # process = psutil.Process(os.getpid())
    process = psutil.Process(os.getpid())
    if process.status() == psutil.STATUS_ZOMBIE or process.status() == psutil.STATUS_DEAD:
        logger.warning("Process is not running.")
    else:
        cpu_percent = process.cpu_percent(interval=1)
        total_percent = psutil.cpu_percent()  # 获取所有CPU核心的总的CPU占用百分比
        return cpu_percent / total_percent * 100  # 计算占用百分比


@logger.catch
def look_sys_info():
    """

    :return:
    """
    # 获取当前Python脚本的内存占用
    memory_usage = get_memory_usage()
    # logger.info(f"当前内存占用: {memory_usage:.2f} MB")
    cpu_usage = get_cpu_usage_percentage()
    # logger.info(f"当前CPU占用: {cpu_usage} %")
    # logger.debug(f"Bytes sent: {net_io_counters.write_bytes / 1024 / 1024} Mb/s")
    # logger.debug(f"Bytes received: {net_io_counters.read_bytes / 1024 / 1024} Mb/s")
    return memory_usage, cpu_usage


@logger.catch
def network_usage():
    """

    :return:
    """
    # 获取当前进程的 PID
    pid = os.getpid()

    # 获取当前进程的网络连接信息
    net_io_counters = psutil.Process(pid).io_counters()

    # 输出网络连接信息
    send_bytes = net_io_counters.write_bytes / 1024 / 1024
    receive_bytes = net_io_counters.read_bytes / 1024 / 1024
    # logger.debug(f"Bytes sent: {net_io_counters.write_bytes / 1024 / 1024} Mb/s")
    # logger.debug(f"Bytes received: {net_io_counters.read_bytes / 1024 / 1024} Mb/s")
    return send_bytes, receive_bytes


if __name__ == '__main__':
    # for i in range(10002):
    #     logger.debug(i)
    logger.info(get_cpu_usage_percentage())
    look_sys_info()
    network_usage()
