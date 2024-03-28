import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton


class MessageDialog(QDialog):
    """
    message dialog
    """
    def __init__(self, message_type, message_text, parent=None):
        """
        dialog init
        :param message_type:
        :param message_text:
        :param parent:
        """
        super(MessageDialog, self).__init__(parent)

        self.setWindowTitle(message_type)
        self.setFixedSize(300, 200)
        self.setWindowIcon(QIcon("../run/favicon.ico"))

        # 设置对话框居中显示
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(screen.center() - size.center())

        layout = QVBoxLayout()

        # 创建粗体字体
        bold_font = QFont(self.font())
        bold_font.setBold(True)

        # 创建标签来显示消息内容
        message_text_label = QLabel(message_text)
        layout.addWidget(message_text_label)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


def show_message(message_type, message_content):
    """
    show tips
    :param message_type: 消息类型： 错误  警告 成功
    :param message_content: 消息内容
    :return:
    """

    dialog_mg = MessageDialog(message_type, message_content)
    dialog_mg.show()
    dialog_mg.exec_()


if __name__ == '__main__':
    # cProfile.run('main()')
    show_message("成功", "已完成！")
