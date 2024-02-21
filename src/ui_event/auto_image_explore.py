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
            logger.warning("cur data dir no image!")

    def start_timer(self):
        """
        Start the timer to change images periodically.
        """
        if not constants.start_auto_play_flag:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.show_next_image)
            self.timer.start(self.interval)
            logger.info("all image start play!")
            constants.start_auto_play_flag = True
        else:
            logger.warning("all image already play!")

    def stop_timer(self):
        """
        stop play picture
        :return:
        """
        if constants.start_auto_play_flag:
            constants.start_auto_play_flag = False
            self.timer.stop()
            logger.info("all image stop play!")
        else:
            logger.warning("all image not start!")

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
        self.show_page_label_auto.setText(str(self.current_image_index) + "/" + str(len(self.image_files)))

        self.label.resize(pixmap.width(), pixmap.height())

    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('AutoImageDialog Dialog is closing!')
        constants.auto_play_image_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(AutoImageDialog, self).closeEvent(event)

# @logger.catch
# def show_image_auto():
#     """
#     show image to tool
#     :return:
#     """
#     dialog = AutoImageDialog()
#     dialog.showMaximized()
#     dialog.show()
#     dialog.exec_()


if __name__ == '__main__':
    cProfile.run('show_image_auto()')
