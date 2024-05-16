import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from run import constants
from run.constants import sis_server_version, publish_date, build_date
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QPlainTextEdit, QTextEdit


class InformationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    @logger.catch
    def init_ui(self):
        self.setWindowTitle('软件信息(software message)')
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        desc_label = QLabel('软件介绍(software desc):')
        layout.addWidget(desc_label)

        desc = "SIS is designed as a tool to crawl target websites."
        desc_label_2 = QLabel(desc)
        layout.addWidget(desc_label_2)

        version_label = QLabel('软件版本(software version):')
        layout.addWidget(version_label)

        version = sis_server_version  # 替换为实际的软件版本
        version_label_2 = QLabel(version)
        layout.addWidget(version_label_2)

        author_label = QLabel('作者(author):')
        layout.addWidget(author_label)

        author = 'Copyright © 2023 - 2024 Zhaoqi.Cao | Powered by PyQt5(v5.15.10)'
        author_label_2 = QLabel(author)
        layout.addWidget(author_label_2)

        time_label = QLabel('版本发布时间(CST(Shanghai, China)):')
        layout.addWidget(time_label)

        time_label_2 = QLabel(publish_date)
        layout.addWidget(time_label_2)

        website_label = QLabel('访问网站(visit website):')
        layout.addWidget(website_label)

        website = 'https://caozhaoqi.github.io'
        website_label_2 = QLabel(website)
        layout.addWidget(website_label_2)

        modified_label = QLabel('版本修改时间(CST(Shanghai, China)):')
        layout.addWidget(modified_label)

        modified_time = build_date
        modified_label_2 = QLabel(modified_time)
        layout.addWidget(modified_label_2)

        close_button = QPushButton('关闭(close)')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    @logger.catch
    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        logger.debug('about_message_lookup_visible Dialog is closing!')
        constants.about_message_lookup_visible = False
        super(InformationDialog, self).closeEvent(event)
