import os
import platform
import re
import sys
from pathlib import Path
from datetime import datetime
import time
from typing import Optional, List

from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.append(str(Path(__file__).parent.parent))

from run import constants
from utils.system_monitor import check_internet_connection
from utils.wx_push import wx_push_content

# 定义日志文件配置
LOG_FILE_PATTERN = 'sis_v*.log'
LOG_DIR = Path(constants.basic_path) / "log_dir"


@logger.catch
def find_latest_log_file(pattern: str, directory: Path) -> Optional[Path]:
    """查找最新的日志文件
    
    Args:
        pattern: 日志文件名匹配模式
        directory: 日志文件目录
        
    Returns:
        最新日志文件的路径,如果没找到则返回None
    """
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda x: x.stat().st_mtime)


@logger.catch 
def get_log_cur_time(log_file: Path) -> float:
    """获取日志文件最后一行的时间戳
    
    Args:
        log_file: 日志文件路径
        
    Returns:
        最后一行日志的时间戳,如果解析失败则返回当前时间戳
    """
    try:
        lines = log_file.read_text(encoding='utf-8', errors='replace').splitlines()
        if not lines:
            logger.debug("日志文件为空")
            return time.time()
            
        last_line = lines[-1]
        timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}', last_line)
        if timestamp_match:
            timestamp = datetime.strptime(timestamp_match.group(), "%Y-%m-%d %H:%M:%S.%f")
            return timestamp.timestamp()
            
        logger.warning(f"在日志最后一行未找到时间戳: {log_file}")
        return time.time()
        
    except Exception as e:
        logger.warning(f"读取日志文件失败: {log_file}, {e}")
        return time.time()


class LogFileHandler(FileSystemEventHandler):
    """日志文件监控处理器"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.last_modified = time.time()

    @logger.catch
    def on_modified(self, event):
        if Path(event.src_path) == self.log_file:
            self.last_modified = time.time()

    @logger.catch
    def check_for_timeout(self, timeout: int):
        """检查日志是否超时未更新
        
        Args:
            timeout: 超时时间(秒)
        """
        self.last_modified = get_log_cur_time(self.log_file)
        if time.time() - self.last_modified > timeout:
            constants.log_no_output_flag = True
            logger.warning(f"警告：文件 {self.log_file} 已超过 {timeout // 60} 分钟没有输出")


@logger.catch
def push_log_msg(log_file: Path):
    """推送日志消息到微信
    
    Args:
        log_file: 日志文件路径
    """
    last_lines = read_last_lines(log_file)
    msg = f"System info: {platform.node()}\nCurrent read new log:\n{last_lines}"
    wx_push_content(msg)
    logger.debug(f"已推送日志消息到微信: {log_file}")


@logger.catch
def read_last_lines(log_file: Path, n: int = 1000) -> str:
    """读取日志文件的最后n行
    
    Args:
        log_file: 日志文件路径
        n: 读取行数
        
    Returns:
        最后n行内容
    """
    if not log_file.stat().st_size:
        return ""
        
    with open(log_file, 'rb') as f:
        f.seek(0, os.SEEK_END)
        block_size = 1024
        blocks = []
        
        while f.tell() > 0 and len(blocks) * block_size < n * 100:
            step = min(block_size, f.tell())
            f.seek(-step, os.SEEK_CUR)
            blocks.append(f.read(step))
            f.seek(-step, os.SEEK_CUR)
            
        content = b''.join(reversed(blocks))
        lines = content.decode('utf-8', errors='replace').splitlines()[-n:]
        return '\n'.join(lines)


@logger.catch
def log_mon_war(spider_thread_obj):
    """日志监控主函数
    
    Args:
        spider_thread_obj: 爬虫线程对象
    """
    logger.info("日志监控启动...")
    
    timeout = constants.detect_timeout_auto
    
    # 初始化监控
    latest_log = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
    if not latest_log:
        logger.error("未找到匹配的日志文件")
        return
        
    handler = LogFileHandler(latest_log)
    observer = Observer()
    observer.schedule(handler, str(LOG_DIR), recursive=False)
    observer.start()

    try:
        while True:
            handler.check_for_timeout(timeout)
            
            # 检查网络连接
            if not check_internet_connection():
                logger.error("网络连接断开,停止爬虫线程")
                spider_thread_obj.stop()
                constants.stop_download_image_flag = True
                constants.scheduled_download_program_flag = False 
                constants.JM_SD_auto_flag = False
                wx_push_content("网络连接断开,停止爬虫线程")
            elif not spider_thread_obj.is_running():
                logger.success("网络恢复,重启爬虫线程")
                constants.scheduled_download_program_flag = True
                spider_thread_obj.resume()
                spider_thread_obj.run()
                wx_push_content("网络恢复,重启爬虫线程")
                
            logger.info(f"爬虫线程运行状态: {spider_thread_obj.is_running()}")
            
            # 检查日志输出
            if constants.log_no_output_flag and constants.internet_connect_status:
                spider_thread_obj.pause()
                spider_thread_obj.resume()
                spider_thread_obj.run()
                logger.warning(f"日志无输出,重启爬虫线程,状态: {spider_thread_obj.is_running()}")
                constants.log_no_output_flag = False
                
            time.sleep(timeout)
            
            # 检查新日志文件
            new_log = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
            if new_log != latest_log:
                observer.unschedule_all()
                latest_log = new_log
                handler = LogFileHandler(latest_log)
                observer.schedule(handler, str(LOG_DIR), recursive=False)
                logger.debug(f"开始监控新日志文件: {latest_log}")
                
            push_log_msg(new_log)
            logger.debug("完成当前监控循环")

    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()
