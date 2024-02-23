import os
import sys

from run import constants

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from PyQt5.QtGui import QPixmap
from loguru import logger
from PIL import Image
import os
from run.constants import data_path

folder_path = os.path.realpath(os.path.join(os.getcwd(), data_path))


@logger.catch
def find_images(directory):
    """
    find image from current dir data
    :param directory:
    :return:
    """
    image_files_lists = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("dir not exists, create dir: " + str(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "gif_unzip" not in root:
                if file.endswith('.jpg') or file.endswith('.png'):
                    image_files_lists.append(os.path.join(root, file))
    return image_files_lists


@logger.catch
def image_exists(image_path, image_list):
    """
    判断图片是否存在
    :param image_path:预下载图片名
    :param image_list:已下载图片list
    :return:
    """
    for image_detail in image_list:
        if image_path in image_detail:
            return True
    return False


@logger.catch
def show_filter_image(images_list):
    """
    过滤过小图片不显示到首页
    :param images_list:
    :return:
    """
    filter_result_images = []
    for filter_image in images_list:
        filter_path, filter_name = os.path.split(filter_image)
        if "square" in filter_name or "custom" in filter_name or "square" in filter_path or "custom" in filter_path \
                or "error_images" in filter_path or "small_images" in filter_path:
            continue
        else:
            filter_result_images.append(filter_image)
    return filter_result_images


current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


@logger.catch
def show_next_image(self):
    """
    show next image to ui
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
    shou first image to ui
    :param self:
    :param image_file:
    :return:
    """
    self.file_name_label.setText(os.path.join(folder_path, image_file))
    self.pixmap_image_tab1 = QPixmap(os.path.join(folder_path, image_file))  # 创建新的QPixmap实例
    self.label.setPixmap(self.pixmap_image_tab1)  # 更新QLabel的显示内容
    self.label.resize(self.pixmap_image_tab1.width(), self.pixmap_image_tab1.height())
    logger.info("current show image name and path: " + str(os.path.join(folder_path, image_file)))


@logger.catch
def show_current_file_name(image_file):
    """
    show current file name
    :param image_file:
    :return:
    """
    _, file_name = os.path.split(image_file)
    return file_name


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
    for filename in image_lists:
        if filename.endswith(".jpg") or filename.endswith(".png"):  # 只处理jpg和png格式的图片
            filepath = os.path.join(image_path, filename)
            if "error_images" in filepath or "small_images" in filepath:
                continue
            else:
                try:
                    image = Image.open(filepath)
                    width, height = image.size
                    if width <= 250 and height <= 250:  # 图片尺寸小于250*250
                        logger.warning(f"图片 {filename} 尺寸过小, 已移动至small_images文件夹。")
                        small_image_lists.append(filepath)
                except Exception as e:
                    logger.error(f"无法打开图片 {filename}, 错误信息:{e}, 已移动至error_images文件夹。")
                    error_image_lists.append(filepath)
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
        f.close()
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
        f.close()
    self.success_tips()
    logger.info("scan end, error and small image write file, images move error_images and small_images folder, "
                "please read txt or folder lookup.")


@logger.catch
def img_category_images(self, image_path):
    """
    分类现有图片
    :param self:
    :param image_path:
    :return:
    """
    image_lists = find_images(image_path)
    custom_image_lists = []
    square_image_lists = []
    master_image_lists = []
    # 遍历目录中的所有图片文件 分类存储至集合
    for filename in image_lists:
        if filename.endswith(".jpg") or filename.endswith(".png"):  # 只处理jpg和png格式的图片
            filepath = os.path.join(image_path, filename)
            img_path, _ = os.path.split(filepath)
            if "square" in img_path or "custom" in img_path or "master" in img_path:
                continue
            elif "square" in filename:
                square_image_lists.append(filename)
            elif "master" in filename:
                master_image_lists.append(filename)
            elif "custom" in filename:
                custom_image_lists.append(filename)
            else:
                logger.warning("未知种类图片，待定: " + str(filename))
    for square_image in square_image_lists:
        dir_path, file_name = os.path.split(square_image)
        if not os.path.exists(dir_path + "/square/"):
            os.makedirs(dir_path + "/square/")
        with open(dir_path + '/square_image_txt.txt', 'a') as f:
            f.write(square_image + "\n")
        shutil.move(square_image, dir_path + "/square/" + file_name)
        f.close()
    for custom_image in custom_image_lists:
        dir_path, file_name = os.path.split(custom_image)
        if not os.path.exists(dir_path + "/custom/"):
            os.makedirs(dir_path + "/custom/")
        with open(dir_path + '/custom_image_txt.txt', 'a') as f:
            f.write(custom_image + "\n")
        shutil.move(custom_image, dir_path + "/custom/" + file_name)
        f.close()
    for master_image in master_image_lists:
        dir_path, file_name = os.path.split(master_image)
        if not os.path.exists(dir_path + "/master/"):
            os.makedirs(dir_path + "/master/")
        with open(dir_path + '/master_image_txt.txt', 'a') as f:
            f.write(master_image + "\n")
        shutil.move(master_image, dir_path + "/master/" + file_name)
        f.close()
    logger.success("img category success!")
    self.success_tips()


@logger.catch
def error_img_update(url):
    """
    error_img_txt update
    :param url:
    :return:
    """
    exists_error_url_flag = False
    error_img_txt_path = constants.data_path + "\\download_fail_image.txt"
    if os.path.exists(error_img_txt_path):
        with open(error_img_txt_path, "r") as f:
            error_img_list = f.readlines()
        for error_img in error_img_list:
            if error_img is url:
                error_img_list.remove(error_img)
                exists_error_url_flag = True
        if exists_error_url_flag:
            for error_img_new in error_img_list:
                # 打开文件并写入元素
                with open(error_img_txt_path, 'w') as file:
                    file.write(str(error_img_new + "\n"))
            return True
    return False
