import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from run import constants
from run.constants import sis_server_version, publish_date, build_date
from PyQt5.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QPushButton
)


class InformationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    @logger.catch
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle('软件信息(software message)')
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        # Add information sections
        info_sections = [
            ('软件介绍(software desc):', "SIS is designed as a tool to crawl target websites."),
            ('软件版本(software version):', sis_server_version),
            ('作者(author):', 'Copyright © 2023 - 2024 Zhaoqi.Cao | Powered by PyQt5(v5.15.10)'),
            ('版本发布时间(CST(Shanghai, China)):', publish_date),
            ('访问网站(visit website):', 'https://caozhaoqi.github.io'),
            ('版本修改时间(CST(Shanghai, China)):', build_date)
        ]

        for title, content in info_sections:
            title_label = QLabel(title)
            content_label = QLabel(content)
            layout.addWidget(title_label)
            layout.addWidget(content_label)

        # Add close button
        close_button = QPushButton('关闭(close)')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event
        
        Args:
            event: Close event object
        """
        logger.debug('About_message_lookup_visible Dialog is closing!')
        constants.about_message_lookup_visible = False
        super(InformationDialog, self).closeEvent(event)
