import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDialog
from loguru import logger

from run import constants
from utils import jmcomic


class JMDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.download_button = None
        self.jm_id_label = None
        self.jm_id_input = None
        self.initUI()

    def initUI(self):
        # 创建布局
        vbox = QVBoxLayout()

        # 创建标签显示jm_id
        self.jm_id_label = QLabel('jm_id:')
        vbox.addWidget(self.jm_id_label)

        # 创建输入框用于输入jm_id
        self.jm_id_input = QLineEdit()
        vbox.addWidget(self.jm_id_input)

        # 创建下载按钮
        self.download_button = QPushButton('下载')
        self.download_button.clicked.connect(self.on_download_clicked)
        vbox.addWidget(self.download_button)

        # 设置窗口的布局
        self.setLayout(vbox)

        # 设置窗口标题和位置
        self.setWindowTitle('JM ID 下载器')
        self.setGeometry(300, 300, 450, 150)
        self.show()

    @logger.catch
    def on_download_clicked(self, _=None):
        """

        :param _:
        :return:
        """
        # 读取输入框中的jm_id
        jm_id = self.jm_id_input.text()
        if not jm_id and jm_id != "":
            logger.success(f'Download jm_id: {jm_id} Finish')
            download_jm_thread_obj = threading.Thread(
                target=download_jm_thread,
                args=(jm_id,))
            download_jm_thread_obj.start()
        else:
            logger.warning("You input jm_id is empty.")

    def reject(self):
        """

        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('jm_dialog is cancel closing!')
        constants.jm_dialog_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(JMDialog, self).reject()

    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('jm dialog Dialog is close closing!')
        constants.jm_dialog_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(JMDialog, self).closeEvent(event)


@logger.catch
def download_jm_thread(jm_id):
    """

    :param jm_id:
    :return:
    """
    logger.start(f"start download jm_id: {jm_id}")
    jmcomic.download_album(jm_id)
    constants.jm_dialog_visible = False

#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = JMDialog()
#     sys.exit(app.exec_())
