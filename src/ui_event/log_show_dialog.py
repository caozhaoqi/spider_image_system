#!coding: utf - 8
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QDialog
from PyQt5.QtCore import QTimer, QFile, QTextStream, Qt
from run import constants
from utils.log_monitor import find_latest_log_file
from loguru import logger

LOG_FILE_PATTERN = 'sis_v*.log'
LOG_DIR = os.path.join(constants.basic_path, "log_dir")  # 日志文件所在的目录


class LogDisplayDialog(QDialog):
    """
    实时日志查看器窗口类
    """

    def __init__(self):
        """
        初始化窗口
        """
        super().__init__()

        self.log_file_name_label = None
        self.timer = None
        self.logTextEdit = None
        self.init_ui()
        self.setup_timer()

    @logger.catch
    def init_ui(self, _=None):
        """
        初始化UI界面
        """
        self.setWindowTitle('log check')
        self.resize(800, 600)

        layout = QVBoxLayout()

        # 使用QTextEdit代替QLabel，因为它支持滚动条
        self.logTextEdit = QTextEdit(self)
        self.logTextEdit.setReadOnly(True)  # 设置为只读，防止用户编辑
        self.logTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 始终显示垂直滚动条
        self.log_file_name_label = QLabel(self)

        layout.addWidget(self.log_file_name_label)

        layout.addWidget(self.logTextEdit)

        self.setLayout(layout)

    @logger.catch
    def setup_timer(self, _=None):
        """
        设置定时器以定期更新日志
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(2500)  # 每秒更新一次

    @logger.catch
    def update_log(self, _=None):
        """
        更新日志内容
        """
        if constants.log_check_visible:
            log_file_path = find_latest_log_file(LOG_FILE_PATTERN, LOG_DIR)
            self.log_file_name_label.setText(log_file_path)
            file = QFile(log_file_path)
            if file.exists():
                if file.open(QFile.ReadOnly | QFile.Text):
                    stream = QTextStream(file)
                    # 设置QTextStream使用UTF-8编码
                    stream.setCodec('UTF-8')
                    content = stream.readAll()

                    # 更新日志内容并滚动到底部
                    self.logTextEdit.append(content)
                    # self.scrollToBottom()

                file.close()
            else:
                self.logTextEdit.append("日志文件不存在")

    @logger.catch
    def scroll_to_bottom(self, _=None):
        """
        滚动到底部的方法
        """
        cursor = self.logTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.logTextEdit.setTextCursor(cursor)

    @logger.catch
    def stop_timer(self, _=None):
        """
        stop play picture
        :return:
        """
        # if constants.start_auto_play_flag:
        # constants.start_auto_play_flag = False
        self.timer.stop()
        logger.debug("log check timer stop.")
        constants.log_check_visible = False

    @logger.catch
    def closeEvent(self, event, _=None):
        """
        对话框关闭
        :param event:
        :return:
        """
        logger.debug('log_check Dialog is closing!')
        constants.log_check_visible = False
        self.stop_timer()
        super(LogDisplayDialog, self).closeEvent(event)


@logger.catch
def show_log_output_method():
    """

    :return:
    """
    if not constants.log_check_visible:
        dialog = LogDisplayDialog()
        dialog.showMaximized()
        dialog.show()
        dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("log_check show!")
        constants.log_check_visible = True
        dialog.exec_()
    else:
        logger.warning("log_check already show!")
