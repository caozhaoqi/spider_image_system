import os
import sys

from selenium.common import StaleElementReferenceException

from ui_event.auto_image_explore import show_image_auto
from ui_event.gi_dialog_ui import show_image_auto_viewer
from ui_event.image_dialog import show_image_viewer
from ui_event.sys_info_ui import show_sys_info_ui

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QListWidgetItem, QHBoxLayout
from loguru import logger
from run.constants import fire_wall_delay_time
from ui_event.about_dialog_ui import InformationDialog
from ui_event.dialog_ui import Dialog
from ui_event.get_url import spider_artworks_url

from run import constants
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
    about msg show
    :return:
    """
    information_dialog = InformationDialog()
    information_dialog.exec_()
    logger.info("show sis tools basic info.")
    pass


@logger.catch
def scan_populate_mp4_list(self):
    """
    scan all mp4 file
    :param self:
    :return:
    """
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
    """
    stop spider images action
    :return:
    """
    constants.stop_spider_url_flag = True
    logger.warning("flag stop_spider_url_flag set true!")
    pass


@logger.catch
def auto_start_spider_image(self):
    """
    auto spider image thread
    @:param self.
    :return:
    """
    spider_thread_obj = threading.Thread(
        target=auto_spider_img_thread,
        args=(self,))
    spider_thread_obj.start()
    logger.info("auto spider img thread stating.")


@logger.catch
def auto_spider_img_thread(self):
    """
    auto spider img thread
    @:param self.
    :return:
    """
    # read txt file spider keyword
    if not constants.stop_spider_url_flag:
        logger.error("already spider img, please stop here before operate!")
        return False
    auto_spider_file_path = os.path.join(constants.data_path, "auto_spider_img")

    if not os.path.exists(auto_spider_file_path):
        os.makedirs(auto_spider_file_path)

    txt_file_list = []
    for root, dirs, files in os.walk(auto_spider_file_path):
        for file in files:
            if file.endswith('spider_img_keyword.txt'):
                txt_file_list.append(os.path.join(root, file))

    file_name = 'spider_img_keyword.txt'
    full_file_path = os.path.join(auto_spider_file_path, file_name)
    if not os.path.exists(full_file_path):
        # 如果文件不存在，创建它
        with open(full_file_path, 'w') as f:
            logger.warning(f"{full_file_path} not exists, will create demo txt!")
            pass  # 创建一个空文件
    try:
        if len(txt_file_list) == 0:
            logger.warning("spider_img_keyword txt length null!")
            return False
        spider_image_keyword = []
        for txt_name in txt_file_list:
            with open(txt_name, 'r', encoding='utf-8') as f:
                spider_image_keyword.append(f.readlines())
    except Exception as e:
        logger.error(f"unknown error, detail {e}")
        return False

    if len(spider_image_keyword) == 0:
        logger.warning("auto spider image null, will exit!")
        return False
    constants.spider_mode = 'auto'
    txt_index = 0
    for spider_img_keyword_detail in spider_image_keyword:
        logger.debug("cur spider kew word txt: " + str(spider_img_keyword_detail))
        # 读取用户输入路径
        constants.stop_spider_url_flag = False
        txt_index += 1
        for spider_image_keyword_item in spider_img_keyword_detail:
            logger.debug("cur spider kew word: " + str(spider_image_keyword_item))
            try:
                spider_artworks_url(self, spider_image_keyword_item.strip())
            except StaleElementReferenceException as sere:
                logger.warning(f"unknown error, detail: {sere}")
            except Exception as e:
                logger.error(f"unknown error, detail: {e}")
            if constants.stop_spider_url_flag:
                logger.warning(f"auto spider img stop! will exit, end spider keyword: {spider_image_keyword_item}!")
                break
            if constants.firewall_flag:
                logger.warning(f"block {constants.visit_url} domain, will retry! cur retry time:"
                               f" {int(fire_wall_delay_time / 60)} minutes.")
                # 设置重试时间
                time.sleep(fire_wall_delay_time)
                continue
        if constants.stop_spider_url_flag:
            # stop auto mode spider
            logger.warning(f"auto spider img stop! will exit, end spider txt name: {txt_file_list[txt_index - 1]}!")
            break


@logger.catch
def stop_download_image():
    """
    stop download image
    :return:
    """
    constants.stop_download_image_flag = True
    # logger.warning("flag stop_download_mage_flag set true!")


@logger.catch
def online_look_image():
    """
    online image look event
    :return:
    """
    show_image_viewer()
    logger.info("online image viewer show!")
    pass


@logger.catch
def auto_play_image():
    """
    auto image play event
    :return:
    """
    show_image_auto()
    logger.info("auto_play_image show!")
    pass


@logger.catch
def performance_monitor():
    """
    performance monitor event
    :return:
    """
    show_sys_info_ui()
    logger.info("sys info show!")
    pass


@logger.catch
def genshin_impact_view():
    """
    genshin impact tools view
    :return:
    """
    show_image_auto_viewer()
    logger.info("show genshin impact show!")
    pass


@logger.catch
def star_rail_view():
    """
    star rail view tools
    :return:
    """
    ...
