import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QListWidgetItem, QHBoxLayout
from loguru import logger

from gui import constants
from gui.about_dialog_ui import InformationDialog
from gui.dialog_ui import Dialog
from utils.time_utils import time_to_utc


@logger.catch
def edit_config_msg():
    """
    update ini config msg
    :return:
    """
    dialog = Dialog()
    logger.info("config msg dialog show visible.")
    dialog.exec_()
    # pass


@logger.catch
def visit_web():
    """
    visit
    :return:
    """
    QDesktopServices.openUrl(QUrl("https://caozhaoqi.github.io/"))
    logger.info("jump target help web url.")
    pass


@logger.catch
def about_message_lookup():
    """

    :return:
    """
    information_dialog = InformationDialog()
    information_dialog.exec_()
    logger.info("show sis tools basic info.")
    pass


@logger.catch
def scan_populate_mp4_list(self):
    i = 0
    video_files = ['文件名', '文件大小', '修改时间', '文件路径', '文件格式', '作者']
    if i == 0:
        # 添加信息表头
        self.listWidget_1.addItem(QListWidgetItem(video_files[0]))
        self.listWidget_2.addItem(QListWidgetItem(video_files[1]))
        self.listWidget_3.addItem(QListWidgetItem(video_files[2]))
        self.listWidget_4.addItem(QListWidgetItem(video_files[3]))
        self.listWidget_5.addItem(QListWidgetItem(video_files[4]))
        self.listWidget_6.addItem(QListWidgetItem(video_files[5]))
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(constants.data_path):
        for file in files:
            if file.endswith('.mp4') or file.endswith('.avi'):  # 仅处理jpg和png图片文件
                file_info = os.stat(os.path.join(root, file))
                file_size = str(int(file_info.st_size / 1024 / 1024)) + ' MB'  # bytes
                file_mtime = time_to_utc(file_info.st_mtime)  # modification time in seconds since the epoch
                file_path = os.path.join(root, file)
                file_format = 'MP4 格式视频'  # You can modify this to get the video format if needed
                author = 'unknown 作者'  # You can modify this to get the author if needed

                # 创建文件信息项
                file_info_item = QListWidgetItem(str(file))
                file_size_item = QListWidgetItem(str(file_size))
                file_mtime_item = QListWidgetItem(str(file_mtime))
                file_path_item = QListWidgetItem(str(file_path))
                file_format_item = QListWidgetItem(str(file_format))
                author_item = QListWidgetItem(str(author))

                # 将文件信息项添加到QListWidget中
                # listWidget = self.listWidget
                self.listWidget_1.addItem(file_info_item)
                self.listWidget_2.addItem(file_size_item)
                self.listWidget_3.addItem(file_mtime_item)
                self.listWidget_4.addItem(file_path_item)
                self.listWidget_5.addItem(file_format_item)
                self.listWidget_6.addItem(author_item)
                i += 1
    logger.info("scan video result, length: " + str(i))


@logger.catch
def stop_spider_image():
    constants.stop_spider_url_flag = True
    logger.warning("flag stop_spider_url_flag set true!")
    pass
