import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil
import time
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
    return cpu_times.user.__str__()


@logger.catch
def get_cpu_usage_percentage():
    """

    :return:
    """
    process = psutil.Process(os.getpid())
    if process.status() == psutil.STATUS_ZOMBIE or process.status() == psutil.STATUS_DEAD:
        logger.warning("Process is not running.")
    else:
        cpu_percent = process.cpu_percent(interval=1)
        total_percent = psutil.cpu_percent()
        if cpu_percent is None:
            cpu_percent = 0
        if total_percent is None or total_percent == 0.0:
            total_percent = 1
        per = cpu_percent / total_percent * 100
        return per


@logger.catch
def look_sys_info():
    """

    :return:
    """
    memory_usage = get_memory_usage()
    cpu_usage = get_cpu_usage_percentage()
    return memory_usage, cpu_usage


@logger.catch
def network_usage():
    """

    :return:
    """
    pid = os.getpid()

    net_io_counters = psutil.Process(pid).io_counters()

    send_bytes = net_io_counters.write_bytes / 1024 / 1024
    receive_bytes = net_io_counters.read_bytes / 1024 / 1024
    return send_bytes, receive_bytes


@logger.catch
def get_network_io_speed(process_name):
    """

    :param process_name:
    :return:
    """
    # 找到与给定名称匹配的进程
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process_id = proc.info['pid']
            break
    else:
        raise ValueError(f"Process {process_name} not found")

    initial_io = psutil.Process(process_id).io_counters()
    initial_bytes_sent = initial_io.bytes_sent
    initial_bytes_recv = initial_io.bytes_recv
    initial_time = time.time()

    time.sleep(1)

    final_io = psutil.Process(process_id).io_counters()
    final_bytes_sent = final_io.bytes_sent
    final_bytes_recv = final_io.bytes_recv
    final_time = time.time()

    time_delta = final_time - initial_time

    recv_speed = (final_bytes_recv - initial_bytes_recv) / time_delta if time_delta > 0 else 0
    send_speed = (final_bytes_sent - initial_bytes_sent) / time_delta if time_delta > 0 else 0

    return recv_speed, send_speed

#
# if __name__ == '__main__':
#     send_speed, recv_speed = get_network_io_speed("cmd.exe")
#     print(f"Upload Speed: {send_speed} Bytes/s")
#     print(f"Download Speed: {recv_speed} Bytes/s")
