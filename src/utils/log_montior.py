import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

import glob
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from run import constants

# 定义日志文件路径模式
LOG_FILE_PATTERN = 'log-*.log'
LOG_DIR = constants.basic_path + "log_dir/"  # 日志文件所在的目录


# 找到最新日期的日志文件
@logger.catch
def find_latest_log_file(pattern, directory):
    """

    :param pattern:
    :param directory:
    :return:
    """
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)  # 按修改时间排序
    return files[0]


# 定义一个事件处理器类，用于监控文件变化
class LogFileHandler(FileSystemEventHandler):
    """

    """

    def __init__(self, log_file):
        """

        :param log_file:
        """
        self.log_file = log_file
        self.last_modified = time.time()

    def on_modified(self, event):
        """

        :param event:
        :return:
        """
        if event.src_path == self.log_file:
            self.last_modified = time.time()

    def check_for_timeout(self, timeout):
        """

        :param timeout:
        :return:
        """
        if time.time() - self.last_modified > timeout:
            constants.log_no_output_flag = True
            logger.warning(f"警告：文件 {self.log_file} 已超过 {timeout // 60} 分钟没有输出。")


@logger.catch
def log_mon_war():
    """

    :return:
    """
    logger.info("log monitor start...")
    # 设置无输出超时时间（例如，5分钟）
    global handler
    TIMEOUT = constants.detect_timeout_auto

    # 初始化最新日志文件路径
    latest_log_file = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
    # 创建事件处理器实例
    if latest_log_file:
        handler = LogFileHandler(latest_log_file)
    else:
        logger.error("未找到匹配的日志文件，请检查日志文件命名是否正确或日志文件是否存在。")
        exit(1)

    # 创建观察者实例并添加事件处理器
    observer = Observer()
    observer.schedule(handler, path=LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            # 定期检查是否超时
            handler.check_for_timeout(TIMEOUT)

            # 休眠一段时间再检查
            time.sleep(TIMEOUT)  # 每分钟检查一次

            # 定期检查是否有新的日志文件
            new_latest_log_file = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
            if new_latest_log_file != latest_log_file:
                # 停止对旧文件的监控
                observer.unschedule(handler)
                # 更新日志文件路径
                latest_log_file = new_latest_log_file
                # 重新安排对新文件的监控
                observer.schedule(handler, path=LOG_DIR, recursive=False)
                logger.debug(f"已开始监控新日志文件：{latest_log_file}")

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
