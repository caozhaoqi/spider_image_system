"""Base logging configuration and constants"""
import os
import sys
from pathlib import Path
import time
from run import constants

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Debug flag
DEBUG = True

# Log configuration
LOG_DIR = Path.cwd().joinpath(
    'log_dir', 
    f'sis_{constants.sis_server_version}_{time.strftime("%Y-%m-%d")}.log'
)

LOG_FORMAT = (
    '<level>{level: <8}</level>  '
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan> - '
    '<level>{message}</level> '
)
