import os
import shutil

from PyQt5.QtGui import QPixmap
from loguru import logger

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


from PIL import Image
import os


@logger.catch
def check_images(self, image_path):
    """
    检查现有图片是否正常
    :param self:
    :param image_path: 数据路径
    :return:
    """
    image_lists = find_images(image_path)
    small_image_lists = []
    error_image_lists = []
    # 遍历目录中的所有图片文件
    for filename in image_lists:
        if filename.endswith(".jpg") or filename.endswith(".png"):  # 只处理jpg和png格式的图片
            filepath = os.path.join(image_path, filename)
            if "error_images" in filepath or "small_images" in filepath:
                continue
            else:
                try:
                    # 打开图片并检查尺寸
                    image = Image.open(filepath)
                    width, height = image.size
                    if width <= 250 and height <= 250:  # 图片尺寸小于250*250
                        logger.warning(f"图片 {filename} 尺寸过小，已删除。")
                        # os.remove(filepath)  # 删除过小的图片
                        small_image_lists.append(filepath)
                    else:
                        logger.info(f"图片 {filename} 尺寸正常。")
                except Exception as e:
                    logger.error(f"无法打开图片 {filename}，错误信息：{e}, 已删除。")
                    # os.remove(filepath)  # 删除过小的图片
                    error_image_lists.append(filepath)
                # continue
    # record list to txt
    for error_images in error_image_lists:
        with open(image_path + '/error_image_txt.txt', 'a') as f:
            if not os.path.exists(image_path + "/error_images/"):
                os.makedirs(image_path + "/error_images/")
            file_path, file_name = os.path.split(error_images)
            if 'error_images' in file_path:
                continue
            else:
                f.write(error_images + "\n")
                shutil.move(error_images, image_path + "/error_images/" + file_name)
    for small_image in small_image_lists:
        with open(image_path + '/small_image_txt.txt', 'a') as f:
            if not os.path.exists(image_path + "/small_images/"):
                os.makedirs(image_path + "/small_images/")
            file_path, file_name = os.path.split(small_image)
            if 'small_images' in file_path:
                continue
            else:
                f.write(small_image + "\n")
                shutil.move(small_image, image_path + "/small_images/" + file_name)
    self.success_tips()
    logger.info("scan end, error and small image write file, images move error_images and small_images folder, "
                "please read txt or folder lookup.")


if __name__ == '__main__':
    check_images(r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data\img_url\ruanmei_img_result'
                 r'\images')
