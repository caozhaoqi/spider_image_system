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
from ui_event.base_event import (
    auto_spider_img_thread, stop_spider_image, stop_download_image,
    user_upload_image, face_detect_action
)
from ui_event.get_url import spider_artworks_url
from utils.log_monitor import log_mon_war
from utils.sis_therading import SISThreading
from utils.img_detect_ai import all_img_detect
from file.ini_file_spider import read_config_all
from utils.go_file_utils import upload_all_gofile
from utils.jm_domain_detect import jm_auto_spider_img_thread, jm_domain_test

router = APIRouter()


@logger.catch
@router.get("/spider_image/config", 
    summary="lookup config ini file", 
    description="lookup config ini file")
def lookup_file_config():
    """查询配置文件内容"""
    ret = read_config_all()
    return JsonResponse.success(ret) if ret else JsonResponse.error("select config ini file fail.")


@logger.catch
@router.post("/spider_start/single", 
    summary="开始爬取单个关键字",
    description='开始爬取单个关键字')
def start_spider_single_image(key_word: Union[str, None] = Query(default=..., alias="key_word")):
    """爬取单个关键字的图片"""
    if not constants.SpiderConfig.stop_spider_url_flag:
        return JsonResponse.error("操作进行中!")

    if not key_word:
        logger.warning("Input keyword empty or error!")
        return JsonResponse.error("关键词不能为空")

    constants.SpiderConfig.spider_mode = 'manual'
    logger.debug(f"You input keyword is: {key_word}")
    
    spider_thread = threading.Thread(
        target=spider_artworks_url,
        args=(None, key_word,)
    )
    spider_thread.start()
    constants.SpiderConfig.stop_spider_url_flag = False
    
    logger.info("Spider img thread starting...")
    return JsonResponse.success("success!")


@logger.catch
@router.get("/spider_start/all", 
    summary='开始爬取所有关键字',
    description='开始爬取所有关键字')
def spider_all_keyword():
    """爬取所有关键字的图片"""
    if not constants.SpiderConfig.stop_spider_url_flag:
        return JsonResponse.error("Already spider img, please stop here before operate!")

    spider_thread = SISThreading(target=auto_spider_img_thread, args=(None,))
    constants.SpiderConfig.stop_spider_url_flag = False

    spider_thread.start()

    monitor_thread = threading.Thread(
        target=log_mon_war,
        args=(spider_thread,)
    )
    monitor_thread.start()

    if constants.ProcessingConfig.log_no_output_flag:
        spider_thread.start()
        logger.warning("Log no output re start spider ing...")
        constants.ProcessingConfig.log_no_output_flag = False

    return JsonResponse.success("Start spider all keyword image")


@logger.catch
@router.get("/download_all_image/start/", 
    summary='下载已爬取的所有图片',
    description='下载已爬取的所有图片')
def download_all_image():
    """下载所有已爬取的图片"""
    if not constants.SpiderConfig.stop_download_image_flag:
        return JsonResponse.error("操作进行中!")

    download_thread = threading.Thread(
        target=download_img_txt,
        args=(None,)
    )
    download_thread.start()
    constants.SpiderConfig.stop_download_image_flag = False
    
    logger.info("Download img thread starting...")
    return JsonResponse.success("Download img thread starting...")


@logger.catch
@router.get("/spider_image/stop", 
    summary="停止爬取图片",
    description="停止爬取图片")
def stop_spider_image_api():
    """停止爬虫任务"""
    return (JsonResponse.success("Stop success!") 
            if stop_spider_image() 
            else JsonResponse.error("Spider url already stop!"))


@logger.catch
@router.get("/spider_image/download_stop", 
    summary="停止下载图片",
    description="停止下载图片")
def stop_download_image_api():
    """停止下载任务"""
    return (JsonResponse.success("Stop success!")
            if stop_download_image()
            else JsonResponse.error("Download image already stop!"))


@logger.catch
@router.get("/spider_image/upload/", 
    summary='上传所有图片至minio',
    description='上传所有图片至minio')
def upload_all_image():
    """上传图片到MinIO"""
    return (JsonResponse.success("Start upload")
            if user_upload_image()
            else JsonResponse.error("Uploading image, please wait."))


@logger.catch
@router.get("/spider_image/face_detect/", 
    summary="人脸切割",
    description="人脸切割")
def start_face_detect():
    """开始人脸检测"""
    return (JsonResponse.success("Start detect!")
            if face_detect_action()
            else JsonResponse.error("Detecting, please wait..."))


@logger.catch
@router.get("/spider_image/detect_img/", 
    summary="nsfw img detect",
    description="nsfw model detect image")
def detect_image_views():
    """NSFW图片检测"""
    if constants.ProcessingConfig.detect_model_flag:
        return JsonResponse.error("Detecting img please wait.")

    constants.ProcessingConfig.detect_model_flag = True
    detect_thread = threading.Thread(
        target=all_img_detect,
        args=(constants.data_path,)
    )
    detect_thread.start()
    
    logger.info("Start detect img!")
    return JsonResponse.success("start detect image for nsfw.")


@logger.catch
@router.post("/upload/gofile", 
    summary="upload gofile file",
    description='upload gofile file')
def upload_to_gofile(path: Union[str, None] = Query(default=..., alias="path")):
    """上传文件到GoFile"""
    if constants.ProcessingConfig.go_file_upload_flag:
        return JsonResponse.error("Gofile uploading file, please wait.")

    constants.ProcessingConfig.go_file_upload_flag = True
    upload_thread = threading.Thread(
        target=upload_all_gofile,
        args=(path,)
    )
    upload_thread.start()
    
    logger.info("Start gofile upload image!")
    return JsonResponse.success("Start gofile upload image!")


@logger.catch
@router.get("/jm/spider/all")
def jm_auto_spider():
    """自动爬取JM图片"""
    if constants.ProcessingConfig.jm_sd_auto_flag:
        return JsonResponse.error("Spider or downloading jm domain, please wait.")

    constants.ProcessingConfig.jm_sd_auto_flag = True
    jm_thread = threading.Thread(target=jm_auto_spider_img_thread)
    jm_thread.start()
    
    logger.info("Start automatic spider and download jm image!")
    return JsonResponse.success("Start automatic spider and download jm image!")


@logger.catch
@router.get("/jm/spider/detect")
def jm_detect_domain():
    """检测JM域名"""
    if constants.ProcessingConfig.jm_sd_auto_flag:
        return JsonResponse.error("Detecting jm domain, please wait.")

    constants.ProcessingConfig.jm_sd_auto_flag = True
    detect_thread = threading.Thread(target=jm_domain_test)
    detect_thread.start()
    
    logger.info("Start detect jm domain!")
    return JsonResponse.success("Start detect jm domain, please check log get result!!!")
