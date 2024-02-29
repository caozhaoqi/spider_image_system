import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os.path

import cv2
import numpy as np
from loguru import logger

from image.img_switch import find_images
from run import constants
from utils.file_utils import get_data_file


@logger.catch
def face_detect(path, image_path):
    """
    使用OpenCV进行人脸和眼睛检测。

    :param path:
    :param image_path: 图像文件的路径。
    :return: None
    """
    try:
        face_xml_path = get_data_file("xml_data/haarcascade_frontalface_default.xml")
        eye_xml_path = get_data_file('xml_data/haarcascade_eye.xml')
        # 加载分类器
        face_cascade = cv2.CascadeClassifier(face_xml_path)
        eye_cascade = cv2.CascadeClassifier(eye_xml_path)

        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Error: Unable to load image at {image_path}")
            return

        # 转换为灰度图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # 在人脸区域内检测眼睛
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            # 将绘制了眼睛矩形框的人脸区域放回原图的正确位置
            img[y:y + h, x:x + w] = roi_color
        if len(faces) == 0:
            # logger.warning(f"No faces detected:{image_path}")
            return
        else:
            save_face(path, image_path, img, faces, gray)
        # 显示结果
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        logger.error(f"An error occurred: {e}")


@logger.catch
def save_face(path, img_path, img, faces, gray):
    """
    
    :param path:
    :param img:
    :param gray:
    :param faces:
    :param img_path:
    :return: 
    """
    file_path, file_name = os.path.split(img_path)
    subdir, _ = os.path.split(os.path.dirname(img_path))
    subdir_1, folder_name = os.path.split(subdir)
    base_path = os.path.join(path, "face_detect_result")
    base_path = os.path.join(base_path, folder_name)
    img_file_path = os.path.join(base_path, "split_face")
    img_file_path_line = os.path.join(base_path, "red_line")
    if not os.path.exists(img_file_path):
        os.makedirs(img_file_path)
        logger.warning("face detect split_face dir not exists, create it.")
    if not os.path.exists(img_file_path_line):
        os.makedirs(img_file_path_line)
        logger.warning("face detect red_line dir not exists, create it.")
    img_file_name = os.path.join(img_file_path, file_name)
    img_file_name_line = os.path.join(img_file_path_line, file_name)
    # 只生成没有的
    if os.path.exists(img_file_name) or os.path.exists(img_file_name_line):
        logger.warning(f"img {img_file_name} already exists, will skip!")
        return True
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
    img_list = find_images(path)
    if img_list:
        for img in img_list:
            face_detect(path, img)
        logger.success(f"generate finish, data path: {path}")
    else:
        logger.warning("cur dir data path not image!")
    constants.face_detect_flag = False


if __name__ == '__main__':
    face_detect_result()
