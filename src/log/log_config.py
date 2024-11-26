"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
import logging
from pprint import pformat
from loguru import logger
from log.log_base import LOG_FORMAT

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging and redirect to loguru"""
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Intercept logging records and emit them through loguru
        
        Args:
            record: The logging record to handle
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find original caller
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Format a log record with optional payload
    
    Args:
        record: The log record to format
        
    Returns:
        str: The formatted log string
    """
    format_string = LOG_FORMAT

    payload = record["extra"].get("payload")
    if payload is not None:
        record["extra"]["payload"] = pformat(
            payload,
            indent=4,
            compact=True,
            width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string
