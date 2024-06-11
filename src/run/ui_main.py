import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from loguru import logger
from log.log_record import log_record, check_version
from ui_event.pyqt_main_ui import UIMainWindows
from utils.system_monitor import sys_mon
import threading


@logger.catch
def ui_paint():
    """
    ui paint from pyqt5
    :return:
    """
    app = QApplication(sys.argv)

    # 单次点击close不退出
    app.setQuitOnLastWindowClosed(False)

    w = UIMainWindows()
    w.show()
    app.exec_()


@logger.catch
def start_sys_mon():
    """

    :return:
    """
    sys_mon_thread_obj = threading.Thread(
        target=sys_mon,
        args=())
    sys_mon_thread_obj.start()
    return True


@logger.catch
def run_main_py():
    """

    :return:
    """
    if log_record() and check_version() and start_sys_mon():
        ui_paint()


if __name__ == '__main__':
    run_main_py()
