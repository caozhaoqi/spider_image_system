from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from loguru import logger


class AsyncMessageBox(QThread):
    finished = pyqtSignal()

    def __init__(self, message, title):
        super().__init__()
        self.message = message
        self.title = title

    def run(self):
        # app = QApplication([])
        msg_box = QMessageBox(QMessageBox.Information, self.title, self.message)
        msg_box.exec()
        self.finished.emit()
        # app.quit()

    @pyqtSlot()
    def on_finished(self):
        print("对话框已关闭")
        # 在这里可以执行其他操作，例如关闭线程等
        # self.emit(PyQt5.QtCore.PYQT_SIGNAL("finished"), True)


@logger.catch
def show_msg_alert(self, title, content):
    """
    show msg from alert
    :param self:
    :param title:
    :param content:
    :return:
    """
    async_msg_alert = AsyncMessageBox(title, content)
    async_msg_alert.run()
    # app = QApplication(sys.argv)
    # if title == '完成':
    #     QMessageBox.information(None, title, content)
    # else:
    #     QMessageBox.warning(None, title, content)

    # sys.exit(app.exec_())
    # async_msg_box.finished.wait()
    #
    # 连接信号和槽，处理对话框关闭事件
    # async_msg_box.finished.c(lambda: logger.info("对话框已关!"))
