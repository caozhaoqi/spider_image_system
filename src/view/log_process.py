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

router = APIRouter()


@logger.catch
@router.post("/spider_start/single", summary="开始爬取单个关键字", description='开始爬取单个关键字')
def start_spider_single_image(key_word: Union[str, None] = Query(default=..., alias="key_word")):
    """

    :param key_word:
    :return:
    """
    if not constants.stop_spider_url_flag:
        return JsonResponse.error("操作进行中！")
    else:
        constants.spider_mode = 'manual'
        if key_word == '' or key_word is None:
            logger.warning("input keyword empty or error!")
            return False
        logger.debug("you input keyword is: " + str(key_word))
        spider_thread_obj = threading.Thread(
            target=spider_artworks_url,
            args=(None, key_word,))
        spider_thread_obj.start()
        constants.stop_spider_url_flag = False
        logger.info("spider img thread starting... ")
        return JsonResponse.success("success!")


@logger.catch
@router.get("/spider_start/all", summary='开始爬取所有关键字', description='开始爬取所有关键字')
def spider_all_keyword():
    """

    :return:
    """

    spider_thread_obj = threading.Thread(
        target=auto_spider_img_thread,
        args=(None,))
    spider_thread_obj.start()
    if not constants.stop_spider_url_flag:
        return JsonResponse.error("already spider img, please stop here before operate!")
    else:
        return JsonResponse.success("start spider all keyword image")


@logger.catch
@router.get("/download_all_image/start/", summary='下载已爬取的所有图片', description='下载已爬取的所有图片')
def download_all_image():
    """

    :return:
    """
    if not constants.stop_download_image_flag:
        return JsonResponse.error("操作进行中！")
    else:
        spider_thread_obj = threading.Thread(
            target=download_img_txt,
            args=(None,))
        spider_thread_obj.start()
        constants.stop_download_image_flag = False
        logger.info("download img thread starting... ")
        return JsonResponse.success("download img thread starting... ")


@logger.catch
@router.get("/spider_image/stop", summary="停止爬取图片", description="停止爬取图片")
def stop_spider_image_api():
    """

    :return:
    """
    if stop_spider_image():
        return JsonResponse.success("stop success!")
    else:
        return JsonResponse.error("spider url already stop!")


@logger.catch
@router.get("/spider_image/download_stop", summary="停止下载图片", description="停止下载图片")
def stop_download_image_api():
    """

    :return:
    """
    if stop_download_image():
        return JsonResponse.success("stop success!")
    else:
        return JsonResponse.error("download image already stop!")


@logger.catch
@router.get("/spider_image/upload/", summary='上传所有图片至minio', description='上传所有图片至minio')
def upload_all_image():
    """

    :return:
    """

    if user_upload_image():
        return JsonResponse.success("start upload")
    else:
        return JsonResponse.error("uploading image, please wait.")


@logger.catch
@router.get("/spider_image/face_detect/", summary="人脸切割", description="人脸切割")
def start_face_detect():
    """

    :return:
    """
    if face_detect_action():
        return JsonResponse.success("start detect!")
    else:
        return JsonResponse.error("detecting, please wait...")
