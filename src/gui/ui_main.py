#!coding:utf-8
import threading

import sys

import cv2
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QMainWindow, QMessageBox, QLabel, QFileDialog
from loguru import logger

from gui import constants
from gui.button_control import spider_btn_control
from gui.constants import sis_server_version
from utils.async_message_box import show_msg_alert
from utils.base_event import scan_populate_mp4_list
from utils.get_url import spider_artworks_url
from gui.spider_base_ui import base_menu, tab_ui_tab, tab_1_ui_paint, tab_2_ui_paint, tab_3_ui_paint
from utils.spider_img_save import download_img_txt
from utils.img_switch import find_images, show_image, folder_path, show_next_image, check_images, img_category_images, \
    show_filter_image
from utils.log_record import log_record, check_version
from utils.video_process import process_images_thread

current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


class UIMainWindows(QMainWindow):

    # @logger.catch
    def __init__(self):
        QWidget.__init__(self)
        # 窗体标题 icon
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
        if not constants.stop_spider_url_flag:
            # 正在抓取
            self.error_tips()
        else:
            key_word = self.file_text.text()
            logger.debug("you input key word is :" + str(key_word))
            # 读取用户输入路径
            spider_thread_obj = threading.Thread(
                target=spider_artworks_url,
                args=(self, key_word,))
            spider_thread_obj.start()
            constants.stop_spider_url_flag = False
            logger.info("spider img thread starting ... ")
        # self.error_path()

    def input_keyword_process_3(self):
        self.file_text_3 = QFileDialog.getExistingDirectory(self, 'Open Folder', '')
        if self.file_text_3:
            logger.debug('Selected folder:' + self.file_text_3)
        else:
            self.errorpath()

        self.filetext.setText(self.file_text_3)

    def download_file_thread_3(self):
        logger.info("start scan images... ")
        scan_image_thread_obj = threading.Thread(
            target=check_images,
            args=(self, constants.data_path))
        scan_image_thread_obj.start()
        pass

    def img_category_button_click(self):
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
        show_msg_alert("完成", "完成！")

    # @logger.catch
    def error_tips(self):
        """
        error tips
        :return:
        """
        show_msg_alert("警告", "请等待当前操作完成！")

    # @logger.catch
    def download_file_thread(self):
        """

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
            logger.info("download img thread starting ... ")
        # self.error_path()

    def set_video_position_click(self, position):
        """设置视频播放位置"""
        # self.media_player.setPosition(position * 1000)
        try:
            cv2.setTrackbarPos('Position', 'Video', position)
            logger.info("current position: " + str(position * 1000))  # 设置视频位置，单位为毫秒
        except Exception as e:
            logger.error("error, detail: " + str(e))
            self.error_tips()

    def load_video(self, file_path):
        """加载视频文件"""
        # file_path_1, file_name = os.path.split(file_path)
        # self.file_name_label_video.setText(file_name)
        # content = QMediaContent(QUrl.fromLocalFile(file_path))  # 创建媒体内容对象，传入视频文件路径
        # self.media_player.setMedia(content)  # 设置媒体内容到QMediaPlayer中
        # self.media_player.play()  # 开始播放视频
        # logger.info("start load video, file path: " + file_path)

    def play_video(self):
        """

        :return:
        """
        try:
            if self.listWidget_4.selectedItems():
                selectedItem = self.listWidget_4.selectedItems()[0]
                selectedFilename = selectedItem.text()
                cap = cv2.VideoCapture(selectedFilename)
                # 创建窗口
                cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

                # 初始化时间戳和播放速度
                last_time = 0
                play_speed = 1.0

                # 创建跟踪条
                # 第一个参数是跟踪条的名称，第二个参数是窗口的名称，第三个参数是跟踪条的默认位置（0-100），第四个参数是跟踪条的长度
                # cv2.createTrackbar('Position', 'Video', 0, 100, lambda x: None)
                if cap.isOpened():
                    while True:
                        ret, frame = cap.read()
                        if not ret:  # 视频结束或出错
                            break
                        cv2.imshow('Video: ' + selectedFilename, frame)
                        # position = cv2.getTrackbarPos('Position', 'Video')
                        # 获取当前时间戳
                        current_time = int(cap.get(cv2.CAP_PROP_POS_MSEC)) // 1000

                        # 处理暂停/继续播放
                        if cv2.waitKey(1) & 0xFF == ord('p'):  # 按p键暂停/继续播放
                            if current_time > last_time:  # 如果当前时间大于上次时间，说明视频在播放，暂停播放
                                cap.set(cv2.CAP_PROP_POS_FRAMES, last_time)
                                logger.info("p pause or play video up!")
                            else:  # 否则，恢复播放
                                cap.set(cv2.CAP_PROP_POS_FRAMES, current_time)
                                logger.info("p replay video up!")
                            last_time = current_time  # 更新上次时间

                        # 处理前进/后退
                        if cv2.waitKey(1) & 0xFF == ord('f'):  # 按f键快进
                            if current_time > last_time:  # 如果当前时间大于上次时间，说明视频在播放，快进到指定位置
                                cap.set(cv2.CAP_PROP_POS_MSEC, (last_time + 1000) * 1000)  # 快进10秒
                                logger.info("f video speed up!")
                            else:  # 否则，快退到指定位置
                                cap.set(cv2.CAP_PROP_POS_MSEC, last_time * 1000)  # 退后1秒
                                logger.info("f video speed down!")

                            last_time = current_time  # 更新上次时间

                        # 处理倍速播放
                        if cv2.waitKey(1) & 0xFF == ord('+'):  # 按+键增加播放速度
                            play_speed += 0.1
                            cap.set(cv2.CAP_PROP_SPEED, play_speed)  # 设置新的播放速度
                            logger.info("+ play video speed up!")
                        if cv2.waitKey(1) & 0xFF == ord('-'):  # 按-键减少播放速度
                            play_speed -= 0.1
                            logger.info("- play video speed down!")
                            if play_speed < 0:  # 防止速度过小导致播放出现问题
                                play_speed = 0.1
                                logger.info("- play video speed < min reset play_speed = 0.1!")
                            cap.set(cv2.CAP_PROP_SPEED, play_speed)  # 设置新的播放速度

                        # 在视频帧上显示当前播放位置和播放速度（可选）
                        cv2.putText(frame, f"Pos: {current_time}ms, Speed: {play_speed}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        # cv2.putText(frame, str(position), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出播放
                            break
                    cap.release()
                    cv2.destroyAllWindows()
                else:
                    logger.error("Error opening video file:", selectedFilename)
            else:
                logger.warning("Please select a video file.")
        except Exception as e:
            logger.error("error, detail: " + str(e))

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
    check_version()
    ui_paint()
