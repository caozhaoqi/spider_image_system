import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import QTimer
from loguru import logger
from image.img_switch import show_filter_image, find_images, folder_path
from run import constants
from PyQt5.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QPushButton, 
    QHBoxLayout, QScrollArea
)
from PyQt5.QtGui import QPixmap


class AutoImageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.current_image_index = 0
        self.timer = None
        self.interval = int(1000 / constants.output_video_fps)
        self.image_files = show_filter_image(find_images(folder_path))
        
        self.init_ui()
        
        if not self.image_files:
            logger.warning("Current data directory has no images!")

    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("SIS Image Auto Viewer")
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Image display area
        self.label = QLabel()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.label.resize(self.scroll_area.width(), self.scroll_area.height())
        layout.addWidget(self.scroll_area)

        # Control buttons
        h_box_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        h_box_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop") 
        self.stop_button.clicked.connect(self.stop_timer)
        h_box_layout.addWidget(self.stop_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        h_box_layout.addWidget(self.close_button)

        # Image counter display
        self.counter_label = QLabel()
        self.update_counter()
        h_box_layout.addWidget(self.counter_label)

        layout.addLayout(h_box_layout)

    def update_counter(self):
        """Update the image counter display"""
        self.counter_label.setText(f"{self.current_image_index}/{len(self.image_files)}")

    @logger.catch
    def start_timer(self, _=None):
        """Start automatic image playback"""
        if not constants.start_auto_play_flag and self.image_files:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.show_next_image)
            self.timer.start(self.interval)
            logger.info("Started image playback")
            constants.start_auto_play_flag = True
        else:
            logger.warning("Cannot start playback - no images or already playing")

    @logger.catch
    def stop_timer(self, _=None):
        """Stop automatic image playback"""
        if self.timer:
            self.timer.stop()
        constants.auto_play_image_visible = False
        constants.start_auto_play_flag = False
        logger.info("Stopped image playback")

    @logger.catch
    def show_next_image(self, _=None):
        """Display the next image in sequence"""
        if constants.start_auto_play_flag and self.image_files:
            try:
                self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
                self.show_image_view(self.current_image_index)
            except Exception as e:
                logger.error(f"Error displaying next image: {e}")

    @logger.catch
    def show_image_view(self, index, _=None):
        """Display the image at the given index"""
        image_path = self.image_files[index]
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())
        self.update_counter()

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('AutoImageDialog is closing')
        constants.auto_play_image_visible = False
        constants.start_auto_play_flag = False
        self.stop_timer()
        logger.info("Autoplay dialog closed, timer stopped")
        super().closeEvent(event)
