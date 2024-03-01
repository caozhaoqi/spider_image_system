import os
import sys
import time
from datetime import datetime

from log.log_record import log_record

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os.path

import cv2
import numpy as np
from loguru import logger

from image.img_switch import find_images
from run import constants
from utils.file_utils import get_data_file, find_img_result


@logger.catch
def face_detect(path, image_path):
    """
    使用OpenCV进行人脸和眼睛检测。

    :param path:
    :param image_path: 图像文件的路径。
    :return: None
    """
    file_path, file_name = os.path.split(image_path)
    folder_name = find_img_result(image_path)

    if folder_name is None:
        folder_name = 'unknown_name'
        logger.warning('folder_name is None, default use unknown_name.')

    base_path = os.path.join(path, "face_detect_result")
    base_path = os.path.join(base_path, folder_name)
    img_file_path = os.path.join(base_path, "split_face")
    img_file_path_line = os.path.join(base_path, "red_line")
    img_file_name = os.path.join(img_file_path, file_name)
    img_file_name_line = os.path.join(img_file_path_line, file_name)

    if not os.path.exists(img_file_path):
        os.makedirs(img_file_path)
        logger.warning("face detect split_face dir not exists, create it.")
    if not os.path.exists(img_file_path_line):
        os.makedirs(img_file_path_line)
        logger.warning(f"face detect red_line dir not exists, create it: {img_file_path}.")

    # 只生成没有的
    if os.path.exists(img_file_name) or os.path.exists(img_file_name_line):
        logger.warning(f"{img_file_name} already exists, will skip!")
        return False
    try:
        face_xml_path = get_data_file("xml_data/haarcascade_frontalface_default.xml")
        # eye_xml_path = get_data_file('xml_data/haarcascade_eye.xml')
        # 加载分类器
        face_cascade = cv2.CascadeClassifier(face_xml_path)
        # eye_cascade = cv2.CascadeClassifier(eye_xml_path)

        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Error: Unable to load image at {image_path}")
            return False

        # 转换为灰度图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        # eye_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) == 0:
            # logger.warning(f"No faces detected:{image_path}")
            return False
        else:
            save_face(img_file_name, img_file_name_line, img, faces)
        # 显示结果
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


@logger.catch
def save_face(img_file_name, img_file_name_line, img, faces):
    """
    
    :param img_file_name_line:
    :param img_file_name:
    :param img:
    :param faces:
    :return:
    """

    target_size = (200, 200)

    # Calculate the dimensions of the faces_image based on the number of faces and target size
    num_faces = len(faces)
    faces_image_height = num_faces * target_size[0]
    faces_image_width = target_size[1]  # Assuming we want to fit only one face horizontally for simplicity

    try:
        # Create a blank image to hold the resized faces
        faces_image = np.zeros((faces_image_height, faces_image_width, 3), dtype=np.uint8)

        # Iterate over the detected faces
        for i, (x, y, w, h) in enumerate(faces):
            # Resize the face to the target size
            face_resized = cv2.resize(img[y:y + h, x:x + w], target_size)

            row = i
            col = 0

            # Place the resized face in the faces_image array
            faces_image[row * target_size[0]:(row + 1) * target_size[0],
            col * target_size[1]:(col + 1) * target_size[1]] = face_resized

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imwrite(img_file_name, faces_image)
        cv2.imwrite(img_file_name_line, img)
    except Exception as e:
        logger.error(f"unknown error, detail: {e}, name: {img_file_name[-27:]}")
        return False
    logger.success(f"save success, name: {img_file_name[-27:]}")
    return True


@logger.catch
def face_detect_result(path):
    """

    :return:
    """
    # 调用 show_detection() 函数标示检测到的人脸
    start_time = time.time()
    img_list = find_images(path)  # 10 ms
    # 2024-03-01 14:12:04.065162
    if not img_list:
        logger.warning("cur dir data path not image!")
        return False
    for img in img_list:
        if not face_detect(path, img):
            continue

    end_time = time.time()
    logger.success(f'generate finish , data path: {path}, cost time:{int((end_time - start_time))} seconds')


constants.face_detect_flag = False

if __name__ == '__main__':
    log_record()
    face_detect_result('../run/data/')
