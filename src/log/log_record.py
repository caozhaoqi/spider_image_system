import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import platform
import sys
from loguru import logger
from run.constants import sis_log_level, build_date, sis_server_version, publish_date
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
    # 创建一个RotatingFileHandler，设置日志文件大小为1MB，备份数量为5
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": sis_log_level, "format": format_record}])
    logger.add(LOG_DIR, encoding='utf-8', rotation="00:00",  retention="30 days", compression="zip")
    logger.debug('SIS log file started record, current log file: ' + LOG_DIR)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    return True


@logger.catch
def sys_info_select():
    """
    sys info print
    :return:
    """
    logger.info("start print current system info: ")
    logger.info("python version: " + sys.version)
    logger.info("os and version info: " + platform.platform())
    logger.info('os version: ' + platform.version())
    logger.info('os name: ' + platform.system())
    logger.info('os bit: ' + str(platform.architecture()))
    logger.info('pc type: ' + platform.machine())
    logger.info('pc name: ' + platform.node())
    logger.info('CPU type: ' + platform.processor())
    logger.info('pc other info: ' + str(platform.uname()))
    logger.info("end print current system info. ")


@logger.catch
def check_version():
    """
    print sis version msg
    :return:
    """
    logger.info("-------------start print SIS version info---------------------------")
    logger.info("system started, current SIS version: " + sis_server_version)
    logger.info("--------------------------------------------------------------------")
    logger.info("current version build time: " + build_date)
    logger.info("--------------------------------------------------------------------")
    logger.info("current version publish time: " + publish_date)
    logger.info("---------------end print SIS version info---------------------------")
    sys_info_select()
    return True
