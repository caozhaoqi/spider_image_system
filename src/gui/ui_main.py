import sys

from PyQt5.QtWidgets import QApplication
from loguru import logger

from gui.pyqt_main_ui import UIMainWindows
from utils.log_record import log_record, check_version


@logger.catch
def ui_paint():
    """

    :return:
    """
    app = QApplication(sys.argv)
    w = UIMainWindows()
    w.show()
    app.exec_()


if __name__ == '__main__':
    log_record()
    check_version()
    ui_paint()
