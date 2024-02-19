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
from file.file_process import count_lines, write_error_image, record_end_download_image, look_end_download_image
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
    image_name = image_url_re(url)
    now_image_list = find_images(constants.data_path)
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
                # 下载完成查询error_image中是否包含，如果包含，则删除
                if error_img_update(url):
                    logger.warning(f"last download fail image: {url}, success download, error_txt update!")
            else:
                write_error_image(constants.data_path + "\\download_fail_image.txt", url)
                logger.error(
                    f"Error! Failed to download image from {url}, " + "detail reason: " + str(response.content))
        except ConnectionError as ce:
            write_error_image(constants.data_path + "\\download_fail_image.txt", url)
            logger.error("error, connect point url error, detail: " + str(ce))
        except ProtocolError as pe:
            write_error_image(constants.data_path + "\\download_fail_image.txt", url)
            logger.error("error, Remote end closed connection without response, detail: " + str(pe))
        except Exception as e:
            write_error_image(constants.data_path + "\\download_fail_image.txt", url)
            logger.error("error, unknown error, detail: " + str(e))
    # else:
    #     logger.warning("file exists will skip file, file name: " + str(filename))


@logger.catch
def download_images_from_file(file_path, cdds_index, final_download_url, continue_download_flag):
    """
    save image to point url from website download image
    :param continue_download_flag:
    :param final_download_url:
    :param cdds_index:
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
            if cur_image == final_download_url:
                logger.warning(f"download image url: {final_download_url}, will continue!")
                cur_download_finish_images_index = index
                break
    else:
        logger.warning("no final download image message or already download last download image!")

    for index, line in enumerate(cur_image_list):
        url = line.strip()
        if index >= cur_download_finish_images_index:
            # 当前下载图片下标大于等于已下载图片下标 0 > = 0 下载0
            if constants.stop_download_image_flag:
                data = ImageModel(cur_download_images_index, file_path, url, image_url_re(url),
                                  time_to_utc(time.time()), cdds_index, True)
                record_end_download_image(constants.data_path + "\\download_final_image.json", data)
                logger.warning(
                    f"set stop image stop_download_image_flag True! save result: {data.image_url}, txt name: {file_path}.")
                break
            if url:  # 跳过空行
                if not os.path.exists(save_img_url):
                    os.makedirs(save_img_url)
                filename = os.path.join(name + "/images", f"{os.path.basename(url)}")
                cur_download_images_index += 1
                download_image(url, filename, cur_txt_image_count, cur_download_images_index)


@logger.catch
def download_img_txt(self):
    """
    download img before process txt file
    :param self:
    :return:
    """
    # 查询上次下载记录
    final_download_txt_name = None
    # final_download_image_name = None
    final_download_url = None
    # final_download_image_index = None
    final_cdds_index = None
    continue_download_flag = False
    download_final_flag = look_end_download_image(constants.data_path + "\\download_final_image.json")
    if download_final_flag:
        download_final_flag_model = ImageModel(download_final_flag['image_index'], download_final_flag['txt_name'],
                                               download_final_flag['image_url'], download_final_flag['image_name'],
                                               download_final_flag['download_date'], download_final_flag['txt_index'],
                                               download_final_flag['continue_flag'])
        final_download_txt_name = download_final_flag_model.txt_name
        final_download_url = download_final_flag_model.image_url
        final_cdds_index = download_final_flag_model.txt_index
        continue_download_flag = download_final_flag_model.continue_flag

    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith("_img.txt")]
    cdds_index = 0
    if len(cdds) == 0:
        logger.warning("no image!")
        constants.stop_download_image_flag = True
        return False
    for cdds_path in cdds:
        if constants.stop_download_image_flag:
            constants.stop_download_image_flag = True
            break
        # logger.debug("download img before, remove duplicate.")
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
            download_images_from_file(new_file_name, cdds_index, final_download_url, continue_download_flag)
        except Exception as e:
            logger.warning("unknown error! detail: " + str(e))
        cdds_index += 1
    logger.success("downloaded all image!")
    self.success_tips()
    return True


@logger.catch
def update_download_continue_flag():
    data = ImageModel(None, None, None, None,
                      time_to_utc(time.time()), None, False)
    record_end_download_image(constants.data_path + "\\download_final_image.json", data)
    logger.info("download final image json continue_flag update success!")
