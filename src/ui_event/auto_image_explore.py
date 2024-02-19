import cProfile

from PyQt5.QtCore import QTimer
from loguru import logger

from image.img_switch import show_filter_image, find_images, folder_path
from run import constants
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QScrollArea, QApplication
from PyQt5.QtGui import QPixmap, QImage


class AutoImageDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.current_image_index = 0
        self.timer = None
        self.interval = 1000 / constants.output_video_fps
        self.image_files = show_filter_image(find_images(folder_path))
        self.setWindowTitle("SIS Image Auto Viewer")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
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

        layout.addLayout(h_box_layout)

        if len(constants.online_img_list) <= 0:
            logger.warning("cur data dir no image!")

    def start_timer(self):
        """
        Start the timer to change images periodically.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_image)
        self.timer.start(self.interval)
        logger.info("all image start play!")

    def stop_timer(self):
        self.timer.stop()
        logger.warning("all image stop play!")

    def show_next_image(self):
        """
        Show the next image in the list.
        """
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.show_image_view(self.current_image_index)

    def show_image_view(self, image_path):
        """
        show point index image
        :param image_path:
        :return:
        """
        image_path = self.image_files[image_path]
        pixmap = QPixmap(image_path)  # 创建新的QPixmap实例
        self.label.setPixmap(pixmap)  # 更新QLabel的显示内容
        # self.label.resize(self.pixmap_image_tab1.width(), self.pixmap_image_tab1.height())


@logger.catch
def show_image_auto():
    """
    show image to tool
    :return:
    """
    dialog = AutoImageDialog()
    dialog.showMaximized()
    dialog.show()
    dialog.exec_()


if __name__ == '__main__':
    cProfile.run('show_image_auto()')
