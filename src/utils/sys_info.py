"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import Tuple, Union

sys.path.append(str(Path(__file__).parent.parent))

import psutil
import time
from loguru import logger


@logger.catch
def get_memory_usage() -> float:
    """获取当前进程内存使用情况
    
    Returns:
        内存使用量(MB)
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)


@logger.catch
def get_cpu_usage() -> str:
    """获取当前进程CPU使用时间
    
    Returns:
        用户态CPU时间
    """
    process = psutil.Process(os.getpid())
    cpu_times = process.cpu_times()
    return str(cpu_times.user)


@logger.catch
def get_cpu_usage_percentage() -> Union[float, None]:
    """获取当前进程CPU使用率百分比
    
    Returns:
        CPU使用率百分比,进程未运行时返回None
    """
    process = psutil.Process(os.getpid())
    if process.status() in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
        logger.warning("进程未运行")
        return None
        
    cpu_percent = process.cpu_percent(interval=1) or 0
    total_percent = psutil.cpu_percent() or 1
    return (cpu_percent / total_percent) * 100


@logger.catch
def look_sys_info() -> Tuple[float, Union[float, None]]:
    """获取系统资源使用情况
    
    Returns:
        内存使用量(MB)和CPU使用率百分比的元组
    """
    memory_usage = get_memory_usage()
    cpu_usage = get_cpu_usage_percentage()
    return memory_usage, cpu_usage


@logger.catch
def network_usage() -> Tuple[float, float]:
    """获取当前进程网络IO使用量
    
    Returns:
        发送和接收字节数(MB)的元组
    """
    net_io = psutil.Process(os.getpid()).io_counters()
    send_bytes = net_io.write_bytes / (1024 * 1024)
    receive_bytes = net_io.read_bytes / (1024 * 1024)
    return send_bytes, receive_bytes


@logger.catch
def get_network_io_speed(process_name: str) -> Tuple[float, float]:
    """获取指定进程的网络IO速度
    
    Args:
        process_name: 进程名称
        
    Returns:
        接收和发送速度(字节/秒)的元组
        
    Raises:
        ValueError: 未找到指定进程时抛出
    """
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            process_id = proc.info['pid']
            break
    else:
        raise ValueError(f"未找到进程: {process_name}")

    process = psutil.Process(process_id)
    initial_io = process.io_counters()
    initial_time = time.time()

    time.sleep(1)

    final_io = process.io_counters()
    final_time = time.time()

    time_delta = final_time - initial_time
    if time_delta <= 0:
        return 0.0, 0.0

    recv_speed = (final_io.bytes_recv - initial_io.bytes_recv) / time_delta
    send_speed = (final_io.bytes_sent - initial_io.bytes_sent) / time_delta

    return recv_speed, send_speed


@logger.catch
def get_cur_os() -> str:
    """获取当前操作系统类型
    
    Returns:
        操作系统类型('win32'或'linux')
    """
    os_name = sys.platform
    return os_name if os_name == 'win32' else 'linux'

# if __name__ == '__main__':
#     send_speed, recv_speed = get_network_io_speed("cmd.exe")
#     print(f"上传速度: {send_speed} 字节/秒")
#     print(f"下载速度: {recv_speed} 字节/秒")
