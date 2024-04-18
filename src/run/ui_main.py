import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from loguru import logger
from ui_event.base_event import exit_save_data
from log.log_record import log_record, check_version
from ui_event.pyqt_main_ui import UIMainWindows


@logger.catch
def ui_paint():
    """
    ui paint from pyqt5
    :return:
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    app.lastWindowClosed.connect(on_last_window_closed)

    w = UIMainWindows()
    w.show()
    app.exec_()


@logger.catch
def on_last_window_closed():
    """

    :return:
    """
    logger.warning("Console window is closing...")
    exit_save_data()


@logger.catch
def run_main_py():
    if log_record() and check_version():
        ui_paint()


if __name__ == '__main__':
    run_main_py()
