import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import QTimer
from loguru import logger
from image.img_switch import show_filter_image, find_images, folder_path
from run import constants
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap


class AutoImageDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.current_image_index = 0
        self.timer = None
        self.interval = int(1000 / constants.output_video_fps)
        self.image_files = show_filter_image(find_images(folder_path))
        self.setWindowTitle("SIS Image Auto Viewer")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()

        self.scroll_area = QScrollArea()
        self.show_page_label_auto = QLabel()
        self.scroll_area.setWidget(self.label)
        # self.scroll_area.setParent(self.label)
        self.label.resize(self.scroll_area.width(), self.scroll_area.height())
        layout.addWidget(self.scroll_area)

        h_box_layout = QHBoxLayout()
        self.prev_button = QPushButton("start")
        self.prev_button.clicked.connect(self.start_timer)
        h_box_layout.addWidget(self.prev_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        h_box_layout.addWidget(self.close_button)

        self.next_button = QPushButton("Stop")
        self.next_button.clicked.connect(self.stop_timer)
        h_box_layout.addWidget(self.next_button)

        h_box_layout.addWidget(self.show_page_label_auto)

        layout.addLayout(h_box_layout)
        self.show_page_label_auto.setText(str(self.current_image_index) + "/" + str(len(self.image_files)))

        if len(constants.online_img_list) <= 0:
            logger.warning("Cur data dir no image!")

    @logger.catch
    def start_timer(self, _=None):
        """
        Start the timer to change images periodically.
        """
        if not constants.start_auto_play_flag:
            if self.current_image_index >= 0 and self.image_files != []:
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.show_next_image)
                self.timer.start(self.interval)
                logger.info("All image start play!")
                constants.start_auto_play_flag = True
            else:
                logger.warning("All image already play, or no image!")
        # else:
        #     logger.warning("auto_image_dialog not visible or image play stop!")

    @logger.catch
    def stop_timer(self, _=None):
        """
        stop play picture
        :return:
        """
        # if constants.start_auto_play_flag:
        # constants.start_auto_play_flag = False
        self.timer.stop()
        constants.auto_play_image_visible = False
        constants.start_auto_play_flag = False
        logger.warning("All image stop play!")
        # else:
        #     logger.warning("all image not start, or no image!")

    @logger.catch
    def show_next_image(self, _=None):
        """
        Show the next image in the list.
        """
        if constants.start_auto_play_flag:
            try:
                if self.current_image_index >= 0 and self.image_files != []:
                    self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
                    self.show_image_view(self.current_image_index)
                else:
                    logger.warning("No image in cur dir!")
            except Exception as e:
                logger.error(f"Unknown error, auto_image_explore.py, detail: {e}")
        # else:
        #     logger.warning("auto_image_dialog not visible or image play stop!")
        #     return False

    @logger.catch
    def show_image_view(self, image_path, _=None):
        """
        show point index image
        :param _:
        :param image_path:
        :return:
        """
        image_path = self.image_files[image_path]
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.show_page_label_auto.setText(str(self.current_image_index) + "/" + str(len(self.image_files)))

        self.label.resize(pixmap.width(), pixmap.height())

    @logger.catch
    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        logger.debug('AutoImageDialog Dialog is closing!')
        constants.auto_play_image_visible = False
        constants.start_auto_play_flag = False
        self.stop_timer()
        logger.info("Autoplay dialog closed, timer stop!")
        super(AutoImageDialog, self).closeEvent(event)
