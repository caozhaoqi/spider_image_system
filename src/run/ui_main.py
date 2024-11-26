"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from threading import Thread

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QApplication
from loguru import logger
from log.log_record import log_record, check_version
from ui_event.pyqt_main_ui import UIMainWindows
from utils.system_monitor import sys_mon


@logger.catch
def ui_paint() -> None:
    """Initialize and run the PyQt5 UI application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit on window close
    
    window = UIMainWindows()
    window.show()
    app.exec_()


@logger.catch
def start_sys_mon() -> bool:
    """Start system monitoring in a background thread
    
    Returns:
        bool: True if monitor thread started successfully
    """
    monitor_thread = Thread(target=sys_mon, daemon=True)
    monitor_thread.start()
    return True


@logger.catch
def run_main_py() -> None:
    """Main entry point - initialize logging, check version and start UI"""
    if all([log_record(), check_version(), start_sys_mon()]):
        ui_paint()


if __name__ == '__main__':
    run_main_py()
