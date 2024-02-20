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


# def show_message_box():
#     win32api.MessageBox(0, "这是你的消息", "消息框标题", win32con.MB_OK)

import ctypes


def show_message_box():
    # 加载user32.dll库
    user32 = ctypes.windll.user32
    # ctypes.windll.

    # 定义消息框的参数
    MB_OK = 0x00000000  # 只包含一个确定按钮
    title = "消息框标题"
    message = "这是一条系统消息提示"

    # 显示消息框
    user32.MessageBoxW(0, message, title, MB_OK)


from plyer import notification


def send_cross_platform_notification(title, message):
    """
    system send_cross_platform_notification
    :param title: info title
    :param message: info content
    :return:
    """
    platform = "windows" if os.name == "nt" else "macosx" if sys.platform == "darwin" else "linux"

    if platform == "windows":
        notification.notify(
            title=title,
            message=message,
            app_icon=None,
            timeout=10
        )
    elif platform == "macosx":
        notification.notify(
            title=title,
            message=message,
            app_icon=None
        )
    elif platform == "linux":
        # 在Linux上，plyer使用DBus发送通知，你可能需要安装一些依赖
        notification.notify(
            title=title,
            message=message,
            app_icon=None,
            timeout=10
        )


if __name__ == '__main__':
    cProfile.run('send_cross_platform_notification()')
