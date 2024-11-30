"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
import threading
from pathlib import Path
from threading import Thread

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QApplication, QMessageBox
from loguru import logger
from log.log_record import log_record, check_version
from ui_event.pyqt_main_ui import UIMainWindows
from utils.system_monitor import sys_mon


def show_error_dialog(message: str) -> None:
    """Display error message dialog"""
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    QMessageBox.critical(None, "Error", message)


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
    sys_mon_thread_obj = threading.Thread(
        target=sys_mon,
        args=())
    sys_mon_thread_obj.start()
    return True

@logger.catch
def init_system():
    """系统初始化"""
    try:
        # 初始化日志
        if not log_record():
            logger.error("日志系统初始化失败")
            return False
            
        # 检查版本
        if not check_version():
            logger.error("版本检查失败")
            return False
            
        # 启动系统监控
        if not start_sys_mon():
            logger.error("系统监控启动失败") 
            return False
            
        return True
        
    except Exception as e:
        logger.exception(f"系统初始化异常: {str(e)}")
        return False

@logger.catch
def main():
    """主函数"""
    try:
        # 系统初始化
        if not init_system():
            # 显示错误对话框
            show_error_dialog("系统初始化失败,请查看日志")
            return
            
        # 启动UI
        ui_paint()
        
    except Exception as e:
        logger.exception(f"程序启动异常: {str(e)}")
        show_error_dialog(f"程序启动异常: {str(e)}")

if __name__ == '__main__':
    main()
