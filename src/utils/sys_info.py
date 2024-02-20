import psutil
import os
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
        if cpu_percent is None:
            cpu_percent = 0
        if total_percent is None or total_percent == 0.0:
            total_percent = 1
        per = cpu_percent / total_percent * 100  # 计算占用百分比
        return per


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
    return send_bytes, receive_bytes


@logger.catch
def get_network_io_speed(process_name):
    # 找到与给定名称匹配的进程
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process_id = proc.info['pid']
            break
    else:
        raise ValueError(f"Process {process_name} not found")

    # 获取初始网络I/O统计信息
    initial_io = psutil.Process(process_id).io_counters()
    initial_bytes_sent = initial_io.bytes_sent
    initial_bytes_recv = initial_io.bytes_recv
    initial_time = time.time()

    # 等待一段时间（例如1秒）
    time.sleep(1)

    # 获取最终网络I/O统计信息
    final_io = psutil.Process(process_id).io_counters()
    final_bytes_sent = final_io.bytes_sent
    final_bytes_recv = final_io.bytes_recv
    final_time = time.time()

    # 计算时间差
    time_delta = final_time - initial_time

    # 计算上传和下载速度（Bytes/s）
    recv_speed = (final_bytes_recv - initial_bytes_recv) / time_delta if time_delta > 0 else 0
    send_speed = (final_bytes_sent - initial_bytes_sent) / time_delta if time_delta > 0 else 0

    return recv_speed, send_speed


if __name__ == '__main__':
    send_speed, recv_speed = get_network_io_speed("cmd.exe")
    print(f"Upload Speed: {send_speed} Bytes/s")
    print(f"Download Speed: {recv_speed} Bytes/s")
