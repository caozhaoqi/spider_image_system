import os
import sys
import time

from image.img_switch import find_images, image_exists, error_img_update
from model.ImageModel import ImageModel
from utils.http_tools import image_url_re
from utils.time_utils import time_to_utc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from loguru import logger
from urllib3.exceptions import ProtocolError

from run import constants
from run.constants import data_path
from file.file_process import count_lines, record_end_download_image, look_end_download_image, \
    read_end_download_image, save_download_end, update_download_continue_flag
from ui_event.get_url import remove_duplicates_from_txt



@logger.catch
def download_image(url, filename, cur_txt_image_count, cur_download_images_index):
    """
    download image from point url
    :param cur_download_images_index:
    :param cur_txt_image_count:
    :param url: url location
    :param filename: file name
    :return:
    """
    now_image_list = find_images(constants.data_path)
    image_name = image_url_re(url)
    if now_image_list is None:
        # 无数据 自动置位false
        image_exists_flag = False
    else:
        image_exists_flag = image_exists(image_name, now_image_list)
    if not image_exists_flag:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Image saved as {filename}, cur images index: {cur_download_images_index}"
                             f", cur txt images download count: {cur_txt_image_count}")
            else:
                logger.error(
                    f"Error! Failed to download image from {url}, cur images index: {cur_download_images_index}, cur "
                    f"txt images download count: {cur_txt_image_count}" + "detail: " + str(response.content))
        except ConnectionError as ce:
            logger.error(f"error, connect point url error,cur images index: {cur_download_images_index}, cur txt "
                         f"images download count: {cur_txt_image_count}, detail: " + str(ce))
        except ProtocolError as pe:
            logger.error(f"error, Remote end closed connection without response, cur images index: "
                         f"{cur_download_images_index}, cur txt images download count: {cur_txt_image_count}, detail: "
                         + str(pe))
        except Exception as e:
            logger.error(f"error, unknown error,cur images index: {cur_download_images_index}, cur txt images "
                         f"download count: {cur_txt_image_count}, detail: " + str(e))


@logger.catch
def download_images_from_file(file_path, cdds_index, final_download_url, continue_download_flag,
                              txt_all_image_download_flag):
    """
    save image to point url from website download image
    :param txt_all_image_download_flag: cur txt download image flag
    :param continue_download_flag: is continue download
    :param final_download_url: final download image url
    :param cdds_index: txt index
    :param file_path: save path
    :return:
    """
    (name, suffix) = os.path.splitext(file_path)
    save_img_url = name + "/images"

    cur_download_images_index = 0
    cur_download_finish_images_index = 0
    cur_txt_image_count = count_lines(file_path)

    with open(file_path, 'r') as f:
        cur_image_list = f.readlines()
    if continue_download_flag:
        for index, cur_image in enumerate(cur_image_list):
            if cur_image.strip() == final_download_url:
                logger.warning(f"download image url: {final_download_url}, will continue!")
                cur_download_finish_images_index = index
                break
            else:
                continue
    else:
        logger.warning(f"Hasn't final download image message or already download last download txt name: {file_path}.")
        if txt_all_image_download_flag:
            # txt_all_image_download_flag
            logger.warning(f"cur txt all downloaded, start next txt name: {file_path}")
            return False

    for index, line in enumerate(cur_image_list):
        url = line.strip()
        if index >= cur_download_finish_images_index:
            # 当前下载图片下标大于等于已下载图片下标 0 > = 0 下载0
            if constants.stop_download_image_flag:
                save_download_end(index, file_path, url, cdds_index)
                break
            if url:  # 跳过空行
                if not os.path.exists(save_img_url):
                    os.makedirs(save_img_url)
                filename = os.path.join(name + "/images", f"{os.path.basename(url)}")
                cur_download_images_index += 1
                download_image(url, filename, cur_txt_image_count, index)


@logger.catch
def download_img_txt(self):
    """
    download img before process txt file
    :param self:
    :return:
    """

    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith("_img.txt")]
    cdds_index = 0
    if len(cdds) == 0:
        logger.warning("no image!")
        constants.stop_download_image_flag = True
        return False
    for cdds_path in cdds:
        # 查询上次下载记录
        download_final_flag_model, final_download_txt_name, final_download_url, final_cdds_index, \
        continue_download_flag = read_end_download_image()
        txt_all_image_download_flag = False
        if constants.stop_download_image_flag:
            break
        file_path, file_name = os.path.split(cdds_path)
        base_name, ext = os.path.splitext(file_name)
        new_file_name = file_path + "/" + base_name + "_result.txt"
        logger.success("download_img_txt: remove duplicate success, start new file name: " + new_file_name)
        remove_duplicates_from_txt(cdds_path,
                                   new_file_name)
        try:
            logger.info(
                f"start download image, txt file name {cdds_path}, index: {cdds_index}, txt count: {len(cdds)}.")
            if final_download_txt_name and continue_download_flag:
                new_file_name = final_download_txt_name
                cdds_index = final_cdds_index
                update_download_continue_flag()
                logger.warning(f"last download txt file name: {cdds[cdds_index]}! image name: {final_download_url}")
                # continue
                cur_file_name = cdds_path.split('\\')[-1].split('.')[0]
                final_file_name = final_download_txt_name.split('/')[-1]
                if cur_file_name not in final_file_name:
                    # 如果当前下载txt文件名不在最后下载文件名中，则说明当前文件已下载完成，结束继续下载，开始下载下一个文件
                    logger.warning(f"current txt already download finished, start download next txt file image, "
                                   f"txt name: {cdds_path}.")
                    continue_download_flag = False
                    txt_all_image_download_flag = True

            download_images_from_file(new_file_name, cdds_index, final_download_url, continue_download_flag,
                                      txt_all_image_download_flag)
        except Exception as e:
            logger.warning("unknown error! detail: " + str(e))
        cdds_index += 1
    logger.success("downloaded all image!")
    self.success_tips()
    return True
