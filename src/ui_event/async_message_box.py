import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cProfile
import sys

import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from run import constants


class Worker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        # 在这里执行耗时操作
        time.sleep(5)  # 模拟耗时操作
        # if not constants.stop_download_image_flag:
        self.finished.emit("操作完成")  # 发送信号表示工作完成


class MyApp(QApplication):
    def __init__(self, sys_argv):
        super(MyApp, self).__init__(sys_argv)
        self.messageBox = None
        self.thread = None
        self.initUI()

    def initUI(self):
        self.messageBox = QMessageBox()
        self.messageBox.setWindowTitle('提示')
        self.messageBox.setText('开始执行任务...')
        self.messageBox.setModal(True)
        self.thread = Worker()
        self.thread.start()  # 开始线程
        self.thread.finished.connect(self.onFinished)  # 连接信号到槽函数

    def onFinished(self, result):
        self.messageBox.setText('操作完成')  # 更新对话框文本
        self.messageBox.exec_()  # 显示对话框，等待用户关闭


def test():
    """
    profile test.
    :return:
    """
    app = MyApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == '__main__':
    cProfile.run('test()')
