import os
import platform
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
import re
from datetime import datetime
import glob
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from run import constants
from utils.system_monitor import check_internet_connection
from utils.wx_push import wx_push_content

# 定义日志文件路径模式
LOG_FILE_PATTERN = 'sis_v*.log'
LOG_DIR = os.path.join(constants.basic_path, "log_dir")  # 日志文件所在的目录


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


@logger.catch
def get_log_cur_time(log_file_path):
    """

    :param log_file_path:
    :return:
    """

    # 打开日志文件并读取最后一行
    last_timestamp = time.time()
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='replace') as log_file:
            lines = log_file.readlines()
            if lines:
                last_line = lines[-1]  # 最后一行
            else:
                logger.debug("日志文件为空。")
                last_line = None
    except FileNotFoundError:
        logger.warning(f"文件 {log_file_path} 未找到。")
        last_line = None

    # 如果最后一行存在，则提取时间戳
    if last_line:
        # 假设时间戳格式为 "YYYY-MM-DD HH:MM:SS.sss"
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}'
        match = re.search(timestamp_pattern, last_line)

        if match:
            last_timestamp = match.group()
            last_log_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S.%f")

            timestamp = last_log_time.timestamp()

            timestamp_float = float(timestamp)
            last_timestamp = timestamp_float
            # logger.success(f"时间戳已匹配, file: {log_file_path}, 最后一行日志的时间戳是: {last_log_time}")
        else:
            logger.warning(f"在日志: {log_file_path}, 最后一行日志中未找到时间戳。")
    else:
        logger.warning(f"无法读取: {log_file_path}, 最后一行日志。")

    return last_timestamp


class LogFileHandler(FileSystemEventHandler):
    """

    """

    def __init__(self, log_file):
        """

        :param log_file:
        """
        self.log_file = log_file
        self.last_modified = time.time()

    @logger.catch
    def on_modified(self, event):
        """

        :param event:
        :return:
        """
        if event.src_path == self.log_file:
            self.last_modified = time.time()

    @logger.catch
    def check_for_timeout(self, timeout):
        """

        :param timeout:
        :return:
        """
        self.last_modified = get_log_cur_time(self.log_file)
        cur_time = time.time()
        if cur_time - self.last_modified > timeout:
            # if time.time() - time.time() > timeout:  # test
            constants.log_no_output_flag = True
            logger.warning(f"警告：文件 {self.log_file} 已超过 {timeout // 60} 分钟没有输出。")


@logger.catch
def push_log_msg(new_latest_log_file):
    """

    """

    last_lines = read_last_lines(new_latest_log_file, n=1000)
    lines_header = platform.node()
    wx_push_content(f"System info: {lines_header}. \n Current read new log: \n {last_lines}")
    logger.debug(f"Already push log: {new_latest_log_file} msg to WeChat.")
    # pass


@logger.catch
def read_last_lines(log_file, n=1000):
    """

    读取日志文件的最后n行
    """
    with open(log_file, 'rb') as f:
        size = os.path.getsize(log_file)
        if size == 0:
            return []
        blocks = -1  # 最后一块
        step = 1024  # 步长
        while size > step:
            size -= step
            if size < 0:
                blocks -= 1
                step = 1024
            elif size == 0:
                blocks -= 1
                step = 1
            if blocks < 0:
                break
        f.seek(size)
        lines = f.readlines()
        if size != 0 and lines and lines[-1]:
            lines.append(f.readline())
    return lines[-n:]


@logger.catch
def log_mon_war(spider_thread_obj):
    """

    :param spider_thread_obj:
    :return:
    """
    logger.info("Log monitor start...")
    # 设置无输出超时时间（例如，5分钟）
    handler = None
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

            ret = check_internet_connection()
            # 无网络，暂停爬虫
            if not ret:
                logger.error("No internet connect, stop spider image thread and download thread!")
                spider_thread_obj.stop()
                constants.stop_download_image_flag = True
                constants.scheduled_download_program_flag = False
                constants.JM_SD_auto_flag = False
                wx_push_content("No internet connect, stop spider image thread and download thread!")
            else:
                # 恢复网络，恢复爬虫
                if not spider_thread_obj.is_running():
                    logger.success("Internet resume connect, resume spider image thread and download thread.")
                    constants.scheduled_download_program_flag = True
                    spider_thread_obj.resume()
                    spider_thread_obj.run()
                    wx_push_content("Internet resume connect, resume spider image thread and download thread.")
            logger.info(f"Spider_thread_obj.is_running flag value: {spider_thread_obj.is_running()}")
            if constants.log_no_output_flag and constants.internet_connect_status:
                # 在某个时候，您可能想要暂停线程
                spider_thread_obj.pause()
                spider_thread_obj.resume()
                spider_thread_obj.run()
                logger.warning(
                    f"Log no output, spider threading status: {spider_thread_obj.is_running()}, re start spider ing...")
                constants.log_no_output_flag = False
            # 休眠一段时间再检查
            time.sleep(TIMEOUT)  # 每分钟检查一次

            # 定期检查是否有新的日志文件
            new_latest_log_file = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
            if new_latest_log_file != latest_log_file:
                # 停止对旧文件的监控
                try:
                    observer.unschedule(handler)
                except KeyError:
                    logger.warning("Failed to unschedule the LogFileHandler. It might not be scheduled.")
                # 更新日志文件路径
                latest_log_file = new_latest_log_file
                # 重新安排对新文件的监控
                observer.schedule(handler, path=LOG_DIR, recursive=False)
                logger.debug(f"已开始监控新日志文件：{latest_log_file}")

            #         push log end 10 line to WeChat
            push_log_msg(new_latest_log_file)
            logger.debug("End current loop log monitor.")

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
