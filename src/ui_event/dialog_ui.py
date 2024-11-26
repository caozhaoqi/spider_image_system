"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, 
    QComboBox, QMessageBox, QCheckBox, QHBoxLayout, QWidget
)
from loguru import logger
from run import constants
from file.ini_file_spider import write_minio_config_to_file
from run.constants import (
    visit_url, s2_url, s1_url, target_url, spider_images_max_count,
    sis_log_level, r18_mode, all_show, proxy_flag, proxy_server_ip,
    proxy_server_port, search_delta_time, detail_delta_time,
    output_video_fps, output_video_width, output_video_height
)
from model.SpiderConfigModel import SpiderConfigModel


class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui_elements()
        self.init_ui()

    def init_ui_elements(self):
        """Initialize UI element attributes"""
        self.output_video_height_label = None
        self.output_video_height_line = None 
        self.output_video_width_line = None
        self.output_video_width_label = None
        self.s1_proxy_server_port_line = None
        self.s1_proxy_server_port_label = None
        self.s1_proxy_server_ip_line = None
        self.s1_proxy_server_ip_label = None
        self.detail_delta_time_label = None
        self.output_video_fps_line = None
        self.sis_log_level_label = None
        self.comboBox_sis_log_level = None
        self.spider_image_max_count_line = None
        self.spider_image_max_count_label = None
        self.s1_url_line = None
        self.s1_url_label = None
        self.visit_url_line = None
        self.visit_url_label = None
        self.r18_mode_label = None
        self.output_video_fps_label = None
        self.search_delta_time_label = None
        self.proxy_flag_label = None
        self.s2_url_label = None
        self.target_url_label = None
        self.all_show_label = None
        self.checkBox_r18 = None
        self.detail_delta_time_line = None
        self.search_delta_time_line = None
        self.checkBox_proxy = None
        self.checkBox_all_show = None
        self.target_url_line = None
        self.s2_url_line = None

    @logger.catch
    def init_ui(self):
        """Initialize the UI layout and components"""
        self.setWindowTitle('编辑工具配置(Edit tools config)')
        self.setFixedSize(800, 800)

        self.create_input_fields()
        self.create_buttons()
        self.setup_layout()

    def create_input_fields(self):
        """Create and initialize all input fields"""
        # URL fields
        self.visit_url_label = QLabel('访问网站 URL(visit_url):')
        self.visit_url_line = QLineEdit(visit_url)

        self.s1_url_label = QLabel('源1图片服务器URL(s1_url):')
        self.s1_url_line = QLineEdit(s1_url)

        self.s2_url_label = QLabel('源2图片服务器URL(s2_url):')
        self.s2_url_line = QLineEdit(s2_url)

        self.target_url_label = QLabel('目标图片服务器URL(target_url):')
        self.target_url_line = QLineEdit(target_url)

        # Spider settings
        self.spider_image_max_count_label = QLabel('抓取图片最大值(spider_img_max):')
        self.spider_image_max_count_line = QLineEdit(str(spider_images_max_count))

        # Log level combo box
        self.sis_log_level_label = QLabel("日志级别(log_level)")
        self.comboBox_sis_log_level = QComboBox()
        self.setup_log_level_combo()

        # Checkboxes
        self.setup_checkboxes()

        # Proxy settings
        self.s1_proxy_server_ip_label = QLabel('代理服务器地址(ip):')
        self.s1_proxy_server_ip_line = QLineEdit(proxy_server_ip)

        self.s1_proxy_server_port_label = QLabel('代理服务器端口(port):')
        self.s1_proxy_server_port_line = QLineEdit(str(proxy_server_port))

        # Time settings
        self.search_delta_time_label = QLabel('搜索延迟时间(s):')
        self.search_delta_time_line = QLineEdit(str(search_delta_time))

        self.detail_delta_time_label = QLabel('详情延迟时间(s):')
        self.detail_delta_time_line = QLineEdit(str(detail_delta_time))

        # Video settings
        self.setup_video_fields()

    def setup_log_level_combo(self):
        """Setup log level combo box"""
        log_levels = ["INFO", "DEBUG", "ERROR", "WARNING"]
        self.comboBox_sis_log_level.addItems(log_levels)
        index = self.comboBox_sis_log_level.findText(sis_log_level)
        if index >= 0:
            self.comboBox_sis_log_level.setCurrentIndex(index)

    def setup_checkboxes(self):
        """Setup checkbox fields"""
        self.r18_mode_label = QLabel('R18(r18_mode):')
        self.checkBox_r18 = QCheckBox(self)
        self.checkBox_r18.setChecked(r18_mode == 'True')

        self.all_show_label = QLabel('全显示(all_show):')
        self.checkBox_all_show = QCheckBox(self)
        self.checkBox_all_show.setChecked(all_show == 'True')

        self.proxy_flag_label = QLabel('代理(proxy_flag):')
        self.checkBox_proxy = QCheckBox(self)
        self.checkBox_proxy.setChecked(proxy_flag == 'True')

    def setup_video_fields(self):
        """Setup video-related fields"""
        self.output_video_fps_label = QLabel('输出视频帧率(fps):')
        self.output_video_fps_line = QLineEdit(str(output_video_fps))

        self.output_video_width_label = QLabel('输出视频宽度(16:9):')
        self.output_video_width_line = QLineEdit(str(output_video_width))

        self.output_video_height_label = QLabel('输出视频高度(16:9):')
        self.output_video_height_line = QLineEdit(str(output_video_height))

    def create_buttons(self):
        """Create save and cancel buttons"""
        self.save_button = QPushButton('保存(save)')
        self.cancel_button = QPushButton('取消(cancel)')
        
        self.save_button.clicked.connect(lambda: save_data(self))
        self.cancel_button.clicked.connect(self.reject)

    def setup_layout(self):
        """Setup the main layout and add all widgets"""
        layout = QVBoxLayout()

        # Add URL fields
        layout.addWidget(self.create_horizontal_widget([
            (self.visit_url_label, self.visit_url_line),
            (self.s1_url_label, self.s1_url_line),
            (self.s2_url_label, self.s2_url_line),
            (self.target_url_label, self.target_url_line)
        ]))

        # Add log and image settings
        layout.addWidget(self.create_horizontal_widget([
            (self.spider_image_max_count_label, self.spider_image_max_count_line),
            (self.sis_log_level_label, self.comboBox_sis_log_level)
        ]))

        # Add video settings
        layout.addWidget(self.create_horizontal_widget([
            (self.output_video_fps_label, self.output_video_fps_line),
            (self.output_video_width_label, self.output_video_width_line),
            (self.output_video_height_label, self.output_video_height_line)
        ]))

        # Add checkboxes
        layout.addWidget(self.create_horizontal_widget([
            (self.r18_mode_label, self.checkBox_r18),
            (self.all_show_label, self.checkBox_all_show),
            (self.proxy_flag_label, self.checkBox_proxy)
        ]))

        # Add proxy settings
        layout.addWidget(self.create_horizontal_widget([
            (self.s1_proxy_server_ip_label, self.s1_proxy_server_ip_line),
            (self.s1_proxy_server_port_label, self.s1_proxy_server_port_line)
        ]))

        # Add time settings
        layout.addWidget(self.create_horizontal_widget([
            (self.search_delta_time_label, self.search_delta_time_line),
            (self.detail_delta_time_label, self.detail_delta_time_line)
        ]))

        # Add buttons
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def create_horizontal_widget(self, widgets):
        """Create a horizontal widget containing the given widget pairs"""
        container = QWidget()
        layout = QHBoxLayout(container)
        for label, widget in widgets:
            layout.addWidget(label)
            layout.addWidget(widget)
        return container

    def reject(self):
        """Handle dialog rejection"""
        logger.debug('Config dialog is cancel closing!')
        constants.UIConfig.edit_config_msg_visible = False
        super().reject()

    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Config dialog is close closing!')
        constants.UIConfig.edit_config_msg_visible = False
        super().closeEvent(event)


@logger.catch
def save_data(self):
    """Save configuration data to ini file"""
    # Collect data from UI elements
    config = SpiderConfigModel()
    config.s1_url = self.s1_url_line.text()
    config.s2_url = self.s2_url_line.text() 
    config.visit_url = self.visit_url_line.text()
    config.target_url = self.target_url_line.text()
    config.spider_images_max_count = self.spider_image_max_count_line.text()
    config.sis_log_level = self.comboBox_sis_log_level.currentText()
    config.output_video_fps = self.output_video_fps_line.text()
    config.output_video_width = self.output_video_width_line.text()
    config.output_video_height = self.output_video_height_line.text()
    config.proxy_server_ip = self.s1_proxy_server_ip_line.text()
    config.proxy_server_port = self.s1_proxy_server_port_line.text()
    config.r18_mode = self.checkBox_r18.isChecked()
    config.all_show = self.checkBox_all_show.isChecked()
    config.proxy_flag = self.checkBox_proxy.isChecked()
    config.search_delta_time = int(self.search_delta_time_line.text()) if self.search_delta_time_line.text() else None
    config.detail_delta_time = int(self.detail_delta_time_line.text()) if self.detail_delta_time_line.text() else None

    # Log configuration changes
    logger.debug("Update config ini file msg:")
    for key, value in vars(config).items():
        logger.debug(f"{key}: {value}")

    # Save configuration
    if write_minio_config_to_file(minio_config=config):
        QMessageBox(QMessageBox.Information, "保存", "配置写入成功,程序即将退出,请重新启动应用以使配置生效!").exec_()
        self.hide()
        constants.UIConfig.edit_config_msg_visible = False
    else:
        QMessageBox(QMessageBox.Warning, "错误", "发生未知错误,写入配置失败,请检查log信息!").exec_()
