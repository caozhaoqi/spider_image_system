# 导入OS模块
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

# -----------------------系统调试------------------------------------
DEBUG = True
# -----------------------日志-----------------------------------------
LOG_DIR = os.path.join(os.getcwd(), f'./log_dir/sis_{time.strftime("%Y-%m-%d")}.log')
LOG_FORMAT = '<level>{level: <8}</level>  <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <cyan>{name}</cyan>:<cyan>{' \
             'function}</cyan> - <level>{message}</level> '
