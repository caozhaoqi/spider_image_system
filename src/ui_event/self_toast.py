import os
import sys
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QApplication, QDialog
from loguru import logger

from run import constants


class Toast(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)

        self.timer = None
        self.initUI(message)

    @logger.catch
    def initUI(self, message, _=None):
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()

        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.setLayout(layout)

        self.resize(260, 200)

        # self.move(QApplication.desktop().width() - self.width(),
        #           QApplication.desktop().height() - self.height())

        # self.setC
        # self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(constants.detail_delta_time)  # Toast 显示 3 秒


@logger.catch
def toast_tips_self(content):
    """

    :param content:
    :return:
    """

    toast = Toast(content)
    toast.show()
    toast.exec_()


@logger.catch
def show_toast_thread(content):
    """

    :param content:
    :return:
    """
    toast_thread_obj = threading.Thread(
        target=toast_tips_self,
        args=(content,))
    toast_thread_obj.start()
