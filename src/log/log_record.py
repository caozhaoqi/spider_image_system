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
import run.constants
from utils.version_control import compare_versions_with_pre_release, download_new_version


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
    logger.add(LOG_DIR, encoding='utf-8', rotation="00:00", retention="30 days", compression="zip")
    logger.info("------------------------------log start record-------------------------------")
    logger.debug('Current SIS log file path: ' + LOG_DIR)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    return True


@logger.catch
def check_version_update():
    """
    check sis version update
    :return: update sis success flag
    """
    lasted_version = run.constants.sis_server_version
    if compare_versions_with_pre_release(run.constants.sis_server_version, lasted_version) != 0:
        logger.info(f"Find new version: {lasted_version}, will update software version.")
        if download_new_version(lasted_version):
            logger.success("New version download success, sis will quit! please run new version software!")
            return True
        else:
            logger.warning(f"Unknown error, will continued run: {run.constants.sis_server_version} version software!")
            return False
    else:
        logger.info(f"Current version: {run.constants.sis_server_version} is newest version!")
        return False


@logger.catch
def sys_info_select():
    """
    sys info print
    :return:
    """
    logger.info("Start print current system info: ")
    logger.info("Python version: " + sys.version)
    logger.info("OS and version info: " + platform.platform())
    logger.info('OS version: ' + platform.version())
    logger.info('OS name: ' + platform.system())
    logger.info('OS bit: ' + str(platform.architecture()))
    logger.info('PC type: ' + platform.machine())
    logger.info('PC name: ' + platform.node())
    logger.info('CPU type: ' + platform.processor())
    logger.info('PC other info: ' + str(platform.uname()))
    logger.info("End print current system info. ")
    # logger.info("now, start check version update update!")
    # check_version_update()


@logger.catch
def check_version():
    """
    print sis version msg
    :return:
    """
    # logger.info("-------------start print SIS version info---------------------------")
    logger.info("System started, current SIS version: " + sis_server_version)
    # logger.info("--------------------------------------------------------------------")
    # logger.info("current version build time: " + build_date)
    # logger.info("--------------------------------------------------------------------")
    # logger.info("current version publish time: " + publish_date)
    # logger.info("---------------end print SIS version info---------------------------")
    # sys_info_select()
    return True
