# 导入OS模块
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH
from src.log.log_base import LOG_FORMAT

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pprint import pformat
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    log 格式化记录
    :param record:
    :return:
    """
    format_string = LOG_FORMAT

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string
