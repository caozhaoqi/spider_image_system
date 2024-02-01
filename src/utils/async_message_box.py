import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop
from loguru import logger


@logger.catch
def show_async_message_box(content, title):
    """

    :param content:
    :param title:
    :return:
    """
    class AsyncMessageBoxThread(QThread):
        show_message = pyqtSignal(str)

        def run(self):
            loop = QEventLoop(self)
            self.show_message.connect(loop.quit)
            self.show_message.emit(content)
            loop.exec_()

    app = QApplication([])
    window = AsyncMessageBoxThread()
    window.start()
    window.show_message.connect(lambda: show_message_box(content, title))
    sys.exit(app.exec_())


@logger.catch
def show_message_box(title, text):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.exec_()


if __name__ == '__main__':
    # 调用函数显示异步消息提示框
    show_async_message_box("warning", "操作尚未完成！")

