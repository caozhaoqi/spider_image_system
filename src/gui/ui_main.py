#!coding:utf-8
import threading

import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QMainWindow, QMessageBox, QLabel
from loguru import logger

from gui import constants
from utils.get_url import spider_artworks_url
from gui.spider_base_ui import base_menu, tab_ui_tab, tab_1_ui_paint, tab_2_ui_paint
from utils.spider_img_save import download_img_txt
from utils.img_switch import find_images, show_image, folder_path, show_next_image
from utils.log_record import log_record
from utils.video_process import process_images_thread

image_files = find_images(folder_path)
current_image_index = 0


class UIMainWindows(QMainWindow):

    # @logger.catch
    def __init__(self):
        QWidget.__init__(self)
        # 窗体标题 icon
        self.images_convert_thread = None
        self.show_page_label = None
        self.setWindowTitle(u"spider pixiv img tools")
        # self.filename = ''
        # self.file_name_txt = ''
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
        tab_2_ui_paint(self)

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
            self.show_page_label.setText(str(current_image_index) + "/" + str(len(image_files)))
            logger.info("next image show, current page: " + str(current_image_index) + ", count page: " + str(
                len(image_files)))
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
            self.show_page_label.setText(str(current_image_index) + "/" + str(len(image_files)))
            logger.info("after image show, current page: " + str(current_image_index) + ", count page: " + str(
                len(image_files)))
        except Exception as e:
            logger.warning("dir not image , or other err! detail: " + str(e))

    # @logger.catch
    def input_keyword_process(self):
        """
        选择数据路径
        :return:
        """
        if constants.spider_image_flag:
            self.error_tips()
        else:
            key_word = self.file_text.text()
            logger.debug("you input key word is :" + str(key_word))
            # 读取用户输入路径
            spider_thread_obj = threading.Thread(
                target=spider_artworks_url,
                args=(self, key_word,))
            spider_thread_obj.start()
            constants.spider_image_flag = True
            logger.info("spider img thread starting ... ")
        # self.error_path()

    # @logger.catch
    def success_tips(self):
        """
        success tips
        :return:
        """
        QMessageBox.information(self, u"完成", u"操作完成")

    # @logger.catch
    def error_tips(self):
        """
        error tips
        :return:
        """
        QMessageBox.critical(self, u"警告", u"请等待当前操作完成!")

    # @logger.catch
    def download_file_thread(self):
        """

        :return:
        """
        # ret = True
        if constants.download_image_flag:
            self.error_tips()
        else:
            spider_thread_obj = threading.Thread(
                target=download_img_txt,
                args=(self,))
            spider_thread_obj.start()
            constants.download_image_flag = True
            logger.info("download img thread starting ... ")
        # self.error_path()

    def set_video_position_click(self, position):
        """设置视频播放位置"""
        self.media_player.setPosition(position * 1000)  # 设置视频位置，单位为毫秒

    def load_video(self, file_path):
        """加载视频文件"""
        content = QMediaContent(QUrl.fromLocalFile(file_path))  # 创建媒体内容对象，传入视频文件路径
        self.media_player.setMedia(content)  # 设置媒体内容到QMediaPlayer中
        self.media_player.play()  # 开始播放视频
        logger.info("start load video, file path: " + file_path)

    def image_video_click(self):
        """
        image 生成视频
        :return:
        """
        if constants.process_image_flag:
            self.error_tips()
        else:
            self.images_convert_thread = threading.Thread(
                target=process_images_thread,
                args=(self,))
            self.images_convert_thread.start()
            logger.success("image start process. ")
            constants.process_image_flag = True
        pass


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
