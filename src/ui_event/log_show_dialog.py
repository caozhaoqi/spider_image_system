"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QDialog
from PyQt5.QtCore import QTimer, QFile, QTextStream, Qt
from loguru import logger

from run import constants
from utils.log_monitor import find_latest_log_file

LOG_FILE_PATTERN = 'sis_v*.log'
LOG_DIR = Path(constants.basic_path) / "log_dir"


class LogDisplayDialog(QDialog):
    """Real-time log viewer dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Starting LogDisplayDialog initialization")
        try:
            # 基本设置
            self.setWindowTitle('Log Viewer')
            self.resize(800, 600)
            self.setModal(True)
            
            # 初始化UI组件
            self.log_file_name_label = QLabel(self)
            self.log_text_edit = QTextEdit(self)
            self.log_text_edit.setReadOnly(True)
            
            # 设置布局
            layout = QVBoxLayout(self)
            layout.addWidget(self.log_file_name_label)
            layout.addWidget(self.log_text_edit)
            
            # 添加一些测试文本
            self.log_text_edit.append("Initializing log viewer...")
            
            # 设置定时器
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_log)
            self.timer.start(2500)

            constants.UIConfig.log_check_visible = True

            logger.debug("LogDisplayDialog initialization complete")
        except Exception as e:
            logger.exception(f"Failed to initialize LogDisplayDialog: {e}")
            raise

    def closeEvent(self, event):
        logger.debug("Log dialog closing")
        if self.timer:
            self.timer.stop()
        super().closeEvent(event)
        constants.UIConfig.log_check_visible = False

    @logger.catch
    def update_log(self):
        """Update log content"""
        if not constants.UIConfig.log_check_visible:
            return

        log_file_path = find_latest_log_file(LOG_FILE_PATTERN, str(LOG_DIR))
        self.log_file_name_label.setText(str(log_file_path))

        log_file = QFile(str(log_file_path))
        if not log_file.exists():
            self.log_text_edit.append("Log file does not exist")
            return

        if log_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(log_file)
            stream.setCodec('UTF-8')
            content = stream.readAll()
            self.log_text_edit.append(content)
            log_file.close()

    @logger.catch
    def scroll_to_bottom(self):
        """Scroll text edit to bottom"""
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text_edit.setTextCursor(cursor)

    @logger.catch
    def stop_timer(self):
        """Stop the update timer"""
        self.timer.stop()
        logger.debug("Log viewer timer stopped")
        constants.UIConfig.log_check_visible = False


@logger.catch
def show_log_output_method():
    """Show the log viewer dialog"""
    try:
        if not constants.UIConfig.log_check_visible:
            logger.debug("Creating new LogDisplayDialog instance")
            dialog = LogDisplayDialog()
            dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
            constants.log_check_visible = True
            
            # 保持对话框的引用
            global current_dialog
            current_dialog = dialog
            
            logger.debug("Showing log viewer dialog")
            dialog.showMaximized()
            result = dialog.exec_()
            logger.debug(f"Dialog closed with result: {result}")
        else:
            logger.warning("Log viewer already shown")
    except Exception as e:
        logger.exception(f"Error in show_log_output_method: {e}")
