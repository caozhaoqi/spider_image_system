import os
import requests
from PyQt5.QtWidgets import QMessageBox

from loguru import logger
from urllib3.exceptions import ProtocolError

from gui import constants
from gui.constants import data_path
from utils.async_message_box import show_msg_alert
from utils.get_url import remove_duplicates_from_txt


@logger.catch
def download_image(url, filename):
    """
    download image from point url
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
                logger.debug(f"Image downloaded and saved as {filename}")
            else:
                logger.error(f"Error! Failed to download image from {url}" + "detail reason: " + str(response.content))
        except ConnectionError as ce:
            logger.error("error, connect point url error, detail: " + str(ce))
        except ProtocolError as pe:
            logger.error("error, Remote end closed connection without response, detail: " + str(pe))
        except Exception as e:
            logger.error("error, unknown error, detail: " + str(e))
    else:
        logger.error("file exists will skip file, file name: " + str(filename))


@logger.catch
def download_images_from_file(file_path):
    """
    save image to point url from website download image
    :param file_path: save path
    :return:
    """
    (name, suffix) = os.path.splitext(file_path)
    save_img_url = name + "/images"
    with open(file_path, 'r') as f:
        for line in f:
            url = line.strip()
            if url:  # 跳过空行
                if not os.path.exists(save_img_url):
                    os.makedirs(save_img_url)
                filename = os.path.join(name + "/images", f"{os.path.basename(url)}")
                download_image(url, filename)


@logger.catch
def download_img_txt(self):
    """
    download img before process txt file
    :param self:
    :return:
    """
    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith("_img.txt")]
    for cdds_path in cdds:
        logger.debug("download img before , remove duplicate.")
        file_path, file_name = os.path.split(cdds_path)
        base_name, ext = os.path.splitext(file_name)
        new_file_name = file_path + "/" + base_name + "_result.txt"
        remove_duplicates_from_txt(cdds_path,
                                   new_file_name)
        logger.success("download_img_txt: remove duplicate success, start new file name :" + new_file_name)
        try:
            download_images_from_file(new_file_name)
        except Exception as e:
            logger.warning("unknown error! detail: " + str(e))
    constants.download_image_flag = False
    # QMessageBox.information(self, u"完成", u"操作完成")
    logger.success("downloaded all image !")
    self.success_tips()
    # show_msg_alert("完成", "完成！")
    return True
