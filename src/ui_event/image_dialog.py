import cProfile
import sys
import threading

import requests
from loguru import logger

from run import constants
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea, QApplication
from PyQt5.QtGui import QPixmap, QImage


class ImageDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SIS Online Image Viewer")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()

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

        layout.addLayout(h_box_layout)

        if len(constants.online_img_list) <= 0:
            logger.warning("cur data dir no image!")
        else:
            #     load index page show image
            self.show_image_view_threading(constants.online_img_list[0])
            logger.debug("index image show!")

    def show_previous_image(self):
        """
        show previous image
        :return:
        """
        if len(constants.online_img_list) <= 0:
            logger.warning("function show_previous_image, cur data dir no image!")
            return False
        if constants.cur_show_img_index > 0:
            constants.cur_show_img_index -= 1
        else:
            constants.cur_show_img_index = len(constants.online_img_list) - 1
        self.show_image_view_threading(constants.online_img_list[constants.cur_show_img_index])
        logger.debug(f"function show_previous_image, current page: {constants.cur_show_img_index}")
        pass

    def show_next_image(self):
        """
        show next image
        :return:
        """
        if len(constants.online_img_list) <= 0:
            logger.warning("function show_next_image, cur data dir no image!")
            return False
        if constants.cur_show_img_index < len(constants.online_img_list) - 1:
            constants.cur_show_img_index += 1
        else:
            constants.cur_show_img_index = 0
        self.show_image_view_threading(constants.online_img_list[constants.cur_show_img_index])
        logger.debug(f"function show_next_image, current page: {constants.cur_show_img_index}")
        pass

    def show_image_view_threading(self, image_path):
        if len(constants.online_img_list) <= 0:
            logger.warning("function show_image_view, cur data dir no image!")
            return False
        spider_thread_obj = threading.Thread(
            target=self.show_image_view,
            args=(image_path,))
        spider_thread_obj.start()
        logger.info("show img thread stating.")

    def show_image_view(self, image_path):
        """
        show point index image
        :param image_path:
        :return:
        """
        response = requests.get(image_path)
        if response.headers.get('Content-Type', '').startswith('image/'):
            # 创建QPixmap对象并加载图片数据
            pixmap = QPixmap.fromImage(QImage.fromData(response.content))
            self.label.setPixmap(pixmap)
            logger.debug("loading image success!")
        else:
            logger.warning(f"error, Invalid image format! response content: {response}")


@logger.catch
def show_image_viewer():
    """
    show image to tool
    :return:
    """
    dialog = ImageDialog()
    dialog.showMaximized()
    dialog.show()
    dialog.exec_()


if __name__ == '__main__':
    cProfile.run('show_image_viewer()')
