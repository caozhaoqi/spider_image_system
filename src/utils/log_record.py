import logging
import sys

from loguru import logger

from gui.constants import sis_log_level
from log.log_base import LOG_DIR
from log.log_config import InterceptHandler, format_record


@logger.catch
def log_record():
    """
    log output
    :return:
    """
    # 日志配置与捕获
    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": sis_log_level, "format": format_record}])
    logger.add(LOG_DIR, encoding='utf-8', rotation="12:00")
    logger.debug('python log system loaded , current log directory：' + LOG_DIR)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
