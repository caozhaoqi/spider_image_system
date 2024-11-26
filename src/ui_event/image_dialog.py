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

import threading
import requests
from loguru import logger
from run import constants
from PyQt5.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QPushButton, 
    QHBoxLayout, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage


class ImageDialog(QDialog):
    def __init__(self, maximize: bool = True):
        super().__init__()
        self.setModal(True)
        self.init_ui()
        if maximize:
            self.showMaximized()

    def init_ui(self):
        """Initialize the UI components"""
        # Create main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create image display widgets
        self.label = QLabel()
        self.show_page_label_online = QLabel()
        
        # Setup scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.label.resize(self.scroll_area.width(), self.scroll_area.height())
        layout.addWidget(self.scroll_area)

        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_image)
        button_layout.addWidget(self.prev_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_image)
        button_layout.addWidget(self.next_button)
        
        button_layout.addWidget(self.show_page_label_online)
        layout.addLayout(button_layout)
    
    @logger.catch
    def showEvent(self, event):
        """重写显示事件"""
        super().showEvent(event)
        self.load_initial_image()

    @logger.catch
    def show(self):
        """重写 show 方法，使用 exec_ 代替"""
        return self.exec_()

    def load_initial_image(self):
        """Load the first image on dialog creation"""
        self.update_page_counter()
        if not constants.online_img_list:
            logger.warning("No images available in current directory")
            return
        self.show_image_view_threading(constants.online_img_list[0])

    def update_page_counter(self):
        """Update the page counter display"""
        total = len(constants.online_img_list)
        self.show_page_label_online.setText(f"{constants.cur_show_img_index + 1}/{total}")

    @logger.catch
    def show_previous_image(self, _=None):
        """Display the previous image"""
        if not self.can_change_image():
            return False

        if constants.cur_show_img_index > 0:
            constants.cur_show_img_index -= 1
        else:
            constants.cur_show_img_index = len(constants.online_img_list) - 1

        self.change_image()
        logger.debug(f"Showing previous image, current page: {constants.cur_show_img_index}")

    @logger.catch
    def show_next_image(self, _=None):
        """Display the next image"""
        if not self.can_change_image():
            return False

        if constants.cur_show_img_index < len(constants.online_img_list) - 1:
            constants.cur_show_img_index += 1
        else:
            constants.cur_show_img_index = 0

        self.change_image()
        logger.debug(f"Showing next image, current page: {constants.cur_show_img_index}")

    def can_change_image(self):
        """Check if image can be changed"""
        if not constants.UIConfig.online_look_image_visible:
            logger.warning("Loading image, please wait.")
            return False
        if not constants.UIConfig.online_look_image_visible:
            logger.warning("No images available")
            return False
        return True

    def change_image(self):
        """Change the displayed image"""
        constants.online_show_image = False
        self.show_image_view_threading(
            constants.online_img_list[constants.cur_show_img_index]
        )

    @logger.catch
    def show_image_view_threading(self, image_path, _=None):
        """Start a thread to load and display the image"""
        if not constants.online_img_list:
            logger.warning("No images available to display")
            return False

        thread = threading.Thread(
            target=self.show_image_view,
            args=(image_path,)
        )
        thread.start()
        logger.info("Image loading thread started")

    @logger.catch
    def show_image_view(self, image_path, _=None):
        """Load and display the image"""
        try:
            response = requests.get(image_path)
            if response.headers.get('Content-Type', '').startswith('image/'):
                pixmap = QPixmap.fromImage(QImage.fromData(response.content))
                self.label.setPixmap(pixmap)
                self.label.resize(pixmap.width(), pixmap.height())
                self.update_page_counter()
                logger.success(f"Successfully loaded image: {image_path[-27:].strip()}")
                constants.online_show_image = True
            else:
                logger.warning(f"Invalid image format in response: {response}")
        except Exception as e:
            constants.online_show_image = True
            logger.error(f"Error loading image: {str(e)}")

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Image Dialog closing')
        constants.UIConfig.online_look_image_visible = False
        super().closeEvent(event)
