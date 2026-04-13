"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     base_event.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from threading import Thread
import time
from typing import List, Optional

sys.path.append(str(Path(__file__).parent.parent))

from selenium.common import StaleElementReferenceException
from PyQt5.QtCore import QUrl, Qt, QObject
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QListWidgetItem, QDialog
from loguru import logger

from utils.minio_file import upload_image
from file.file_process import get_image_keyword
from ui_event.auto_image_explore import AutoImageDialog
from ui_event.image_dialog import ImageDialog
from ui_event.log_analyze_dialog import LogAnalyzeHistogram
from ui_event.sys_info_ui import SystemMonitor
from utils.face_detect import face_detect_result
from utils.file_utils import convert_and_move_folder
from utils.os_environment_check import detect_installed
from utils.txt_decode import scan_txt_file_all
from ui_event.about_dialog_ui import InformationDialog
from ui_event.dialog_ui import Dialog
from ui_event.get_url import spider_artworks_url
from run import constants
from utils.time_utils import time_to_utc, random_fw_time
from image.spider_img_save import download_re_error_image
from utils.file_unzip_7zip import unzip_file
from ui_event.img_analyze_dialog import ImgAnalyzeHistogram
from ui_event.keyword_dialog import KeywordDialog
from utils.log_monitor import log_mon_war
from utils.sis_therading import SISThreading
from utils.sys_info import get_cur_os
from utils.system_monitor import kill_process_linux, kill_process_win, reduce_sys_res_usage
from utils.img_detect_ai import all_img_detect
from ui_event.JM_dialog import JMDialog
from utils.jm_domain_detect import jm_domain_test, jm_auto_spider_img_thread
from utils.go_file_utils import upload_all_gofile
from ui_event.log_show_dialog import LogDisplayDialog

# 在全局范围内存储对话框引用
_dialog_references = []

def show_dialog(dialog_class: type, visible_flag: str, title: str = None, maximize: bool = False) -> None:
    """Generic function to show dialogs
    
    Args:
        dialog_class: Dialog class to instantiate
        visible_flag: Visibility flag path in constants
        title: Window title (optional)
        maximize: Whether to show maximized (default False)
    """
    if visible_flag.startswith('.'):
        visible_flag = visible_flag[1:]

    parts = visible_flag.split('.')
    obj = constants
    for part in parts:
        obj = getattr(obj, part)

    if not obj:
        # Create dialog and store reference
        dialog = dialog_class()
        _dialog_references.append(dialog)
        
        if title:
            dialog.setWindowTitle(title)
            
        # Connect close event to remove reference
        dialog.finished.connect(lambda: _dialog_references.remove(dialog))
        
        if maximize:
            dialog.showMaximized()
        else:
            dialog.show()


@logger.catch
def edit_config_msg(_=None) -> None:
    """Update ini config message"""
    show_dialog(Dialog, ".UIConfig.edit_config_msg_visible", "Config msg dialog")


@logger.catch
def visit_web(_=None) -> None:
    """Visit help website"""
    QDesktopServices.openUrl(QUrl("https://caozhaoqi.github.io/"))
    logger.info("Jump target help web url.")


@logger.catch
def about_message_lookup(_=None) -> None:
    """Show about message dialog"""
    show_dialog(InformationDialog, ".UIConfig.about_message_lookup_visible", "Show sis tools basic info")


@logger.catch
def scan_populate_mp4_list(self) -> None:
    """Scan and populate video file list"""
    headers = ['文件名', '文件大小', '修改时间', '文件路径', '文件格式', '作者']
    list_widgets = [self.listWidget_1, self.listWidget_2, self.listWidget_3,
                    self.listWidget_4, self.listWidget_5, self.listWidget_6]

    # Add headers
    for widget, header in zip(list_widgets, headers):
        widget.addItem(QListWidgetItem(header))

    # Scan files
    for root, _, files in os.walk(constants.data_path):
        for file in files:
            if file.endswith(('.mp4', '.avi')):
                file_path = Path(root) / file
                file_info = file_path.stat()

                file_data = [
                    str(file),
                    f"{int(file_info.st_size / (1024 * 1024))} MB",
                    time_to_utc(file_info.st_mtime),
                    str(file_path),
                    'MP4 格式视频',
                    'unknown 作者'
                ]

                for widget, data in zip(list_widgets, file_data):
                    widget.addItem(QListWidgetItem(str(data)))


@logger.catch
def stop_spider_image(_=None) -> bool:
    """Stop spider images action"""
    if not constants.SpiderConfig.stop_spider_url_flag:
        constants.SpiderConfig.stop_spider_url_flag = True
        logger.warning("Flag stop_spider_url_flag set true!")
        return True
    logger.warning("Spider url already stop!")
    return False


@logger.catch
def auto_start_spider_image(self) -> bool:
    """Start auto spider image thread"""
    if not constants.SpiderConfig.stop_spider_url_flag:
        logger.error("Already spider img, please stop here before operate!")
        return False

    spider_thread = SISThreading(target=auto_spider_img_thread, args=(self,))
    constants.SpiderConfig.stop_spider_url_flag = False
    spider_thread.start()

    monitor_thread = Thread(target=log_mon_war, args=(spider_thread,))
    monitor_thread.start()
    return True


@logger.catch
def add_keyword_alert(_=None) -> None:
    """Show keyword dialog"""
    dialog = KeywordDialog()
    logger.info("Keyword msg dialog show visible.")
    dialog.exec_()


@logger.catch
def auto_spider_img_thread(self) -> bool:
    """Auto spider image thread"""
    logger.info("Auto spider img thread starting...")

    if constants.ProcessingConfig.log_no_output_flag and not constants.SpiderConfig.stop_spider_url_flag:
        constants.SpiderConfig.stop_spider_url_flag = False

    spider_keywords, txt_files = get_image_keyword()

    # 检查关键词列表是否为空
    has_keywords = False
    for keywords in spider_keywords:
        if keywords:
            has_keywords = True
            break

    if not has_keywords:
        logger.warning("Auto spider image null, please add keyword!")
        if self:
            self.sys_tips("Notice: spider_img_keyword.txt文件为空, 请先点击图像->关键字中添加关键字!")
        return False

    constants.SpiderConfig.spider_mode = 'auto'

    for txt_index, keywords in enumerate(spider_keywords):
        logger.debug(f"Current spider keyword txt: {keywords}")
        constants.SpiderConfig.stop_spider_url_flag = False

        for keyword in keywords:
            keyword = keyword.strip()
            logger.debug(f"Current spider keyword: {keyword}")

            try:
                spider_artworks_url(self, keyword)
            except StaleElementReferenceException as e:
                logger.warning(f"Stale element error: {e}")
            except Exception as e:
                logger.error(f"Unknown error: {e}")

            if constants.SpiderConfig.stop_spider_url_flag:
                logger.warning(f"Auto spider img stop! Final keyword: {keyword}")
                break

            if constants.ProcessingConfig.firewall_flag:
                delay = random_fw_time(constants.fire_wall_delay_time)
                logger.warning(f"Block {constants.visit_url} domain. Retry in {delay} seconds")
                time.sleep(delay)
                continue

        if constants.SpiderConfig.stop_spider_url_flag:
            logger.warning(f"Auto spider img stop! End txt file: {txt_files[txt_index]}")
            break

    return True


@logger.catch
def stop_download_image(_=None) -> bool:
    """Stop downloading images"""
    if not constants.SpiderConfig.stop_download_image_flag or not constants.SpiderConfig.download_image_re_flag:
        constants.SpiderConfig.stop_download_image_flag = True
        constants.SpiderConfig.download_image_re_flag = False
        logger.warning("Flag SpiderConfig.stop_spider_url_flag set true!")
        return True
    logger.warning("Download image already stop or not download image!")
    return False


@logger.catch
def online_look_image(_=None) -> None:
    """Show online image viewer"""
    show_dialog(ImageDialog, ".UIConfig.online_look_image_visible", "Online image viewer", maximize=True)


@logger.catch
def auto_play_image(_=None) -> None:
    """Show auto image player"""
    show_dialog(AutoImageDialog, ".UIConfig.auto_play_image_visible", "Auto_play_image", maximize=True)


@logger.catch
def performance_monitor(_=None) -> None:
    """Show system performance monitor"""
    show_dialog(SystemMonitor, ".UIConfig.performance_monitor_visible", "System info", maximize=True)


@logger.catch
def log_analyze_ui(_=None) -> None:
    """Show log analysis dialog"""
    logger.warning("Function disabled...")
    # show_dialog(LogAnalyzeHistogram, "UIConfig.log_analyze_visible", "Log_analyze_visible", maximize=True)


@logger.catch
def encoding_tools_convert(_=None) -> None:
    """Convert text file encodings"""
    scan_txt_file_all(constants.data_path)
    logger.success("Convert point txt finish!")


@logger.catch
def detect_installed_flag(_=None) -> None:
    """Detect chrome webdriver installation"""
    Thread(target=detect_installed).start()
    logger.debug("Detecting chrome webdriver start!")


@logger.catch
def face_detect_action(_=None) -> bool:
    """Start face detection"""
    if not constants.ProcessingConfig.face_detect_flag:
        constants.ProcessingConfig.face_detect_flag = True
        Thread(target=face_detect_result, args=(constants.data_path,)).start()
        logger.info("Start detect face!")
        return True
    logger.error("Detect face ing, please wait.")
    return False


@logger.catch
def convert_folder_name(_=None) -> None:
    """Convert folder names"""
    if not constants.ProcessingConfig.convert_folder_name_flag:
        constants.ProcessingConfig.convert_folder_name_flag = True
        Thread(target=convert_and_move_folder,
               args=(Path(constants.data_path) / 'img_url',)).start()
        logger.info("Start convert folder_name!")
    else:
        logger.error("Converting folder_name please wait.")


@logger.catch
def user_upload_image(_=None) -> bool:
    """Upload images"""
    if not constants.SpiderConfig.uploading_image_flag:
        constants.SpiderConfig.uploading_image_flag = True
        Thread(target=upload_image, args=(constants.basic_path,)).start()
        logger.info("Start upload image!")
        return True
    logger.error("Uploading image, please wait.")
    return False


@logger.catch
def user_download_image(_=None) -> None:
    """Download failed images"""
    if not constants.SpiderConfig.download_image_re_flag:
        constants.SpiderConfig.download_image_re_flag = True
        Thread(target=download_re_error_image).start()
        logger.info("Start re error download image!")
    else:
        logger.error("Downloading error image, please wait.")


@logger.catch
def unzip_file_method(_=None) -> None:
    """Unzip files"""
    if not constants.SpiderConfig.unzip_file_flag:
        constants.SpiderConfig.unzip_file_flag = True
        Thread(target=unzip_file, args=(constants.data_path,)).start()
        logger.info(f"Start unzip file! path: {constants.data_path}")
    else:
        logger.error("Unzip ing file, please wait.")


@logger.catch
def exit_save_data(_=None) -> None:
    """Save data before exit"""
    logger.warning("-" * 61)
    logger.warning(f"-----SIS-{constants.sis_server_version} exe will quit!-----------------")
    logger.warning("-" * 61)


@logger.catch
def kill_other_close(_=None) -> None:
    """Kill other processes"""
    try:
        if get_cur_os() == "win32":
            reduce_sys_res_usage()
            logger.success("Kill other process success!")
            kill_process_win('taskkill /im ui_main.exe /F /T')
        else:
            kill_process_linux('ui_main')
    except Exception as e:
        logger.error(f"Clear other process fail: {e}")


@logger.catch
def img_category_ana(self, maximize: bool = True) -> None:
    """图片分析对话框"""
    dialog = ImgAnalyzeHistogram()
    dialog.setWindowTitle("Img anal dialog")
    if maximize:
        dialog.showMaximized()
    dialog.exec_()


@logger.catch
def on_last_window_closed(_=None) -> None:
    """Handle window close"""
    logger.debug("Console window is closing...")
    exit_save_data()
    logger.debug("Start clean other process...")
    kill_other_close()


@logger.catch
def model_detect_img(_=None) -> None:
    """Start image detection"""
    if not constants.ProcessingConfig.detect_model_flag:
        constants.ProcessingConfig.detect_model_flag = True
        Thread(target=all_img_detect, args=(constants.data_path,)).start()
        logger.info("Start detect img!")
    else:
        logger.error("Detecting img please wait.")


@logger.catch
def start_download_jm(_=None) -> None:
    """Show JM download dialog"""
    show_dialog(JMDialog, ".UIConfig.jm_dialog_visible", "Dialog_jm")


@logger.catch
def jm_domain_test_method(_=None) -> None:
    """Test JM domains"""
    if not constants.ProcessingConfig.jm_domain_detect_flag:
        constants.ProcessingConfig.jm_domain_detect_flag = True
        Thread(target=jm_domain_test).start()
        logger.info("Start detect jm domain!")
    else:
        logger.error("Detecting jm domain, please wait.")


@logger.catch
def jm_automatic_method(_=None) -> None:
    """Start automatic JM spider"""
    if not constants.ProcessingConfig.jm_sd_auto_flag:
        constants.ProcessingConfig.jm_sd_auto_flag = True
        Thread(target=jm_auto_spider_img_thread).start()
        logger.info("Start automatic spider and download jm image!")
    else:
        logger.error("Spider or downloading jm domain, please wait.")


@logger.catch
def stop_jm_spider(_=None) -> None:
    """Stop JM spider"""
    if constants.ProcessingConfig.jm_sd_auto_flag:
        constants.ProcessingConfig.jm_sd_auto_flag = False
        logger.debug("Start JM auto spider stop.")
    else:
        logger.warning("JM auto already stop.")


@logger.catch
def jm_category_image_method(_=None) -> None:
    """Process JM image categories"""
    logger.warning("The function disabled.")


@logger.catch
def go_file_upload_all(_=None) -> None:
    """Upload files to GoFile"""
    if not constants.ProcessingConfig.go_file_upload_flag:
        constants.ProcessingConfig.go_file_upload_flag = True
        Thread(target=upload_all_gofile, args=(constants.data_path,)).start()
        logger.info("Start gofile upload image!")
    else:
        logger.error("Gofile uploading file, please wait.")


class BaseEvent(QObject):
    def __init__(self):
        super().__init__()
        self._log_dialog = None  # 添加这个实例变量来保持对话框引用

    @logger.catch
    def log_check_ui(self) -> None:
        """日志查看按钮"""
        logger.debug("Log check button clicked")
        try:
            if not self._log_dialog:
                self._log_dialog = LogDisplayDialog()
                self._log_dialog.setWindowTitle("Log Viewer")
                # 设置对话框关闭时的处理
                self._log_dialog.finished.connect(self._on_log_dialog_closed)
                self._log_dialog.showMaximized()
                self._log_dialog.exec_()
        except Exception as e:
            logger.exception(f"Failed to show log dialog: {e}")

    def _on_log_dialog_closed(self):
        """对话框关闭时的处理"""
        logger.debug("Log dialog closed")
        self._log_dialog = None
