import os

from PyQt5.QtGui import QPixmap
from loguru import logger

folder_path = os.path.realpath(os.path.join(os.getcwd(), f'../data'))


# 获取所有图片文件
@logger.catch
def find_images(directory):
    """
    find image from current dir data
    :param directory:
    :return:
    """
    logger.info("current use image dir:" + str(directory))
    image_files = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("dir not exists , create dir: " + str(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):
                image_files.append(os.path.join(root, file))
    return image_files


current_image_index = 0
image_files = find_images(folder_path)


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
    pixmap2 = QPixmap(os.path.join(folder_path, image_file))  # 创建新的QPixmap实例
    self.label.setPixmap(pixmap2)  # 更新QLabel的显示内容
    self.label.resize(pixmap2.width(), pixmap2.height())
