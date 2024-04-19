import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil
import time

from loguru import logger

# 设置资源使用的警告阈值
from run import constants

MEMORY_THRESHOLD = 0.8  # 内存使用阈值（90%）
CPU_THRESHOLD = 0.96  # CPU使用阈值（90%）
NETWORK_THRESHOLD = 10 * 1024 * 1024  # 网络带宽阈值（1MB/s）
DISK_USAGE_THRESHOLD = 0.99  # 设置存储使用警告阈值（例如，90% 使用率）

# 上次检查的资源使用情况
last_memory_usage = 0
last_cpu_usage = 0
last_disk_usage = 0
last_network_usage = 0


# 检查系统盘存储使用情况的函数
@logger.catch
def check_disk_usage():
    """

    :return:
    """
    global DISK_USAGE_THRESHOLD
    # 获取系统盘使用情况
    disk_usage = psutil.disk_usage('/')
    # 计算使用率
    disk_percent_used = disk_usage.percent / 100.0
    # 检查是否超过阈值
    if disk_percent_used > DISK_USAGE_THRESHOLD:
        # 输出警告信息
        logger.error(
            f"Warning: System disk usage is above {DISK_USAGE_THRESHOLD * 100}%. Current usage: {disk_percent_used * 100}%.")


# 检查内存使用情况的函数
@logger.catch
def check_memory_usage():
    """

    :return:
    """
    global last_memory_usage, MEMORY_THRESHOLD
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    if memory_percent > MEMORY_THRESHOLD:
        logger.error(
            "Warning: Memory usage is above {}%. Current usage: {}%".format(MEMORY_THRESHOLD * 100, memory_percent))
    last_memory_usage = memory_percent


# 检查CPU使用情况的函数
@logger.catch
def check_cpu_usage():
    """

    :return:
    """
    global last_cpu_usage, CPU_THRESHOLD
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent / 100 > CPU_THRESHOLD:
        logger.error("Warning: CPU usage is above {}%. Current usage: {}%".format(CPU_THRESHOLD * 100, cpu_percent))
    last_cpu_usage = cpu_percent


# 检查网络带宽的函数
@logger.catch
def check_network_usage():
    """

    :return:
    """
    global last_network_usage, NETWORK_THRESHOLD
    # 获取网络接口的发送和接收字节数
    net_io_counters = psutil.net_io_counters(pernic=True)
    total_sent = sum(nic.bytes_sent for nic in net_io_counters.values())
    total_recv = sum(nic.bytes_recv for nic in net_io_counters.values())
    # 计算总带宽（发送和接收），并转换为MB/s
    network_usage = (total_sent + total_recv) / (1024 * 1024)
    # 检查是否超过了阈值
    if network_usage > NETWORK_THRESHOLD:
        logger.error(
            f"Warning: Network usage is above {NETWORK_THRESHOLD / (1024 * 1024)} MB/s. Current usage: {network_usage / (1024 * 1024)} MB/s")
    last_network_usage = network_usage


@logger.catch
def check_top_processes():
    """
    检查系统中CPU、内存和网络I/O占用率最高的前10个进程的详情。
    """
    # 获取所有进程，并计算CPU和内存占用率
    processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
    # 对进程按CPU占用率进行排序
    sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)

    # 初始化一个空的列表来存储前10个进程的详情
    top_processes = []

    # 遍历进程，收集前10个的详细信息
    for process in sorted_processes:
        try:
            # 获取进程的PID和名称
            pid = process.info['pid']
            name = process.info['name']

            cpu_percent = process.cpu_percent()
            # 获取进程的CPU和内存占用率
            memory_info = process.memory_info()
            memory_percent = memory_info.rss / (1024 * 1024)

            # 尝试获取网络I/O统计信息
            try:
                net_io_counters = process.io_counters()

                send_bytes = net_io_counters.write_bytes / 1024 / 1024
                receive_bytes = net_io_counters.read_bytes / 1024 / 1024
                # 注意：这里提供的是总的网络I/O，不是实时的带宽占用
                net_io = send_bytes + receive_bytes
            except AttributeError:
                net_io = 0  # 如果无法获取，则设为0

            # 将进程详情添加到列表中
            top_processes.append({
                'PID': pid,
                'Name': name,
                'CPU Usage': cpu_percent,
                'Memory Usage': memory_percent,
                'Network IO': net_io
            })

            # 只收集前10个进程的信息
            if len(top_processes) >= 10:
                break

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 进程可能已经结束，或者我们没有权限访问它
            continue
    logger.warning("-----------------start output system resources msg---------------------------------")
    for proc in top_processes:
        logger.info(proc)
    logger.warning("-----------------end output system resources msg------------------------------------")
    return True


# 示例使用

@logger.catch
def sys_mon():
    """

    :return:
    """
    logger.info("system monitor start...")
    while True:
        # 检查CPU使用率
        check_cpu_usage()

        # 检查网络带宽
        check_network_usage()

        check_memory_usage()

        check_disk_usage()

        check_top_processes()

        # 等待一段时间再次检查（例如，每秒检查一次）
        time.sleep(constants.detect_timeout_auto * 5)

#
# if __name__ == '__main__':
#     check_top_processes()
