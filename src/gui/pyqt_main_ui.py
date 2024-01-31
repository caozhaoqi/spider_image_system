#!coding: utf - 8
import re
import threading

import cv2
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QFileDialog
from loguru import logger

from gui import constants
from gui.constants import sis_server_version, zoom_out_scale, zoom_in_scale
from utils.async_message_box import show_msg_alert
from utils.base_event import scan_populate_mp4_list
from utils.file_process import scan_directory_zip_txt
from utils.get_url import spider_artworks_url
from gui.spider_base_ui import base_menu, tab_ui_tab, tab_1_ui_paint, tab_2_ui_paint, tab_3_ui_paint
from utils.http_request import url_zip_all_process, unzip_generate_gif
from utils.spider_img_save import download_img_txt
from utils.img_switch import find_images, show_image, folder_path, show_next_image, check_images, img_category_images, \
    show_filter_image
from utils.video_process import process_images_thread, play_video_process

current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


class UIMainWindows(QMainWindow):

    # @logger.catch
    def __init__(self):
        QWidget.__init__(self)
        # 窗体标题 icon
        self.unzip_generate_video_thread = None
        self.download_gif_zip_thread = None
        self.pixmap_image_tab1 = None
        self.file_text_3 = None
        self.images_convert_thread = None
        self.show_page_label = None
        self.setWindowTitle(u"Spider Image System (Version: " + sis_server_version + ")")
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
        tab_3_ui_paint(self)
        # load cur dir MP4 video
        scan_populate_mp4_list(self)
        # 获取屏幕大小 窗口大小
        self.isDragging = False
        self.dragStartPos = None
        self.lastMousePos = None
        self.scaleFactor = 1.0
        self.label.installEventFilter(self)
        # # 设置窗口大小为屏幕大小
        show_next_image(self)
        self.showMaximized()  # 最大化窗口

    def jump_point_image_click(self):
        """
        跳转指定页面
        :return:
        """
        images_list = find_images(constants.data_path)
        if len(images_list) == 0:
            logger.warning("jump image, no image!")
            return False
        image_keyword = self.image_page.text()
        if image_keyword == '' or image_keyword is None:
            logger.warning("input error!")
            return False
        numbers = re.findall(r'\d+', image_keyword)
        letters = re.findall('[a-zA-Z]+', image_keyword)
        logger.info(f"you input search keyword: {numbers}, {letters}")
        # logger.info("跳转指定页码，或显示指定结果。")
        if numbers[0] and len(letters) == 0:
            # 存在数字 并且不存在字母
            logger.info(f"start jump image page {image_keyword}")
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
            logger.warning("dir not image , or other err! detail: " + str(e))

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
            logger.warning("dir not image , or other err! detail: " + str(e))

    # @logger.catch
    def input_keyword_process(self):
        """
        选择数据路径
        :return:
        """
        if not constants.stop_spider_url_flag:
            # 正在抓取
            self.error_tips()
        else:
            key_word = self.file_text.text()
            if key_word == '' or key_word is None:
                logger.warning("input keyword empty or error!")
                return False
            logger.debug("you input key word is: " + str(key_word))
            # 读取用户输入路径
            spider_thread_obj = threading.Thread(
                target=spider_artworks_url,
                args=(self, key_word,))
            spider_thread_obj.start()
            constants.stop_spider_url_flag = False
            logger.info("spider img thread starting ... ")
        # self.error_path()

    def input_keyword_process_3(self):
        """
        选中指定文件夹tab 3
        :return:
        """
        self.file_text_3 = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if self.file_text_3:
            logger.debug('Selected folder:' + self.file_text_3)
        # else:
        #     self.errorpath()
        self.filetext.setText(self.file_text_3)

    def download_file_thread_3(self):
        """
        下载指定txt中url对应images
        :return:
        """
        logger.info("start scan images... ")
        scan_image_thread_obj = threading.Thread(
            target=check_images,
            args=(self, constants.data_path))
        scan_image_thread_obj.start()
        pass

    def img_category_button_click(self):
        """
        图片分类
        :return:
        """
        logger.info('start img category...')
        img_category_thread_obj = threading.Thread(
            target=img_category_images,
            args=(self, constants.data_path))
        img_category_thread_obj.start()

    # @logger.catch
    def success_tips(self):
        """
        success tips
        :return:
        """
        logger.success('show success tips.')
        # success_tips_thread = threading.Thread(
        #     target=show_msg_alert,
        #     args=(self, "完成", "完成！",))
        # success_tips_thread.start()
        # show_msg_alert("完成", "完成！")

    # @logger.catch
    def error_tips(self):
        """
        error tips
        :return:
        """
        logger.error('show error tips.')
        # error_tips_thread = threading.Thread(
        #     target=show_msg_alert,
        #     args=(self, "错误", "请等待当前操作完成！",))
        # error_tips_thread.start()
        # show_msg_alert("完成", "完成！")

    # @logger.catch
    def download_file_thread(self):
        """
        下载所有图片进程
        :return:
        """
        # ret = True
        if not constants.stop_download_image_flag:
            self.error_tips()
        else:
            spider_thread_obj = threading.Thread(
                target=download_img_txt,
                args=(self,))
            spider_thread_obj.start()
            constants.stop_download_image_flag = False
            logger.info("download img thread starting... ")
        # self.error_path()

    def set_video_position_click(self, position):
        """
        更改设置视频播放位置
        unuse
        @:parameter position 位置
        """
        # self.media_player.setPosition(position * 1000)
        try:
            cv2.setTrackbarPos('Position', 'Video', position)
            logger.info("current position: " + str(position * 1000))  # 设置视频位置，单位为毫秒
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
        if cv2.getTrackbarPos('Position', 'Video') > 0:  # 确保视频正在播放中
            cv2.setTrackbarPos('Position', 'Video', 0)  # 暂停在开始位置
        else:  # 如果已经暂停，则恢复播放到当前位置
            cv2.setTrackbarPos('Position', 'Video', cv2.getTrackbarPos('Position', 'Video'))
            cv2.waitKey(1)  # 等待用户操作，避免立即继续播放导致界面闪烁
            cv2.setTrackbarPos('Position', 'Video', 0)  # 暂停在开始位置，确保视频从当前位置继续播放
            cv2.waitKey(1000)  # 等待一段时间（如1秒），让用户看到暂停效果后再恢复播放

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
            new_size = self.pixmap_image_tab1.size() * float(zoom_in_scale)  # 放大10%
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(new_size, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"scale zoom in new_size {new_size}")
        except Exception as e:
            logger.warning(f"unknown error! detail {e}")

    def zoom_out_method(self):
        """
        缩小
        :return:
        """
        try:
            new_size = self.pixmap_image_tab1.size() * float(zoom_out_scale)  # 缩小90%
            self.pixmap_image_tab1 = self.pixmap_image_tab1.scaled(new_size, Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmap_image_tab1)
            logger.info(f"scale zoom out new_size {new_size}")
        except Exception as e:
            logger.warning(f"unknown error! detail {e}")

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
                self.dragStartPos = event.pos() - self.label.pos()  # 记录鼠标和标签的相对位置
                self.lastMousePos = event.pos()  # 记录上一次鼠标的位置
        elif event.type() == QEvent.MouseMove and self.isDragging:
            dx = event.pos().x() - self.lastMousePos.x()  # 计算鼠标的移动距离
            dy = event.pos().y() - self.lastMousePos.y()  # 计算鼠标的移动距离
            newPos = self.label.pos() + QPoint(dx, dy)  # 更新标签的位置
            self.label.move(newPos)  # 移动标签到新位置
            self.lastMousePos = event.pos()  # 更新上一次鼠标的位置
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.isDragging = False
        return super().eventFilter(obj, event)

    def download_gif_zip_click(self):
        """

        :return:
        """
        self.download_gif_zip_thread = threading.Thread(
            target=url_zip_all_process,
            args=(self, scan_directory_zip_txt(constants.data_path), ))
        self.download_gif_zip_thread.start()
        # if url_zip_all_process():
        logger.success("success download zip  file thread start")
        #     self.success_tips()
        # else:
        #     self.error_tips()

    def unzip_generate_video_click(self):
        """

        :return:
        """
        # if unzip_generate_gif():
        #     logger.success("success unzip generate file")
        #     self.success_tips()
        # else:
        #     self.error_tips()

        self.unzip_generate_video_thread = threading.Thread(
            target=unzip_generate_gif,
            args=(self, ))
        self.unzip_generate_video_thread.start()
        # if url_zip_all_process():
        logger.success("success unzip generate file thread start")