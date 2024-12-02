"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import subprocess
import sys
import time

import requests
import psutil
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import constants
from utils.sys_info import get_cur_os
from utils.wx_push import wx_push_content

# 系统资源阈值配置
THRESHOLDS = {
    'memory': 0.90,  # 内存使用阈值 90%
    'cpu': 0.90,     # CPU使用阈值 90%
    'network': 5 * 1024 * 1024,  # 网络带宽阈值 5MB/s
    'disk': 0.90     # 存储使用阈值 90%
}

# 监控状态
MONITOR_STATE = {
    'memory': 0,
    'cpu': 0, 
    'disk': 0,
    'network': 0
}

# 监控进程数量
PROCESS_COUNT = 5

@logger.catch
def check_disk_usage() -> None:
    """检查系统盘存储使用情况"""
    disk_usage = psutil.disk_usage('/')
    disk_percent = disk_usage.percent / 100.0
    
    if disk_percent > THRESHOLDS['disk']:
        logger.error(
            f"Warning: System disk usage is above {THRESHOLDS['disk']*100}%. "
            f"Current usage: {disk_percent*100}%"
        )

@logger.catch 
def check_memory_usage() -> None:
    """检查内存使用情况"""
    memory = psutil.virtual_memory()
    memory_percent = memory.percent / 100
    
    if memory_percent > THRESHOLDS['memory']:
        logger.error(
            f"Warning: Memory usage is above {THRESHOLDS['memory']*100}%. "
            f"Current usage: {memory_percent*100}%"
        )
        if reduce_sys_res_usage():
            logger.success("Successfully reduced memory usage on win32 system!")
            wx_push_content(
                f"Warning: Memory usage is above {THRESHOLDS['memory']*100}%, "
                f"memory usage reduced. Current usage: {memory_percent*100}%"
            )
    MONITOR_STATE['memory'] = memory_percent

@logger.catch
def check_cpu_usage() -> None:
    """检查CPU使用情况"""
    cpu_percent = psutil.cpu_percent(interval=1) / 100
    
    if cpu_percent > THRESHOLDS['cpu']:
        logger.error(
            f"Warning: CPU usage is above {THRESHOLDS['cpu']*100}%. "
            f"Current usage: {cpu_percent*100}%"
        )
        if reduce_sys_res_usage():
            logger.success("Successfully reduced CPU usage on win32 system!")
            wx_push_content(
                f"Warning: CPU usage is above {THRESHOLDS['cpu']*100}%, "
                f"CPU usage reduced. Current usage: {cpu_percent*100}%"
            )
    MONITOR_STATE['cpu'] = cpu_percent

@logger.catch
def reduce_sys_res_usage() -> bool:
    """降低系统资源使用"""
    try:
        if get_cur_os() == "win32":
            if not kill_process_win('taskkill /im chrome.exe /F'):
                logger.warning("Starting force kill chrome.exe process")
                kill_process_win("taskkill /im chrome.exe /F /T")
        else:
            kill_process_linux('chrome')
            kill_process_linux('chromedriver')
            kill_process_linux('webdriver')
        return True
    except Exception as e:
        logger.warning(f"Failed to reduce resource usage: {e}")
        return False

@logger.catch
def kill_process_win(command: str) -> bool:
    """结束Windows进程
    
    Args:
        command: 进程终止命令
        
    Returns:
        是否成功终止进程
    """
    import subprocess
    
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    try:
        if not stdout.decode('gbk'):
            logger.warning(f"Error: {stderr.decode('gbk').strip()}")
            return False
        logger.debug(f"Output: {stdout.decode('gbk').strip()}")
        return True
    except Exception:
        logger.warning(f"Error: {stderr.decode('gbk').strip()}")
        return False

@logger.catch
def kill_process_linux(process_name: str) -> None:
    """结束Linux进程
    
    Args:
        process_name: 进程名称
    """
    try:
        pid = subprocess.check_output(['pgrep', '-f', process_name]).decode('utf-8').strip()
        if pid:
            os.system(f'kill -9 {pid}')
            logger.success(f"Killed {process_name} with PID {pid} on Linux system")
    except Exception as e:
        logger.warning(f"Error killing {process_name}: {e} on Linux system")

@logger.catch
def check_network_usage() -> None:
    """检查网络带宽使用情况"""
    net_io = psutil.net_io_counters(pernic=True)
    total_bytes = sum(nic.bytes_sent + nic.bytes_recv for nic in net_io.values())
    network_usage = total_bytes / (1024 * 1024)  # Convert to MB
    
    if network_usage > THRESHOLDS['network']:
        logger.error(
            f"Warning: Network usage is above {THRESHOLDS['network']/(1024*1024)} MB/s. "
            f"Current usage: {network_usage/(1024*1024)} MB/s"
        )
    MONITOR_STATE['network'] = network_usage

@logger.catch
def check_internet_connection() -> bool:
    """检查互联网连接状态
    
    Returns:
        是否连接正常
    """
    try:
        response = requests.get('https://www.baidu.com')
        if response.status_code == 200:
            logger.info("Internet connection normal")
            constants.ProcessingConfig.internet_connect_status = True
            return True
    except Exception:
        constants.ProcessingConfig.internet_connect_status = False
        return False
    return False

@logger.catch
def check_top_processes() -> bool:
    """检查系统资源占用最高的进程"""
    processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
    sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)
    
    top_processes = []
    for process in sorted_processes[:PROCESS_COUNT]:
        try:
            pid = process.info['pid']
            name = process.info['name']
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            try:
                io_counters = process.io_counters()
                net_io = (io_counters.write_bytes + io_counters.read_bytes) / (1024 * 1024)
            except (psutil.AccessDenied, AttributeError):
                net_io = 0
                
            top_processes.append({
                'PID': pid,
                'Name': name,
                'CPU Usage': cpu_percent,
                'Memory Usage (MB)': memory_mb,
                'Network IO (MB)': net_io
            })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    logger.warning("----- System Resource Usage -----")
    for proc in top_processes:
        logger.info(proc)
    logger.warning("--------------------------------")
    
    return True

@logger.catch
def sys_mon() -> None:
    """系统资源监控主函数"""
    logger.info("System monitor starting...")
    logger.info(f"Resource detection interval: {constants.detect_timeout_auto}s")
    
    while True:
        time.sleep(constants.detect_timeout_auto)
        
        check_cpu_usage()
        check_network_usage() 
        check_memory_usage()
        check_disk_usage()
        check_top_processes()
