import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from loguru import logger

from gui import constants
from gui.constants import data_path

folder_path = os.path.realpath(os.path.join(os.getcwd(), data_path))


# 获取所有图片文件
@logger.catch
def find_images(directory):
    """
    find image from current dir data
    :param directory:
    :return:
    """
    logger.info("current use image dir:" + str(directory))
    image_files_lists = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("dir not exists , create dir: " + str(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):
                image_files_lists.append(os.path.join(root, file))
    return image_files_lists


current_image_index = 0
image_files = find_images(folder_path)
# file_name = ''


@logger.catch
def show_next_image(self):
    """

    :param self:
    :return:
    """
    try:
        global current_image_index, image_files
        current_image_index = (current_image_index + 1) % len(image_files)
        show_image(self, image_files[current_image_index])
        self.show_page_label.setText(str(current_image_index) + "/" + str(len(image_files)))

    except Exception as e:
        logger.warning("dir not image, or other err! detail: " + str(e))


@logger.catch
def show_image(self, image_file):
    """

    :param self:
    :param image_file:
    :return:
    """
    # 打开图片文件
    self.file_name_label.setText(show_current_file_name(image_file))
    # _, file_name = os.path.split(image_file)
    pixmap2 = QPixmap(os.path.join(folder_path, image_file))  # 创建新的QPixmap实例
    # logger.debug(file_name+","+constants.file_name_txt)
    self.label.setPixmap(pixmap2)  # 更新QLabel的显示内容
    self.label.resize(pixmap2.width(), pixmap2.height())
    logger.info("current show image name and path: " + str(os.path.join(folder_path, image_file)))


@logger.catch
def show_current_file_name(image_file):
    # global file_name
    _, file_name = os.path.split(image_file)
    return file_name
