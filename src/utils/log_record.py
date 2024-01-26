import logging
import platform
import sys

from loguru import logger

from gui.constants import sis_log_level, build_date, sis_server_version, publish_date
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


@logger.catch
def sys_info_select():
    """
    sys info print
    :return:
    """
    logger.info("start out current system info :")
    logger.info("python_version: " + sys.version)
    logger.info("os and version info: " + platform.platform())
    logger.info('get os version: ' + platform.version())
    logger.info('get os name: ' + platform.system())
    logger.info('os bit: ' + str(platform.architecture()))
    logger.info('compute type: ' + platform.machine())
    logger.info('compute name: ' + platform.node())
    logger.info('CPU type: ' + platform.processor())
    logger.info('compute other info: ' + str(platform.uname()))
    logger.info("end out current system info .")


@logger.catch
def check_version():
    """
    out app version msg
    :return:
    """
    logger.info("-------------start print version info---------------------------")
    logger.info("system starting , current server version : " + sis_server_version)
    logger.info("---------------------------------------------------------------")
    logger.info("current version build date : "
                + build_date)
    logger.info("---------------------------------------------------------------")
    logger.info(" current version publish date: " + publish_date)
    logger.info("---------------end print version info---------------------------")
    sys_info_select()
