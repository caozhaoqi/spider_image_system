import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image.fail_image import process_error_image
from image.img_switch import find_images, image_exists, img_category_images, check_images
from utils.file_download import send_request
from utils.file_utils import remove_duplicates_from_txt
from utils.http_utils import image_url_re
from utils.minio_file import upload_image
import threading
from loguru import logger
from urllib3.exceptions import ProtocolError
from run import constants
from run.constants import data_path
from file.file_process import count_lines, read_end_download_image, save_download_end, update_download_continue_flag, \
    record_download_finish_txt, exists_txt_from_finish, write_error_image


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
            response = send_request(url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Image s aved as {filename}, cur images index: {cur_download_images_index}"
                             f", cur txt images download count: {cur_txt_image_count}")
            else:
                write_error_image(constants.data_path, url, filename)
                logger.error(
                    f"Error! Failed to download image from {url}, cur images index: {cur_download_images_index}, cur "
                    f"txt images download count: {cur_txt_image_count}, " + "detail: " + str(response.content))
        except ConnectionError as ce:
            write_error_image(constants.data_path, url, filename)
            logger.error(f"error, connect point url error, cur images index: {cur_download_images_index}, cur txt "
                         f"images download count: {cur_txt_image_count}, detail: " + str(ce))
        except ProtocolError as pe:
            write_error_image(constants.data_path, url, filename)
            logger.error(f"error, Remote end closed connection without response, cur images index: "
                         f"{cur_download_images_index}, cur txt images download count: {cur_txt_image_count}, detail: "
                         + str(pe))
        except Exception as e:
            write_error_image(constants.data_path, url, filename)
            logger.error(f"error, unknown error, cur images index: {cur_download_images_index}, cur txt images "
                         f"download count: {cur_txt_image_count}, detail: " + str(e))


@logger.catch
def download_images_from_file(file_path, cdds_index, final_download_url, continue_download_flag):
    """
    save image to point url from website download image
    :param continue_download_flag: is continued download
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

    with open(file_path, 'r', encoding='utf-8') as f:
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
                filename = os.path.join(os.path.join(name, "images"), f"{os.path.basename(url)}")
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
        logger.warning("current dir no image!")
        constants.stop_download_image_flag = True
        return False
    for cdds_path in cdds:
        download_final_flag_model, final_download_txt_name, final_download_url, final_cdds_index, continue_download_flag = read_end_download_image()
        if constants.stop_download_image_flag:
            break
        try:
            if not exists_txt_from_finish(cdds_path):
                logger.info(
                    f"start download image, txt file name {cdds_path}, index: {cdds_index}, txt count: {len(cdds)}.")
                if final_download_txt_name and continue_download_flag:
                    update_download_continue_flag()
                    logger.warning(f"last download txt file name: {cdds_path}! image name: {final_download_url}")

                new_file_name = remove_repeat_content(cdds_path)
                download_images_from_file(new_file_name, cdds_index, final_download_url, continue_download_flag)
        except Exception as e:
            logger.warning("unknown error! detail: " + str(e))
        cdds_index += 1
        process_image(self, cdds_path)
        if not constants.stop_download_image_flag:
            # 非当前停止txt记录
            #     记录已下载完成txt
            record_download_finish_txt(cdds_path)
        if constants.upload_minio_image_Flag == 'True' and not constants.category_image_flag and not constants.check_images_flag:
            logger.debug("will start upload image and log!")
            upload_image(constants.basic_path)
        else:
            logger.warning(f"not start upload image, {constants.upload_minio_image_Flag},"
                           f" not {constants.category_image_flag}, not {constants.check_images_flag}")
    logger.success("downloaded all image!")
    if self:
        self.success_tips()
    else:
        logger.success("downloaded image operate success finished!")
    constants.stop_download_image_flag = True
    return True


@logger.catch
def skip_txt_index(cdds_path, final_download_txt_name):
    """
     un use
    :param cdds_path:
    :param final_download_txt_name:
    :return:
    """
    # continue
    cur_file_name = cdds_path.split('\\')[-1].split('.')[0]
    final_file_name = final_download_txt_name.split('/')[-1]
    if cur_file_name not in final_file_name:
        # 如果当前下载txt文件名不在最后下载文件名中，则说明当前文件已下载完成，结束继续下载，开始下载下一个文件
        logger.warning(f"current txt already download finished, start download next txt file image, "
                       f"txt name: {cdds_path}.")
        continue_download_flag = False
        txt_all_image_download_flag = True
        return continue_download_flag, txt_all_image_download_flag
    return None, None


@logger.catch
def remove_repeat_content(cdds_path):
    """

    :param cdds_path:
    :return:
    """
    file_path, file_name = os.path.split(cdds_path)
    base_name, ext = os.path.splitext(file_name)
    new_file_name = file_path + "/" + base_name + "_result.txt"
    logger.success("download_img_txt: remove duplicate success, start new file name: " + new_file_name)
    remove_duplicates_from_txt(cdds_path,
                               new_file_name)
    return new_file_name


@logger.catch
def process_image(self, cdds_path):
    """

    :param cdds_path:
    :param self:
    :return:
    """
    #  处理错误图片 分类图片
    logger.debug("start remove error image!")
    # constants.before_image_process_flag = True
    constants.check_images_flag = True
    remove_error_image(self)
    logger.debug("start category image!")
    constants.category_image_flag = True
    img_category_button(self)
    logger.success(f"image basic process finished. cdds name: {cdds_path}")


@logger.catch
def download_re_error_image():
    """

    :return:
    """
    try:
        # error_image_list = []
        path = os.path.join(constants.data_path, "download_fail_image.txt")
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            error_image_list = f.readlines()
        if not error_image_list:
            logger.warning("download image fail txt no content!")
            return False
        # 处理list 摒弃原始url，换回或者，换新domain
        error_image_list = process_error_image(error_image_list)
        logger.success("replace domain success, will retry download!")
        for index, error_image in enumerate(error_image_list):
            split_result = error_image.strip().split(',')
            error_image_name = image_url_re(split_result[0])
            keyword = split_result[1]
            if keyword == '':
                keyword = 'unknown_keyword'
            # r'img_url\/(.*?)_img_result'     pattern = r'.*?\\([^_]+)_img_result'
            new_file_path = os.path.join(os.path.join(constants.data_path, "img_url"), "re_download")
            new_file_path = os.path.join(new_file_path, "img_url")
            new_file_path = os.path.join(new_file_path, keyword+"_img_result")
            new_file_path = os.path.join(new_file_path, "images")
            if not os.path.exists(new_file_path):
                logger.warning("dir not exists, will create!")
                os.makedirs(new_file_path)
            new_file_name = os.path.join(new_file_path, error_image_name)
            download_image(split_result[0].strip(), new_file_name, len(error_image_list), index)
        constants.download_image_re_flag = False
    except Exception as e:
        logger.warning(f"unknown error, detail: {e}")
    logger.success("download all image for re!")


@logger.catch
def remove_error_image(self):
    """
        下载指定txt中url对应images

    :param self:
    :return:
    """
    logger.info("start scan images... ")
    scan_image_thread_obj = threading.Thread(
        target=check_images,
        args=(self, constants.data_path))
    scan_image_thread_obj.start()


@logger.catch
def img_category_button(self):
    """
    图片分类
    :return:
    """
    logger.info('start img category...')
    img_category_thread_obj = threading.Thread(
        target=img_category_images,
        args=(self, constants.data_path))
    img_category_thread_obj.start()
