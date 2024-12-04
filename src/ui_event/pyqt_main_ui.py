"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

#!coding: utf-8
import os
import platform
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import re
import threading
import cv2
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QFileDialog, QSystemTrayIcon
from PyQt5 import QtWidgets, QtGui, QtCore
from loguru import logger

from file.file_process import scan_directory_zip_txt
from file.gofile_downloader import start_download_file_link
from run import constants
from run.constants import sis_server_version, zoom_out_scale, zoom_in_scale
from http_tools.http_request import url_zip_all_process, unzip_generate_gif
from image.img_switch import show_filter_image, folder_path, find_images, show_image
from image.spider_img_save import download_img_txt, img_category_button, remove_error_image
from image.video_process import play_video_process, process_images_thread
from ui_event.base_event import scan_populate_mp4_list, on_last_window_closed
from ui_event.get_url import spider_artworks_url
from ui_event.spider_base_ui import base_menu, tab_1_ui_paint, tab_2_ui_paint, tab_3_ui_paint, tab_ui_tab
from ui_event.log_show_dialog import show_log_output_method
from utils.time_utils import get_cur_time
from utils.wx_push import wx_push_content

current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


@logger.catch
def open_data_path_method():
    """Opens the data directory in the system file explorer"""
    try:

        # 判断操作系统
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', constants.data_path])
        elif platform.system() == 'Windows':  # Windows
            subprocess.run(['start', constants.data_path], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', constants.data_path])


        logger.success(f"Opened data path: {constants.data_path}")
    except Exception as e:
        logger.error(f"Failed to open data path: {constants.data_path}, error: {e}")


class UIMainWindows(QMainWindow):

    @logger.catch
    def __init__(self):
        """Initialize the main UI window"""
        QMainWindow.__init__(self)

        # Initialize instance variables
        self.trayIcon = None
        self.trayIconMenu = None
        self.quitAppAction = None
        self.openMainWindowAction = None
        self.open_data_path_thread = None
        self.edt_input_file_text_3_str = None
        self.edt_input_file_text_3 = None
        self.start_download_file_link_thread = None
        self.unzip_generate_video_thread = None
        self.download_gif_zip_thread = None
        self.pixmap_image_tab1 = None
        self.images_convert_thread = None
        self.show_page_label = None
        self.spider_mode_show_label = None
        self.index_1_show_flag = False

        # Setup window properties
        self.setWindowTitle(f"Spider Image System ({sis_server_version})")
        icon = QIcon()
        icon.addPixmap(QPixmap("../run/favicon.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        # Setup UI components
        self.setMenuBar(base_menu(self))
        self.tab1, self.tab2, self.tab3, self.tab_widget = tab_ui_tab(self)

        tab_1_ui_paint(self)
        tab_2_ui_paint(self)
        tab_3_ui_paint(self)

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Setup image interaction properties
        self.isDragging = False
        self.dragStartPos = None
        self.lastMousePos = None
        self.scaleFactor = 1.0
        # self.label.installEventFilter(self)

        # Show maximized window
        self.showMaximized()

        # Initialize UI state
        self.spider_mode_show_label.setText(constants.SpiderConfig.spider_mode)

        # Setup system tray
        self.set_tray_icon()

    def on_tab_changed(self, index, _=None):
        """Handle tab change events"""
        if index == 1 and not self.index_1_show_flag:
            scan_populate_mp4_list(self)
            logger.info("Video tab clicked, loading mp4 data")
            self.index_1_show_flag = True

    @logger.catch
    def jump_point_image_click(self, _=None):
        """Jump to specified image page"""
        images_list = find_images(constants.data_path)
        if not images_list:
            logger.warning("Cannot jump - no images found")
            return False

        image_keyword = self.image_page.text()
        if not image_keyword:
            logger.warning("No keyword entered")
            return False

        numbers = re.findall(r'\d+', image_keyword)
        letters = re.findall('[a-zA-Z]+', image_keyword)
        logger.info(f"Search keyword: {numbers}, {letters}")

        if numbers and not letters:
            # Jump to page number
            logger.info(f"Jumping to image page: {image_keyword}")
            self.jump_point_image_page(int(numbers[0]))
        else:
            # Search by name
            logger.info(f"Searching for image with keyword: {image_keyword}")
            for index, image_content in enumerate(images_list):
                if image_keyword in image_content:
                    self.jump_point_image_page(index)
                    break

        logger.info(f"Jump successful - current page {numbers[0]}")

    @logger.catch
    def next_img(self, _=None):
        """Show next image"""
        try:
            global current_image_index, image_files
            current_image_index = (current_image_index + 1) % len(image_files)
            show_image(self, image_files[current_image_index])
            self.show_page_label.setText(f"{current_image_index}/{len(image_files)}")
            logger.info(f"Showing next image - page {current_image_index}/{len(image_files)}")
        except Exception as e:
            logger.warning(f"Error showing next image: {e}")

    @logger.catch
    def before_img(self, _=None):
        """Show previous image"""
        try:
            global current_image_index, image_files
            current_image_index = (current_image_index - 1 + len(image_files)) % len(image_files)
            show_image(self, image_files[current_image_index])
            self.show_page_label.setText(f"{current_image_index}/{len(image_files)}")
            logger.info(f"Showing previous image - page {current_image_index}/{len(image_files)}")
        except Exception as e:
            logger.warning(f"Error showing previous image: {e}")

    @logger.catch
    def jump_point_image_page(self, index, _=None):
        """Jump to specific image index"""
        try:
            global image_files, current_image_index
            current_image_index = index
            show_image(self, image_files[current_image_index])
            self.show_page_label.setText(f"{current_image_index}/{len(image_files)}")
            logger.info(f"Jumped to image - page {current_image_index}/{len(image_files)}")
        except Exception as e:
            logger.warning(f"Error jumping to image: {e}")

    @logger.catch
    def input_keyword_process(self, _=None):
        """Process keyword input for spider"""
        if not constants.SpiderConfig.stop_spider_url_flag:
            self.error_tips("爬取操作")
            return

        constants.SpiderConfig.spider_mode = 'manual'
        key_word = self.file_text.text()

        if not key_word:
            logger.warning("Empty keyword entered")
            return False

        logger.debug(f"Processing keyword: {key_word}")
        spider_thread = threading.Thread(
            target=spider_artworks_url,
            args=(self, key_word,)
        )
        spider_thread.start()
        constants.SpiderConfig.stop_spider_url_flag = False
        logger.info("Spider image thread started")

    @logger.catch
    def input_keyword_process_3(self, _=None):
        """Select folder for tab 3"""
        folder = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if folder:
            logger.debug(f'Selected folder: {folder}')
            self.edt_input_file_text_3_str = folder
            self.edt_input_file_text_3.setText(folder)

    @logger.catch
    def remove_error_image_click(self, _=None):
        """Remove error images"""
        if constants.ProcessingConfig.single_flag:
            self.error_tips("删除错误图片操作")
            return

        constants.ProcessingConfig.single_flag = True
        remove_error_image(self)

    @logger.catch
    def img_category_button_click(self, _=None):
        """Categorize images"""
        if constants.ProcessingConfig.single_flag:
            self.error_tips("图片分类操作")
            return

        constants.single_flag = True
        img_category_button(self)

    @logger.catch
    def success_tips(self, operate_name, _=None):
        """Show success notification"""
        message = f"{get_cur_time()}: {operate_name}, 操作完成! (*^▽^*)"
        self.sys_status_label.setText(message)

        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("成功提示", operate_name, QtGui.QIcon("./favicon.ico"), 10000)
            wx_push_content(message)
        else:
            logger.warning("System tray message not supported")

        logger.success('Success notification shown')

    @logger.catch
    def error_tips(self, operate_name, _=None):
        """Show error notification"""
        message = f"{get_cur_time()}: {operate_name}, 操作失败! o(╥﹏╥)o"
        self.sys_status_label.setText(message)

        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("错误提示", operate_name, QtGui.QIcon("./favicon.ico"), 10000)
            wx_push_content(message)
        else:
            logger.warning("System tray message not supported")

        logger.error('Error notification shown')

    @logger.catch
    def sys_tips(self, content, _=None):
        """Show system notification"""
        message = f"{get_cur_time()}: {content}"
        self.sys_status_label.setText(message)

        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("系统提示", content, QtGui.QIcon("./favicon.ico"), 10000)
            wx_push_content(content)
        else:
            logger.warning("System tray message not supported")

        logger.warning('System notification shown')

    @logger.catch
    def download_file_thread(self, _=None):
        """Start download thread for all images"""
        if not constants.SpiderConfig.stop_download_image_flag:
            self.error_tips("下载图片操作")
            return

        spider_thread = threading.Thread(
            target=download_img_txt,
            args=(self,)
        )
        spider_thread.start()
        constants.SpiderConfig.stop_download_image_flag = False
        logger.info("Download image thread started")

    @logger.catch
    def set_video_position_click(self, position, _=None):
        """Set video playback position"""
        try:
            cv2.setTrackbarPos('Position', 'Video', position)
            logger.info(f"Video position set to: {position * 1000}")
        except Exception as e:
            logger.error(f"Error setting video position: {e}")
            self.error_tips("快进视频操作")

    @logger.catch
    def play_video(self, _=None):
        """Play selected video"""
        play_video_process(self)

    @logger.catch
    def pause_video(self, _=None):
        """Pause/resume video playback"""
        current_pos = cv2.getTrackbarPos('Position', 'Video')
        if current_pos > 0:
            cv2.setTrackbarPos('Position', 'Video', 0)
        else:
            cv2.setTrackbarPos('Position', 'Video', current_pos)
            cv2.waitKey(1)
            cv2.setTrackbarPos('Position', 'Video', 0)
            cv2.waitKey(1000)

    @logger.catch
    def image_video_click(self, _=None):
        """Convert images to video"""
        if constants.SpiderConfig.process_image_flag:
            self.error_tips("生成视频操作")
            return

        self.images_convert_thread = threading.Thread(
            target=process_images_thread,
            args=(self,)
        )
        self.images_convert_thread.start()
        constants.SpiderConfig.process_image_flag = True
        logger.success("Image processing thread started")

    @logger.catch
    def zoom_in_method(self, _=None):
        """Zoom in on image"""
        try:
            new_size = self.pixmap_image_tab1.size() * float(zoom_in_scale)
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(
                new_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"Image zoomed in to size: {new_size}")
        except Exception as e:
            logger.warning(f"Zoom in failed: {e}")

    @logger.catch
    def zoom_out_method(self, _=None):
        """Zoom out on image"""
        try:
            new_size = self.pixmap_image_tab1.size() * float(zoom_out_scale)
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(
                new_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"Image zoomed out to size: {new_size}")
        except Exception as e:
            logger.warning(f"Zoom out failed: {e}")

    @logger.catch
    def eventFilter(self, obj, event, _=None):
        """Handle mouse events for image dragging"""
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.isDragging = True
                self.dragStartPos = event.pos() - self.label.pos()
                self.lastMousePos = event.pos()

        elif event.type() == QEvent.MouseMove and self.isDragging:
            dx = event.pos().x() - self.lastMousePos.x()
            dy = event.pos().y() - self.lastMousePos.y()
            newPos = self.label.pos() + QPoint(dx, dy)
            self.label.move(newPos)
            self.lastMousePos = event.pos()

        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.isDragging = False

        return super().eventFilter(obj, event)

    @logger.catch
    def download_gif_zip_click(self, _=None):
        """Download and process GIF zip files"""
        if constants.SpiderConfig.download_gif_zip_flag:
            logger.warning("GIF zip download already in progress")
            self.error_tips("下载动态操作")
            return

        self.download_gif_zip_thread = threading.Thread(
            target=url_zip_all_process,
            args=(scan_directory_zip_txt(constants.data_path),)
        )
        self.download_gif_zip_thread.start()
        constants.SpiderConfig.download_gif_zip_flag = True
        logger.success("GIF zip download thread started")

    @logger.catch
    def unzip_generate_video_click(self, _=None):
        """Unzip files and generate videos"""
        if constants.SpiderConfig.unzip_generate_video_flag:
            logger.warning("Video generation already in progress")
            self.error_tips("解压生成gif视频操作")
            return

        self.unzip_generate_video_thread = threading.Thread(
            target=unzip_generate_gif,
            args=()
        )
        self.unzip_generate_video_thread.start()
        constants.SpiderConfig.unzip_generate_video_flag = True
        logger.success("Video generation thread started")

    @logger.catch
    def download_video_zip_click(self, _=None):
        """Download video zip file from link"""
        if constants.SpiderConfig.download_video_link_flag:
            logger.warning("Video download already in progress")
            self.error_tips("下载gif压缩包操作")
            return

        link = self.edt_input_file_text_3.text()
        logger.info(f"Starting download from link: {link}")

        self.start_download_file_link_thread = threading.Thread(
            target=start_download_file_link,
            args=(link,)
        )
        constants.SpiderConfig.download_video_link_flag = True
        self.start_download_file_link_thread.start()
        logger.success("Video download thread started")

    def closeEvent(self, event):
        """Handle application close event"""
        logger.warning("Main UI close button clicked - application closing...")
        self.quit_app()

    @logger.catch
    def open_data_dir(self, _=None):
        """Open data directory in file explorer"""
        self.open_data_path_thread = threading.Thread(
            target=open_data_path_method,
            args=()
        )
        self.open_data_path_thread.start()
        logger.success("Data directory opened")

    @logger.catch
    def show_log_output(self, _=None):
        """Show log output dialog"""
        show_log_output_method()

    @logger.catch
    def re_translate_ui(self, _=None):
        """Retranslate UI elements"""
        _translate = QtCore.QCoreApplication.translate
        self.ui.setWindowTitle(_translate("MainWindow", "USB Listen"))
        self.ui.setWindowIcon(QtGui.QIcon("./favicon.ico"))

    @logger.catch
    def set_tray_icon(self, _=None):
        """Setup system tray icon and menu"""
        # Create actions
        self.openMainWindowAction = QtWidgets.QAction("模拟系统消息")
        self.quitAppAction = QtWidgets.QAction("退出")

        # Connect actions
        self.openMainWindowAction.triggered.connect(self.windows_message)
        self.quitAppAction.triggered.connect(self.quit_app)

        # Create tray menu
        self.trayIconMenu = QtWidgets.QMenu()
        self.trayIconMenu.addAction(self.openMainWindowAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAppAction)

        # Setup tray icon
        self.trayIcon = QtWidgets.QSystemTrayIcon()
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QtGui.QIcon("./favicon.ico"))
        self.trayIcon.setToolTip("Spider Image System")
        self.trayIcon.activated[QtWidgets.QSystemTrayIcon.ActivationReason].connect(self.open_main_window)
        self.trayIcon.show()

    @logger.catch
    def open_main_window(self, reason, _=None):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    @logger.catch
    def windows_message(self, _=None):
        """Show system tray message"""
        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage(
                "系统提示",
                "模拟系统提示!",
                QtGui.QIcon("./favicon.ico"),
                10000
            )
        else:
            logger.warning("System tray messages not supported")

    @logger.catch
    def quit_app(self, _=None):
        """Handle application quit with confirmation"""
        reply = QtWidgets.QMessageBox.information(
            self,
            "退出确认",
            "是否确认退出？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            on_last_window_closed()
            logger.success(f"Spider image system {constants.sis_server_version} shutting down")
            logger.info("------------------------------Log end record-------------------------------")
            QtWidgets.qApp.quit()
