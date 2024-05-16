#!coding: utf - 8
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from image.spider_img_save import download_img_txt, remove_error_image, img_category_button
from image.video_process import play_video_process, process_images_thread
from ui_event.base_event import scan_populate_mp4_list, exit_save_data
from ui_event.get_url import spider_artworks_url
from ui_event.spider_base_ui import base_menu, tab_1_ui_paint, tab_2_ui_paint, tab_3_ui_paint, tab_ui_tab
from ui_event.log_show_dialog import show_log_output_method
from utils.time_utils import get_cur_time
from ui_event.base_event import on_last_window_closed

current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


@logger.catch
def open_data_path_method():
    """

    :return:
    """
    try:
        if os.name == 'nt':  # Windows
            os.startfile(constants.data_path)
        else:
            import subprocess
            subprocess.Popen(['xdg-open', constants.data_path])

        logger.success(f"open data path: {constants.data_path} success!")
    except Exception as e:
        logger.error(f"open data path: {constants.data_path} fail, detail: {e}")


class UIMainWindows(QMainWindow):

    @logger.catch
    def __init__(self):
        """

        """
        QWidget.__init__(self)
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
        self.setWindowTitle(u"Spider Image System " + sis_server_version + ")")
        icon = QIcon()
        icon.addPixmap(
            QPixmap("../run/favicon.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.setMenuBar(base_menu(self))
        self.tab1, self.tab2, self.tab3, self.tab_widget = tab_ui_tab(self)

        tab_1_ui_paint(self)
        tab_2_ui_paint(self)
        tab_3_ui_paint(self)

        scan_populate_mp4_list(self)

        self.isDragging = False
        self.dragStartPos = None
        self.lastMousePos = None
        self.scaleFactor = 1.0
        self.label.installEventFilter(self)
        self.showMaximized()
        # init ui show
        self.spider_mode_show_label.setText(constants.spider_mode)

        # 配置最小化
        self.set_tray_icon()

    @logger.catch
    def jump_point_image_click(self, _=None):
        """
        跳转指定页面
        :return:
        """
        images_list = find_images(constants.data_path)
        if len(images_list) == 0:
            logger.warning("jump image error, no image!")
            return False
        image_keyword = self.image_page.text()
        if image_keyword == '' or image_keyword is None:
            logger.warning("input keyword error!")
            return False
        numbers = re.findall(r'\d+', image_keyword)
        letters = re.findall('[a-zA-Z]+', image_keyword)
        logger.info(f"you input search keyword: {numbers}, {letters}")
        if numbers[0] and len(letters) == 0:
            # 存在数字 并且不存在字母
            logger.info(f"start jump image page: {image_keyword}")
            self.jump_point_image_page(int(image_keyword))
        else:
            logger.info(f"start jump image page, image name keyword {image_keyword}")
            for index, image_content in enumerate(images_list):
                if image_keyword in image_content:
                    self.jump_point_image_page(index)
                    break
        logger.info(f"jump success! current page {numbers[0]}")

    # @staticmethod
    @logger.catch
    def next_img(self, _=None):
        """
        跳转下一页
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

    @logger.catch
    def before_img(self, _=None):
        """
        跳转前一页面
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
            logger.warning("dir not image, or other err! detail: " + str(e))

    @logger.catch
    def jump_point_image_page(self, index, _=None):
        """
        跳转指定页面
        :param _:
        :param index:
        :param self:
        :return:
        """
        try:
            global image_files, current_image_index
            current_image_index = index
            show_image(self, image_files[current_image_index])
            self.show_page_label.setText(str(current_image_index) + "/" + str(len(image_files)))
            logger.info("after image show, current page: " + str(current_image_index) + ", count page: " + str(
                len(image_files)))
        except Exception as e:
            logger.warning("dir not image, or other err! detail: " + str(e))

    @logger.catch
    def input_keyword_process(self, _=None):
        """
        选择数据路径
        :return:
        """
        if not constants.stop_spider_url_flag:
            self.error_tips("爬取操作")
        else:
            constants.spider_mode = 'manual'
            key_word = self.file_text.text()
            if key_word == '' or key_word is None:
                logger.warning("input keyword empty or error!")
                return False
            logger.debug("you input keyword is: " + str(key_word))
            spider_thread_obj = threading.Thread(
                target=spider_artworks_url,
                args=(self, key_word,))
            spider_thread_obj.start()
            constants.stop_spider_url_flag = False
            logger.info("spider img thread starting... ")

    @logger.catch
    def input_keyword_process_3(self, _=None):
        """
        选中指定文件夹tab 3
        :return:
        """
        self.edt_input_file_text_3_str = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if self.edt_input_file_text_3_str:
            logger.debug('Selected folder:' + self.edt_input_file_text_3_str)
        self.edt_input_file_text_3.setText(self.edt_input_file_text_3_str)

    @logger.catch
    def remove_error_image_click(self, _=None):
        """
        下载指定txt中url对应images
        :return:
        """
        if constants.single_flag:
            self.error_tips("删除错误图片操作")
            return
        constants.single_flag = True
        remove_error_image(self)

    @logger.catch
    def img_category_button_click(self, _=None):
        """
        图片分类
        :return:
        """
        if constants.single_flag:
            self.error_tips("图片分类操作")
            return
        constants.single_flag = True
        img_category_button(self)

    @logger.catch
    def success_tips(self, operate_name, _=None):
        """
        success tips
        :param _:
        :param operate_name
        :return:
        """
        # show_toast_thread("操作完成(*^▽^*)！")
        self.sys_status_label.setText(f"{get_cur_time()}: {operate_name}, 操作完成! (*^▽^*)")
        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("成功提示", operate_name, QtGui.QIcon("./favicon.ico"), 10000)
        else:
            logger.warning("ERROR: windowsMessage()")
        logger.success('show success tips.')

    @logger.catch
    def error_tips(self, operate_name, _=None):
        """
        error tips
        :param _:
        :param operate_name
        :return:
        """
        # show_toast_thread("操作失败o(╥﹏╥)o！")
        self.sys_status_label.setText(f"{get_cur_time()}: {operate_name}, 操作失败! o(╥﹏╥)o")
        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("错误提示", operate_name, QtGui.QIcon("./favicon.ico"), 10000)
        else:
            logger.warning("ERROR: windowsMessage()")
        logger.error('show error tips.')

    @logger.catch
    def sys_tips(self, content, _=None):
        """
        show sys tips
        :param _:
        :param content:
        :return:
        """
        self.sys_status_label.setText(f"{get_cur_time()}: {content}")
        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("系统提示", content, QtGui.QIcon("./favicon.ico"), 10000)
        else:
            logger.warning("ERROR: windowsMessage()")
        logger.warning('show sys tips.')

    @logger.catch
    def download_file_thread(self, _=None):
        """
        下载所有图片进程
        :return:
        """
        if not constants.stop_download_image_flag:
            self.error_tips("下载图片操作")
        else:
            spider_thread_obj = threading.Thread(
                target=download_img_txt,
                args=(self,))
            spider_thread_obj.start()
            constants.stop_download_image_flag = False
            logger.info("download img thread starting... ")

    @logger.catch
    def set_video_position_click(self, position, _=None):
        """
        更改设置视频播放位置
        unuse
        @:parameter position 位置
        """
        try:
            cv2.setTrackbarPos('Position', 'Video', position)
            logger.info("current position: " + str(position * 1000))
        except Exception as e:
            logger.error("error, detail: " + str(e))
            self.error_tips("快进视频操作")

    @logger.catch
    def play_video(self, _=None):
        """
        播放指定视频
        :return:
        """
        play_video_process(self)

    @logger.catch
    def pause_video(self, _=None):
        """

        :return:
        """
        if cv2.getTrackbarPos('Position', 'Video') > 0:
            cv2.setTrackbarPos('Position', 'Video', 0)
        else:
            cv2.setTrackbarPos('Position', 'Video', cv2.getTrackbarPos('Position', 'Video'))
            cv2.waitKey(1)
            cv2.setTrackbarPos('Position', 'Video', 0)
            cv2.waitKey(1000)

    @logger.catch
    def image_video_click(self, _=None):
        """
        image 生成视频
        :return:
        """
        if constants.process_image_flag:
            self.error_tips("生成视频操作")
        else:
            self.images_convert_thread = threading.Thread(
                target=process_images_thread,
                args=(self,))
            self.images_convert_thread.start()
            logger.success("spider image process starting. ")
            constants.process_image_flag = True
        pass

    @logger.catch
    def zoom_in_method(self, _=None):
        """
        放大
        :return:
        """
        try:
            new_size = self.pixmap_image_tab1.size() * float(zoom_in_scale)
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(new_size, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"scale zoom in new_size: {new_size}")
        except Exception as e:
            logger.warning(f"unknown error! detail: {e}")

    @logger.catch
    def zoom_out_method(self, _=None):
        """
        缩小
        :return:
        """
        try:
            new_size = self.pixmap_image_tab1.size() * float(zoom_out_scale)
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(new_size, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"scale zoom out new_size: {new_size}")
        except Exception as e:
            logger.warning(f"unknown error! detail: {e}")

    @logger.catch
    def eventFilter(self, obj, event, _=None):
        """
        拖动控制
        :param _:
        :param obj:
        :param event:
        :return:
        """
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
        """
        Download file from point url
        :return:
        """
        if constants.download_gif_zip_flag:
            logger.warning("download_gif_zip ing.")
            self.error_tips("下载动态操作")
        else:
            self.download_gif_zip_thread = threading.Thread(
                target=url_zip_all_process,
                args=(scan_directory_zip_txt(constants.data_path),))
            self.download_gif_zip_thread.start()
            constants.download_gif_zip_flag = True
            logger.success("success download zip file thread start")

    @logger.catch
    def unzip_generate_video_click(self, _=None):
        """
        unzip file generate video from file.
        :return:
        """
        if constants.unzip_generate_video_flag:
            logger.warning("len(zip_url_txt) is null.")
            self.error_tips("解压生成gif视频操作")
        else:
            self.unzip_generate_video_thread = threading.Thread(
                target=unzip_generate_gif,
                args=())
            self.unzip_generate_video_thread.start()
            constants.unzip_generate_video_flag = True
            logger.success("success unzip generate file thread start")

    @logger.catch
    def download_video_zip_click(self, _=None):
        """
        download video zip file from link
        :return:
        """
        if constants.download_video_link_flag:
            logger.warning("already downloading file, please wait！")
            self.error_tips("下载gif压缩包操作")
        else:
            logger.info("start download file!")
            link = self.edt_input_file_text_3.text()
            logger.info(f"you input link: {link}")
            self.start_download_file_link_thread = threading.Thread(
                target=start_download_file_link,
                args=(link,))
            constants.download_video_link_flag = True
            self.start_download_file_link_thread.start()
            logger.success("success download file thread start")

    # def closeEvent(self, event):
    #     """
    #
    #     :param event:
    #     :return:
    #     """
    #     logger.warning("Exe main ui will closing...")
    #     exit_save_data()

    @logger.catch
    def open_data_dir(self, _=None):
        """
        open sys data dir
        :return:
        """
        self.open_data_path_thread = threading.Thread(
            target=open_data_path_method,
            args=())
        self.open_data_path_thread.start()
        logger.success("success open data path start")

    @logger.catch
    def show_log_output(self, _=None):
        """

        :return:
        """
        show_log_output_method()

    @logger.catch
    def re_translate_ui(self, _=None):
        """
        设置主界面
        :return:
        """
        _translate = QtCore.QCoreApplication.translate
        self.ui.setWindowTitle(_translate("MainWindow", "USB Listen"))
        self.ui.setWindowIcon(QtGui.QIcon("./favicon.ico"))

    @logger.catch
    def set_tray_icon(self, _=None):
        """
        最小化右键菜单
        :return:
        """
        # 初始化菜单单项
        self.openMainWindowAction = QtWidgets.QAction("模拟系统消息")
        self.quitAppAction = QtWidgets.QAction("退出")

        # 菜单单项连接方法
        self.openMainWindowAction.triggered.connect(self.windows_message)
        self.quitAppAction.triggered.connect(self.quit_app)

        # 初始化菜单列表
        self.trayIconMenu = QtWidgets.QMenu()
        self.trayIconMenu.addAction(self.openMainWindowAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAppAction)

        # 构建菜单UI
        self.trayIcon = QtWidgets.QSystemTrayIcon()
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QtGui.QIcon("./favicon.ico"))
        self.trayIcon.setToolTip("双击打开程序")
        # 左键双击打开主界面
        self.trayIcon.activated[QtWidgets.QSystemTrayIcon.ActivationReason].connect(self.open_main_window)
        # 允许托盘菜单显示
        self.trayIcon.show()

    @logger.catch
    def open_main_window(self, reason, _=None):
        """
        双击打开主界面并使其活动
        :param reason:
        :return:
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    @logger.catch
    def windows_message(self, _=None):
        """
        配置显示 windows 系统消息通知
        :return:
        """
        # print("example")
        if self.trayIcon.supportsMessages() and self.trayIcon.isSystemTrayAvailable():
            self.trayIcon.showMessage("系统提示", "模拟系统提示！", QtGui.QIcon("./favicon.ico"), 10000)
        else:
            logger.warning("ERROR: windowsMessage()")

    @logger.catch
    def quit_app(self, _=None):
        """
        包含二次确认的退出
        :return:
        """
        checkFlag = QtWidgets.QMessageBox.information(self, "退出确认", "是否确认退出？",
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if checkFlag == QtWidgets.QMessageBox.Yes:
            on_last_window_closed()
            logger.success(f"spider image system {constants.sis_server_version} will quit!")
            logger.info("------------------------------log end record-------------------------------")
            QtWidgets.qApp.quit()
        else:
            pass
