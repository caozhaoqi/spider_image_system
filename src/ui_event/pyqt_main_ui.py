#!coding: utf - 8
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import threading
import cv2
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QFileDialog
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

current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


class UIMainWindows(QMainWindow):

    # @logger.catch
    def __init__(self):
        QWidget.__init__(self)
        self.edt_input_file_text_3_str = None
        self.edt_input_file_text_3 = None
        self.start_download_file_link_thread = None
        self.unzip_generate_video_thread = None
        self.download_gif_zip_thread = None
        self.pixmap_image_tab1 = None
        self.images_convert_thread = None
        self.show_page_label = None
        self.setWindowTitle(u"Spider Image System (Version: " + sis_server_version + ")")
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
        # default not show image click button show
        # show_next_image(self)
        self.showMaximized()

    def jump_point_image_click(self):
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

    # @logger.catch
    def next_img(self):
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

    # @logger.catch
    def before_img(self):
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

    def jump_point_image_page(self, index):
        """
        跳转指定页面
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

    # @logger.catch
    def input_keyword_process(self):
        """
        选择数据路径
        :return:
        """
        if not constants.stop_spider_url_flag:
            self.error_tips()
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

    def input_keyword_process_3(self):
        """
        选中指定文件夹tab 3
        :return:
        """
        self.edt_input_file_text_3_str = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if self.edt_input_file_text_3_str:
            logger.debug('Selected folder:' + self.edt_input_file_text_3_str)
        self.edt_input_file_text_3.setText(self.edt_input_file_text_3_str)

    def remove_error_image_click(self):
        """
        下载指定txt中url对应images
        :return:
        """
        if constants.single_flag:
            self.error_tips()
            return
        constants.single_flag = True
        remove_error_image(self)

    def img_category_button_click(self):
        """
        图片分类
        :return:
        """
        if constants.single_flag:
            self.error_tips()
            return
        constants.single_flag = True
        img_category_button(self)

    # @logger.catch
    def success_tips(self):
        """
        success tips
        :return:
        """
        logger.success('show success tips.')

    def error_tips(self):
        """
        error tips
        :return:
        """
        logger.error('show error tips.')

    # @logger.catch
    def download_file_thread(self):
        """
        下载所有图片进程
        :return:
        """
        if not constants.stop_download_image_flag:
            self.error_tips()
        else:
            spider_thread_obj = threading.Thread(
                target=download_img_txt,
                args=(self,))
            spider_thread_obj.start()
            constants.stop_download_image_flag = False
            logger.info("download img thread starting... ")

    def set_video_position_click(self, position):
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
            self.error_tips()

    def play_video(self):
        """
        播放指定视频
        :return:
        """
        play_video_process(self)

    def pause_video(self):
        if cv2.getTrackbarPos('Position', 'Video') > 0:
            cv2.setTrackbarPos('Position', 'Video', 0)
        else:
            cv2.setTrackbarPos('Position', 'Video', cv2.getTrackbarPos('Position', 'Video'))
            cv2.waitKey(1)
            cv2.setTrackbarPos('Position', 'Video', 0)
            cv2.waitKey(1000)

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
            logger.success("spider image process starting. ")
            constants.process_image_flag = True
        pass

    def zoom_in_method(self):
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

    def zoom_out_method(self):
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

    def eventFilter(self, obj, event):
        """
        拖动控制
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

    def download_gif_zip_click(self):
        """
        Download file from point url
        :return:
        """
        if constants.download_gif_zip_flag:
            logger.warning("download_gif_zip ing.")
            self.error_tips()
        else:
            self.download_gif_zip_thread = threading.Thread(
                target=url_zip_all_process,
                args=(scan_directory_zip_txt(constants.data_path),))
            self.download_gif_zip_thread.start()
            constants.download_gif_zip_flag = True
            logger.success("success download zip file thread start")

    def unzip_generate_video_click(self):
        """
        unzip file generate video from file.
        :return:
        """
        if constants.unzip_generate_video_flag:
            logger.warning("len(zip_url_txt) is null.")
            self.error_tips()
        else:
            self.unzip_generate_video_thread = threading.Thread(
                target=unzip_generate_gif,
                args=())
            self.unzip_generate_video_thread.start()
            constants.unzip_generate_video_flag = True
            logger.success("success unzip generate file thread start")

    def download_video_zip_click(self):
        """
        download video zip file from link
        :return:
        """
        if constants.download_video_link_flag:
            logger.warning("already downloading file, please wait！")
            self.error_tips()
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

    def closeEvent(self, event):
        """

        :param event:
        :return:
        """
        # 在这里处理窗口关闭事件
        logger.warning("Exe main ui will closing...")
        exit_save_data()
