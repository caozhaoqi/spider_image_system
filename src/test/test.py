import re
from datetime import datetime

from loguru import logger


def test_m(last_line):
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}'
    match = re.search(timestamp_pattern, last_line)

    if match:
        last_timestamp = match.group()
        # 将字符串转换为datetime对象
        last_log_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S.%f")

        # 将datetime对象转换为时间戳（毫秒）
        timestamp = last_log_time.timestamp() * 1000  # 得到毫秒数

        # 如果需要更高的精度（微秒），可以加上微秒部分
        # 注意：这里假设datetime对象中的微秒部分是我们需要的
        microseconds = last_log_time.microsecond / 1000000  # 微秒转为秒的小数部分

        # 加上微秒部分到时间戳
        timestamp += microseconds
        last_timestamp = timestamp
        # logger.warning(f"最后一行日志的时间戳是: {last_timestamp}")
    else:
        logger.warning("在最后一行日志中未找到时间戳。")


if __name__ == '__main__':
    test_m("2024-04-22 10:03:43.633 | WARNING  | ui_event.base_event:auto_spider_img_thread:217 - block sd.vv50.de "
           "domain, will retry! cur retry time: 5.0 minutes.")
