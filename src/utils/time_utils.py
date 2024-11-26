"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import time
from typing import Union
from loguru import logger


@logger.catch
def id_generate_time() -> str:
    """生成基于时间戳的随机ID
    
    Returns:
        str: 时间戳+随机数组成的ID字符串,末尾带下划线
    """
    base_time = int(time.time())
    # 生成4位随机数
    rad_num = sum(random.randint(1, 10) * (10 ** i) for i in range(4))
    return f"{base_time}{rad_num}_"


@logger.catch 
def time_to_utc(timestamp: float) -> str:
    """将时间戳转换为UTC格式字符串
    
    Args:
        timestamp: Unix时间戳
        
    Returns:
        str: 格式化的UTC时间字符串(YYYY-MM-DD HH:MM:SS)
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


@logger.catch
def random_fw_time(fire_wall_time: int) -> int:
    """生成随机延迟时间
    
    Args:
        fire_wall_time: 最大延迟时间(秒)
        
    Returns:
        int: 1到fire_wall_time之间的随机延迟秒数
    """
    return random.randint(1, fire_wall_time)


@logger.catch
def sys_sleep_time(driver: object, sleep_time: float, img_flag: bool) -> bool:
    """系统休眠或等待
    
    Args:
        driver: WebDriver对象
        sleep_time: 休眠/等待时间(秒)
        img_flag: True使用time.sleep,False使用driver.implicitly_wait
        
    Returns:
        bool: 休眠/等待是否成功
    """
    try:
        if img_flag:
            time.sleep(sleep_time)
        else:
            driver.implicitly_wait(sleep_time)
        return True
    except Exception as e:
        logger.warning(f"系统休眠出错: {e}")
        return False


@logger.catch
def get_cur_time() -> str:
    """获取当前UTC时间(Asia/Shanghai)
    
    Returns:
        str: 当前UTC时间字符串
    """
    return time_to_utc(time.time())
