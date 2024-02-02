import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from loguru import logger
from urllib3.exceptions import ProtocolError

from run import constants
from run.constants import data_path
from file.file_process import count_lines
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
    if not os.path.exists(filename):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Image saved as {filename}, cur images index: {cur_download_images_index}"
                             f", cur txt images download count: {cur_txt_image_count}")
            else:
                logger.error(f"Error! Failed to download image from {url}" + "detail reason: " + str(response.content))
        except ConnectionError as ce:
            logger.error("error, connect point url error, detail: " + str(ce))
        except ProtocolError as pe:
            logger.error("error, Remote end closed connection without response, detail: " + str(pe))
        except Exception as e:
            logger.error("error, unknown error, detail: " + str(e))
    else:
        logger.warning("file exists will skip file, file name: " + str(filename))


@logger.catch
def download_images_from_file(file_path):
    """
    save image to point url from website download image
    :param file_path: save path
    :return:
    """
    (name, suffix) = os.path.splitext(file_path)
    save_img_url = name + "/images"
    cur_download_images_index = 0
    cur_txt_image_count = count_lines(file_path)
    with open(file_path, 'r') as f:
        for line in f:
            url = line.strip()
            if url:  # 跳过空行
                if not os.path.exists(save_img_url):
                    os.makedirs(save_img_url)
                filename = os.path.join(name + "/images", f"{os.path.basename(url)}")
                cur_download_images_index += 1
                download_image(url, filename, cur_txt_image_count, cur_download_images_index + 1)


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
        logger.warning("no image !")
        constants.stop_download_image_flag = True
        return False
    for cdds_path in cdds:
        if constants.stop_download_image_flag:
            break
        cdds_index += 1
        logger.debug("download img before , remove duplicate.")
        file_path, file_name = os.path.split(cdds_path)
        base_name, ext = os.path.splitext(file_name)
        new_file_name = file_path + "/" + base_name + "_result.txt"
        logger.success("download_img_txt: remove duplicate success, start new file name :" + new_file_name)
        remove_duplicates_from_txt(cdds_path,
                                   new_file_name)
        try:
            logger.info(f"start download image, txt file name {cdds_path}, index: {cdds_index}")
            download_images_from_file(new_file_name)
        except Exception as e:
            logger.warning("unknown error! detail: " + str(e))
    constants.stop_download_image_flag = False
    # QMessageBox.information(self, u"完成", u"操作完成")
    logger.success("downloaded all image !")
    self.success_tips()
    # show_msg_alert("完成", "完成！")
    return True
