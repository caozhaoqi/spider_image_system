#!coding:utf-8
import os
import threading

import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QMainWindow, QMessageBox
from loguru import logger

from src.get_url import spider_artworks_url
from src.gui.spider_base_ui import base_menu, tab_ui_tab, tab_1_ui_paint
from src.spider_img_save import download_img_txt
from src.utils.img_switch import find_images, show_image, folder_path, show_next_image
from src.utils.log_record import log_record

image_files = find_images(folder_path)
current_image_index = 0


# @logger.catch
class UIMainWindows(QMainWindow):

    # @logger.catch
    def __init__(self):
        QWidget.__init__(self)
        # 窗体标题 icon
        self.setWindowTitle(u"spider pixiv img tools")
        self.filename = ''
        icon = QIcon()
        icon.addPixmap(
            QPixmap("favicon.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        # 窗体menu
        self.setMenuBar(base_menu(self))
        # 选项卡
        self.tab1, self.tab2, self.tab3, self.tab_widget = tab_ui_tab(self)
        # tab1 页面绘制
        tab_1_ui_paint(self)

        # 获取屏幕大小 窗口大小
        screen = QDesktopWidget().screenGeometry()
        # 设置窗口大小为屏幕大小
        self.setGeometry(0, 0, screen.width(), screen.height() - 400)
        # 显示第一张图片
        show_next_image(self)
        self.showMaximized()  # 最大化窗口

    # @logger.catch
    def next_img(self):
        """

        :return:
        """
        try:
            global current_image_index, image_files
            current_image_index = (current_image_index + 1) % len(image_files)
            show_image(self, image_files[current_image_index])
        except Exception as e:
            logger.warning("dir not image, or other err! detail: " + str(e))

    # @logger.catch
    def before_img(self):
        """

        :return:
        """
        try:
            global current_image_index, image_files
            current_image_index = (current_image_index - 1 + len(image_files)) % len(image_files)
            show_image(self, image_files[current_image_index])
        except Exception as e:
            logger.warning("dir not image , or other err! detail: " + str(e))

    # @logger.catch
    def input_keyword_process(self):
        """
        选择数据路径
        :return:
        """
        key_word = self.file_text.text()
        logger.debug("you input key word is :" + str(key_word))
        # 读取用户输入路径
        spider_thread_obj = threading.Thread(
            target=spider_artworks_url,
            args=(self, key_word,))
        spider_thread_obj.start()
        logger.info("spider img thread starting ... ")
        self.error_path()

    # @logger.catch
    def complete(self):
        """

        :return:
        """
        QMessageBox.critical(self, u"完成", u"下载完成")

    # @logger.catch
    def error_path(self):
        """

        :return:
        """
        QMessageBox.critical(self, u"警告", u"请等待下载完成!")

    # @logger.catch
    def download_file_thread(self):
        """

        :return:
        """
        # ret = True
        spider_thread_obj = threading.Thread(
            target=download_img_txt,
            args=(self,))
        spider_thread_obj.start()
        logger.info("download img thread starting ... ")
        self.error_path()


@logger.catch
def ui_paint():
    """

    :return:
    """
    app = QApplication(sys.argv)
    w = UIMainWindows()
    w.show()
    app.exec_()


if __name__ == '__main__':
    log_record()
    ui_paint()
