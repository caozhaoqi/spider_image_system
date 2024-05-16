import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import requests
from loguru import logger
from run import constants
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage


class ImageDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SIS Online Image Viewer")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        self.show_page_label_online = QLabel()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.label.resize(self.scroll_area.width(), self.scroll_area.height())
        layout.addWidget(self.scroll_area)

        h_box_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_image)
        h_box_layout.addWidget(self.prev_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        h_box_layout.addWidget(self.close_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_image)
        h_box_layout.addWidget(self.next_button)
        h_box_layout.addWidget(self.show_page_label_online)

        layout.addLayout(h_box_layout)

        self.show_page_label_online.setText(str(constants.cur_show_img_index) + "/" + str(len(
            constants.online_img_list)))
        if len(constants.online_img_list) <= 0:
            logger.warning("cur data dir no image!")
        else:
            self.show_image_view_threading(constants.online_img_list[0])

    @logger.catch
    def show_previous_image(self, _=None):
        """
        show previous image
        :return:
        """
        if not constants.online_show_image:
            logger.warning("loading image, please wait.")
            return False
        if len(constants.online_img_list) <= 0:
            logger.warning("function show_previous_image, cur data dir no image!")
            return False
        if constants.cur_show_img_index > 0:
            constants.cur_show_img_index -= 1
        else:
            constants.cur_show_img_index = len(constants.online_img_list) - 1
        constants.online_show_image = False
        self.show_image_view_threading(constants.online_img_list[constants.cur_show_img_index])
        logger.debug(f"function show_previous_image, current page: {constants.cur_show_img_index}")
        pass

    @logger.catch
    def show_next_image(self, _=None):
        """
        show next image
        :return:
        """
        if not constants.online_show_image:
            logger.warning("loading image, please wait.")
            return False
        if len(constants.online_img_list) <= 0:
            logger.warning("function show_next_image, cur data dir no image!")
            return False
        if constants.cur_show_img_index < len(constants.online_img_list) - 1:
            constants.cur_show_img_index += 1
        else:
            constants.cur_show_img_index = 0
        constants.online_show_image = False
        self.show_image_view_threading(constants.online_img_list[constants.cur_show_img_index])
        logger.debug(f"function show_next_image, current page: {constants.cur_show_img_index}")
        pass

    @logger.catch
    def show_image_view_threading(self, image_path, _=None):
        """

        :param image_path:
        :param _:
        :return:
        """

        if len(constants.online_img_list) <= 0:
            logger.warning("function show_image_view, cur data dir no image!")
            return False
        spider_thread_obj = threading.Thread(
            target=self.show_image_view,
            args=(image_path,))
        spider_thread_obj.start()
        logger.info("show img thread stating.")

    @logger.catch
    def show_image_view(self, image_path, _=None):
        """
        show point index image
        :param _:
        :param image_path:
        :return:
        """
        try:
            response = requests.get(image_path)
            if response.headers.get('Content-Type', '').startswith('image/'):
                # 创建QPixmap对象并加载图片数据
                pixmap = QPixmap.fromImage(QImage.fromData(response.content))
                self.label.setPixmap(pixmap)
                self.label.resize(pixmap.width(), pixmap.height())
                self.show_page_label_online.setText(str(constants.cur_show_img_index) + "/" + str(len(
                    constants.online_img_list)))
                logger.success(f"loading image: {image_path[-27:].strip()} success!")
                constants.online_show_image = True
            else:
                logger.warning(f"error, Invalid image format! response content: {response}")
        except Exception as e:
            constants.online_show_image = True
            logger.error(f"unknown error, detail: {e}")

    @logger.catch
    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        logger.debug('ImageDialog Dialog is closing!')
        constants.online_look_image_visible = False
        super(ImageDialog, self).closeEvent(event)
