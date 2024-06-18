import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.common import StaleElementReferenceException
import threading
import time
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QListWidgetItem
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
from utils.time_utils import time_to_utc, random_fw_time, get_cur_time
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


@logger.catch
def edit_config_msg():
    """
    update ini config msg
    :return:
    """
    if not constants.edit_config_msg_visible:
        dialog = Dialog()
        constants.edit_config_msg_visible = True
        logger.info("Config msg dialog show visible.")
        dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        dialog.exec_()
    else:
        logger.warning("Edit_config_msg dialog already open!")


@logger.catch
def visit_web():
    """
    visit
    :return:
    """
    QDesktopServices.openUrl(QUrl("https://caozhaoqi.github.io/"))
    logger.info("Jump target help web url.")


@logger.catch
def about_message_lookup():
    """
    about msg show
    :return:
    """
    if not constants.about_message_lookup_visible:
        information_dialog = InformationDialog()
        constants.about_message_lookup_visible = True
        logger.info("Show sis tools basic info.")
        information_dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        information_dialog.exec_()
    else:
        logger.warning("About_message_lookup_visible dialog already open!")


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
                # i += 1
    # logger.info("scan video result, length: " + str(i))


@logger.catch
def stop_spider_image():
    """
    stop spider images action
    :return:
    """
    if not constants.stop_spider_url_flag:
        constants.stop_spider_url_flag = True
        logger.warning("Flag stop_spider_url_flag set true!")
        return True
    else:
        logger.warning("Spider url already stop!")
        return False


@logger.catch
def auto_start_spider_image(self):
    """
    auto spider image thread
    @:param self.
    :return:
    """
    # spider_thread_obj = threading.Thread(
    #     target=auto_spider_img_thread,
    #     args=(self,))
    # spider_thread_obj.start()

    # read txt file spider keyword
    if not constants.stop_spider_url_flag:
        logger.error("Already spider img, please stop here before operate!")
        return False

    # 创建SISThreading类的实例并传递参数
    spider_thread_obj = SISThreading(target=auto_spider_img_thread, args=(self,))

    constants.stop_spider_url_flag = False

    # 启动线程
    spider_thread_obj.start()

    log_mon_war_thread_obj = threading.Thread(
        target=log_mon_war,
        args=(spider_thread_obj,))
    log_mon_war_thread_obj.start()


@logger.catch
def add_keyword_alert():
    """

    :return:
    """
    dialog = KeywordDialog()
    logger.info("Keyword msg dialog show visible.")
    # dialog.show()
    dialog.exec_()


@logger.catch
def auto_spider_img_thread(self):
    """
    auto spider img thread
    @:param self.
    :return:
    """
    logger.info("Auto spider img thread starting...")
    # detect spider work status
    if constants.log_no_output_flag and not constants.stop_spider_url_flag:
        constants.stop_spider_url_flag = False
    spider_image_keyword, txt_file_list = get_image_keyword()
    if len(spider_image_keyword) == 0 or spider_image_keyword == [] or spider_image_keyword == [[]]:
        logger.warning("Auto spider image null, please add keyword!")
        if self:
            self.sys_tips("Notice: spider_img_keyword.txt文件为空, 请先点击图像->关键字中添加关键字！")
        return False
    constants.spider_mode = 'auto'
    txt_index = 0
    for spider_img_keyword_detail in spider_image_keyword:
        logger.debug("Current spider kew word txt: " + str(spider_img_keyword_detail))
        # 读取用户输入路径
        constants.stop_spider_url_flag = False
        txt_index += 1
        for spider_image_keyword_item in spider_img_keyword_detail:
            logger.debug("Current spider kew word: " + str(spider_image_keyword_item.strip()))
            try:
                spider_artworks_url(self, spider_image_keyword_item.strip())
            except StaleElementReferenceException as sere:
                logger.warning(f"Unknown error, detail: {sere}")
            except Exception as e:
                logger.error(f"Unknown error, detail: {e}")
            if constants.stop_spider_url_flag:
                logger.warning(
                    f"Auto spider img stop! will exit, final spider keyword: {spider_image_keyword_item.strip()}!")
                break
            fire_wall_delay_time = random_fw_time(constants.fire_wall_delay_time)
            if constants.firewall_flag:
                logger.warning(f"Block {constants.visit_url} domain, will retry! cur random retry time:"
                               f" {float(fire_wall_delay_time)} seconds.")
                # 设置重试时间
                time.sleep(fire_wall_delay_time)
                continue
        if constants.stop_spider_url_flag:
            # stop auto mode spider
            logger.warning(f"Auto spider img stop! will exit, end spider txt name: {txt_file_list[txt_index - 1]}!")
            break


@logger.catch
def stop_download_image():
    """
    stop download image
    :return:
    """
    if not constants.stop_download_image_flag or not constants.download_image_re_flag:
        constants.stop_download_image_flag = True
        constants.download_image_re_flag = False
        logger.warning("Flag stop_download_mage_flag set true!")
        return True
    else:
        logger.warning("Download image already stop or not download image!")
        return False


@logger.catch
def online_look_image():
    """
    online image look event
    :return:
    """
    if not constants.online_look_image_visible:
        dialog = ImageDialog()
        dialog.showMaximized()
        dialog.show()
        dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("Online image viewer show!")
        constants.online_look_image_visible = True
        dialog.exec_()
    else:
        logger.warning("Online look msg already open!")


@logger.catch
def auto_play_image():
    """
    auto image play event
    :return:
    """
    if not constants.auto_play_image_visible:
        dialog = AutoImageDialog()
        dialog.showMaximized()
        dialog.show()
        dialog.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("Auto_play_image show!")
        constants.auto_play_image_visible = True
        dialog.exec_()
    else:
        logger.warning("Auto play image already show!")


@logger.catch
def performance_monitor():
    """
    performance monitor event
    :return:
    """
    if not constants.performance_monitor_visible:
        monitor = SystemMonitor()
        monitor.showMaximized()
        monitor.show()
        monitor.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("System info show!")
        constants.performance_monitor_visible = True
        monitor.exec_()
    else:
        logger.warning("Performance_monitor already show!")


@logger.catch
def log_analyze_ui():
    """

    :return:
    """
    if not constants.log_analyze_visible:
        dialog_lah = LogAnalyzeHistogram()
        dialog_lah.showMaximized()
        dialog_lah.show()
        dialog_lah.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("Log_analyze_visible show!")
        constants.log_analyze_visible = True
        dialog_lah.exec_()
    else:
        logger.warning("Genshin_impact_view already show!")


@logger.catch()
def encoding_tools_convert():
    """
    encoding_tools_convert
    :return:
    """
    scan_txt_file_all(constants.data_path)
    logger.success("Convert point txt finish!")


@logger.catch
def detect_installed_flag():
    """

    :return:
    """
    detect_installed_thread_obj = threading.Thread(
        target=detect_installed,
        args=())
    detect_installed_thread_obj.start()
    logger.debug("Detecting chrome webdriver start!")


@logger.catch
def face_detect_action():
    """

    :return:
    """
    if not constants.face_detect_flag:
        constants.face_detect_flag = True
        face_detect_thread_obj = threading.Thread(
            target=face_detect_result,
            args=(constants.data_path,))
        face_detect_thread_obj.start()
        logger.info("Start detect face!")
        return True
    else:
        logger.error("Detect face ing, please wait.")
        return False


@logger.catch
def convert_folder_name():
    """

    :return:
    """
    if not constants.convert_folder_name_flag:
        constants.convert_folder_name_flag = True
        convert_folder_thread_obj = threading.Thread(
            target=convert_and_move_folder,
            args=(os.path.join(constants.data_path, 'img_url'),))
        convert_folder_thread_obj.start()
        logger.info("Start convert folder_name!")
    else:
        logger.error("Converting folder_name please wait.")


@logger.catch
def user_upload_image():
    """

    :return:
    """
    if not constants.uploading_image_flag:
        constants.uploading_image_flag = True
        upload_image_thread_obj = threading.Thread(
            target=upload_image,
            args=(constants.basic_path,))
        upload_image_thread_obj.start()
        logger.info("Start upload image!")
        return True
    else:
        logger.error("Uploading image, please wait.")
        return False


@logger.catch
def user_download_image():
    """

    :return:
    """

    if not constants.download_image_re_flag:
        constants.download_image_re_flag = True
        download_re_error_threading_obj = threading.Thread(
            target=download_re_error_image,
            args=())
        download_re_error_threading_obj.start()
        logger.info("Start re error download image!")
    else:
        logger.error("Downloading error image, please wait.")


@logger.catch
def unzip_file_method():
    """

    :return:
    """
    if not constants.unzip_file_flag:
        constants.unzip_file_flag = True
        unzip_file_threading_obj = threading.Thread(
            target=unzip_file,
            args=(constants.data_path,))
        unzip_file_threading_obj.start()
        logger.info(f"Start unzip file! path: {constants.data_path}")
    else:
        logger.error("Unzip ing file, please wait.")


@logger.catch
def exit_save_data():
    """

    :return:
    """
    #     # 保存抓取进度 当有抓取任务时
    logger.warning("-------------------------------------------------------------")
    logger.warning(f"-----SIS-{constants.sis_server_version} exe will quit!-----------------")
    logger.warning("-------------------------------------------------------------")


@logger.catch
def kill_other_close():
    """

    :return:
    """
    try:
        if get_cur_os() == "win32":
            reduce_sys_res_usage()
            logger.success("Kill other process success!")
            kill_process_win('taskkill /im ui_main.exe /F /T')
        else:
            kill_process_linux('ui_main')
    except Exception as e:
        logger.error(f"Clear other process fail, detail: {e}")


@logger.catch
def img_category_ana():
    if not constants.img_analyze_visible:
        dialog_img = ImgAnalyzeHistogram()
        dialog_img.showMaximized()
        dialog_img.show()
        dialog_img.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("Img anal dialog show!")
        constants.img_analyze_visible = True
        dialog_img.exec_()
    else:
        logger.warning("Img anal dialog already show!")


@logger.catch
def on_last_window_closed():
    """

    :return:
    """
    logger.debug("Console window is closing...")
    exit_save_data()
    logger.debug("Start clean other process...")
    kill_other_close()


@logger.catch
def model_detect_img():
    """

    :return:
    """
    if not constants.detect_model_flag:
        constants.detect_model_flag = True
        detect_img_folder_thread_obj = threading.Thread(
            target=all_img_detect,
            args=(constants.data_path,))
        detect_img_folder_thread_obj.start()
        logger.info("Start detect img!")
    else:
        logger.error("Detecting img  please wait.")


@logger.catch
def start_download_jm():
    """

    :return:
    """
    if not constants.jm_dialog_visible:
        dialog_jm = JMDialog()
        # dialog_jm.showMaximized()
        dialog_jm.show()
        dialog_jm.setWindowFlag(Qt.WindowMinMaxButtonsHint)
        logger.info("Dialog_jm show!")
        constants.jm_dialog_visible = True
        dialog_jm.exec_()
    else:
        logger.warning("Dialog_jm already show!")


@logger.catch
def jm_domain_test_method():
    """

    :return:
    """
    # jm_domain_test()
    if not constants.jm_domain_detect_flag:
        constants.jm_domain_detect_flag = True
        jm_domain_detectr_thread_obj = threading.Thread(
            target=jm_domain_test,
            args=())
        jm_domain_detectr_thread_obj.start()
        logger.info("Start detect jm domain!")
    else:
        logger.error("Detecting jm domain, please wait.")


@logger.catch
def jm_automatic_method():
    """

    :return:
    """
    # JM_SD_auto_flag search_download_jm
    if not constants.JM_SD_auto_flag:
        constants.JM_SD_auto_flag = True
        jm_auto_thread_obj = threading.Thread(
            target=jm_auto_spider_img_thread,
            args=())
        jm_auto_thread_obj.start()
        logger.info("Start automatic spider and download jm image!")
    else:
        logger.error("Spider or downloading jm domain, please wait.")


@logger.catch
def stop_jm_spider():
    """

    :return:
    """
    if constants.JM_SD_auto_flag:
        constants.JM_SD_auto_flag = False
        logger.success("JM auto spider stop.")
    else:
        logger.warning("JM auto already stop.")
