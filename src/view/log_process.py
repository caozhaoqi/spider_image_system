# 导入OS模块
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
from typing import Union
from fastapi import APIRouter, Query
from loguru import logger
from http_tools.JsonResponse import JsonResponse
from image.spider_img_save import download_img_txt
from run import constants
from ui_event.base_event import auto_spider_img_thread, stop_spider_image, stop_download_image, user_upload_image, \
    face_detect_action
from ui_event.get_url import spider_artworks_url
from utils.log_monitor import log_mon_war
from utils.sis_therading import SISThreading
from utils.img_detect_ai import all_img_detect
from file.ini_file_spider import read_config_all
from utils.go_file_utils import upload_all_gofile
from utils.jm_domain_detect import jm_auto_spider_img_thread, jm_domain_test

router = APIRouter()


@logger.catch
@router.get("/spider_image/config", summary="lookup config ini file", description="lookup config ini file")
def lookup_file_config():
    """

    :return:
    """
    ret = read_config_all()
    if ret:
        return JsonResponse.success(ret)
    else:
        return JsonResponse.error("select config ini file fail.")


@logger.catch
@router.post("/spider_start/single", summary="开始爬取单个关键字", description='开始爬取单个关键字')
def start_spider_single_image(key_word: Union[str, None] = Query(default=..., alias="key_word")):
    """

    :param key_word:
    :return:
    """
    if not constants.stop_spider_url_flag:
        return JsonResponse.error("操作进行中!")
    else:
        constants.spider_mode = 'manual'
        if key_word == '' or key_word is None:
            logger.warning("Input keyword empty or error!")
            return False
        logger.debug("You input keyword is: " + str(key_word))
        spider_thread_obj = threading.Thread(
            target=spider_artworks_url,
            args=(None, key_word,))
        spider_thread_obj.start()
        constants.stop_spider_url_flag = False
        logger.info("Spider img thread starting... ")
        return JsonResponse.success("success!")


@logger.catch
@router.get("/spider_start/all", summary='开始爬取所有关键字', description='开始爬取所有关键字')
def spider_all_keyword():
    """

    :return:
    """

    # spider_thread_obj = threading.Thread(
    #     target=auto_spider_img_thread,
    #     args=(self,))
    # spider_thread_obj.start()

    # 创建SISThreading类的实例并传递参数
    # read txt file spider keyword
    # if not constants.stop_spider_url_flag:
    #     logger.error("Already spider img, please stop here before operate!")
    #     return False
    if not constants.stop_spider_url_flag:
        return JsonResponse.error("Already spider img, please stop here before operate!")
    else:
        spider_thread_obj = SISThreading(target=auto_spider_img_thread, args=(None,))

        constants.stop_spider_url_flag = False

        # 启动线程
        spider_thread_obj.start()

        log_mon_war_thread_obj = threading.Thread(
            target=log_mon_war,
            args=(spider_thread_obj,))
        log_mon_war_thread_obj.start()

        if constants.log_no_output_flag:
            spider_thread_obj.start()
            logger.warning("Log no output re start spider ing...")
            constants.log_no_output_flag = False

        return JsonResponse.success("Start spider all keyword image")


@logger.catch
@router.get("/download_all_image/start/", summary='下载已爬取的所有图片', description='下载已爬取的所有图片')
def download_all_image():
    """

    :return:
    """
    if not constants.stop_download_image_flag:
        return JsonResponse.error("操作进行中!")
    else:
        spider_thread_obj = threading.Thread(
            target=download_img_txt,
            args=(None,))
        spider_thread_obj.start()
        constants.stop_download_image_flag = False
        logger.info("Download img thread starting... ")
        return JsonResponse.success("Download img thread starting... ")


@logger.catch
@router.get("/spider_image/stop", summary="停止爬取图片", description="停止爬取图片")
def stop_spider_image_api():
    """

    :return:
    """
    if stop_spider_image():
        return JsonResponse.success("Stop success!")
    else:
        return JsonResponse.error("Spider url already stop!")


@logger.catch
@router.get("/spider_image/download_stop", summary="停止下载图片", description="停止下载图片")
def stop_download_image_api():
    """

    :return:
    """
    if stop_download_image():
        return JsonResponse.success("Stop success!")
    else:
        return JsonResponse.error("Download image already stop!")


@logger.catch
@router.get("/spider_image/upload/", summary='上传所有图片至minio', description='上传所有图片至minio')
def upload_all_image():
    """

    :return:
    """

    if user_upload_image():
        return JsonResponse.success("Start upload")
    else:
        return JsonResponse.error("Uploading image, please wait.")


@logger.catch
@router.get("/spider_image/face_detect/", summary="人脸切割", description="人脸切割")
def start_face_detect():
    """

    :return:
    """
    if face_detect_action():
        return JsonResponse.success("Start detect!")
    else:
        return JsonResponse.error("Detecting, please wait...")


@logger.catch
@router.get("/spider_image/detect_img/", summary="nsfw img detect", description="nsfw model detect image")
def detect_image_views():
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
        return JsonResponse.success("start detect image for nsfw.")
    else:
        logger.error("Detecting img  please wait.")
        return JsonResponse.error("Detecting img  please wait.")


@logger.catch
@router.post("/upload/gofile", summary="upload gofile file", description='upload gofile file')
def start_spider_single_image(
        path: Union[str, None] = Query(default=..., alias="path")
):
    """

    :param path:
    :return:
    """
    if not constants.GO_FILE_UPLOAD_FLAG:
        constants.GO_FILE_UPLOAD_FLAG = True
        gofile_auto_thread_obj = threading.Thread(
            target=upload_all_gofile,
            args=(path,))
        gofile_auto_thread_obj.start()
        logger.info("Start gofile upload image!")
        return JsonResponse.success("Start gofile upload image!")
    else:
        logger.error("Gofile uploading file, please wait.")
        return JsonResponse.error("Gofile uploading file, please wait.")


@logger.catch
@router.get("/jm/spider/all")
def jm_auto_spider():
    """

    """
    # JM_SD_auto_flag search_download_jm
    if not constants.JM_SD_auto_flag:
        constants.JM_SD_auto_flag = True
        jm_auto_thread_obj = threading.Thread(
            target=jm_auto_spider_img_thread,
            args=())
        jm_auto_thread_obj.start()
        logger.info("Start automatic spider and download jm image!")
        return JsonResponse.success("Start automatic spider and download jm image!")
    else:
        logger.error("Spider or downloading jm domain, please wait.")
        return JsonResponse.error("Spider or downloading jm domain, please wait.")


@logger.catch
@router.get("/jm/spider/detect")
def jm_detect_domain():
    """

    """
    # JM_SD_auto_flag search_download_jm
    if not constants.jm_domain_detect_flag:
        constants.jm_domain_detect_flag = True
        jm_domain_detectr_thread_obj = threading.Thread(
            target=jm_domain_test,
            args=())
        jm_domain_detectr_thread_obj.start()
        logger.info("Start detect jm domain!")
        return JsonResponse.success("Start detect jm domain, please check log get result!!!")
    else:
        logger.error("Detecting jm domain, please wait.")
        return JsonResponse.error("Detecting jm domain, please wait.")
