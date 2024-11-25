import os
import sys
from pathlib import Path
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import platform
from loguru import logger
from run.constants import (
    sis_log_level, 
    build_date,
    sis_server_version, 
    publish_date
)
from log.log_base import LOG_DIR
from log.log_config import InterceptHandler, format_record
from utils.version_control import compare_versions_with_pre_release, download_new_version


@logger.catch
def log_record() -> bool:
    """Configure and initialize logging
    
    Returns:
        bool: True if logging setup successful
    """
    # Configure logging handlers
    logging.getLogger().handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    # Configure loguru handlers
    logger.configure(handlers=[{
        "sink": sys.stdout,
        "level": sis_log_level,
        "format": format_record
    }])
    
    # Add rotating file handler
    logger.add(
        LOG_DIR,
        encoding='utf-8',
        rotation="00:00",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("------------------------------Log start record-------------------------------")
    logger.debug(f'Current SIS log file path: {LOG_DIR}')
    
    return True


@logger.catch
def check_version_update() -> bool:
    """Check and update SIS version if newer version available
    
    Returns:
        bool: True if update successful, False otherwise
    """
    if compare_versions_with_pre_release(sis_server_version, sis_server_version) == 0:
        logger.info(f"Current version {sis_server_version} is newest version!")
        return False
        
    logger.info(f"Found new version: {sis_server_version}, updating software...")
    
    if download_new_version(sis_server_version):
        logger.success("New version downloaded successfully. Please restart to apply update.")
        return True
        
    logger.warning(f"Update failed, continuing with version {sis_server_version}")
    return False


@logger.catch
def sys_info_select() -> None:
    """Log system information"""
    logger.info("System Information:")
    system_info = {
        "Python version": sys.version,
        "OS and version": platform.platform(),
        "OS version": platform.version(),
        "OS name": platform.system(),
        "OS architecture": platform.architecture(),
        "Machine type": platform.machine(),
        "Hostname": platform.node(),
        "CPU type": platform.processor(),
        "System info": platform.uname()
    }
    
    for key, value in system_info.items():
        logger.info(f"{key}: {value}")


@logger.catch
def check_version() -> bool:
    """Log SIS version information
    
    Returns:
        bool: True if version check successful
    """
    logger.info(f"System started, SIS version: {sis_server_version}")
    return True
