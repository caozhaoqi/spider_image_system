import sys
from PyQt5.QtWidgets import  QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import QDateTime


class InformationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('软件信息(software message)')
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        version_label = QLabel('软件版本(software version):')
        layout.addWidget(version_label)

        version = '1.0.2'  # 替换为实际的软件版本
        version_label_2 = QLabel(version)
        layout.addWidget(version_label_2)

        author_label = QLabel('作者(author):')
        layout.addWidget(author_label)

        author = 'czq'  # 替换为实际的作者姓名
        author_label_2 = QLabel(author)
        layout.addWidget(author_label_2)

        time_label = QLabel('时间(time zone: UTC(+8) shanghai):')
        layout.addWidget(time_label)

        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        time_label_2 = QLabel(current_time)
        layout.addWidget(time_label_2)

        website_label = QLabel('访问网站(visit website):')
        layout.addWidget(website_label)

        website = 'https://caozhaoqi.github.io'  # 替换为实际的网站地址
        website_label_2 = QLabel(website)
        layout.addWidget(website_label_2)

        modified_label = QLabel('修改时间(modified time):')
        layout.addWidget(modified_label)

        modified_time = '2024/1/25 12:00:00'  # 替换为实际的修改时间，根据实际需要更新
        modified_label_2 = QLabel(modified_time)
        layout.addWidget(modified_label_2)

        close_button = QPushButton('关闭(close)')  # 添加关闭按钮
        close_button.clicked.connect(self.close)  # 连接关闭信号和关闭方法
        layout.addWidget(close_button)  # 将按钮添加到布局中

        self.setLayout(layout)  # 设置对话框的布局为刚才创建的布局对象


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    information_dialog = InformationDialog()
    information_dialog.show()
    # sys.exit(app.exec_())
