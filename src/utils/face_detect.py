"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import cv2
import numpy as np
from loguru import logger
from image.img_switch import find_images
from run import constants
from utils.file_utils import get_data_file, find_img_result
import time


@logger.catch
def face_detect(base_path: str, image_path: str) -> bool:
    """
    使用OpenCV进行人脸和眼睛检测

    Args:
        base_path: 基础路径
        image_path: 图像文件路径
        
    Returns:
        bool: 检测是否成功
    """
    # 获取文件夹名称
    folder_name = find_img_result(image_path) or 'unknown_name'
    
    # 构建输出路径
    output_base = Path(base_path) / "face_detect_result" / folder_name
    face_output_dir = output_base / "split_face" 
    line_output_dir = output_base / "red_line"
    
    face_output_path = face_output_dir / Path(image_path).name
    line_output_path = line_output_dir / Path(image_path).name

    # 创建输出目录
    face_output_dir.mkdir(parents=True, exist_ok=True)
    line_output_dir.mkdir(parents=True, exist_ok=True)

    # 检查文件是否已存在
    if face_output_path.exists() or line_output_path.exists():
        logger.warning(f"File {face_output_path} already exists, skipping")
        return False

    try:
        # 加载分类器
        face_cascade = cv2.CascadeClassifier(get_data_file("xml_data/haarcascade_frontalface_default.xml"))
        eye_cascade = cv2.CascadeClassifier(get_data_file('xml_data/haarcascade_eye.xml'))

        # 读取并处理图像
        img = cv2.imread(str(image_path))
        if img is None:
            logger.error(f"Unable to load image: {image_path}")
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if not faces.any():
            return False

        return save_face(str(face_output_path), str(line_output_path), img, faces, gray, eye_cascade)

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return False


@logger.catch
def save_face(face_output: str, line_output: str, img: np.ndarray, faces: np.ndarray, 
             gray: np.ndarray, eye_cascade: cv2.CascadeClassifier) -> bool:
    """
    保存检测到的人脸图像
    
    Args:
        face_output: 人脸输出路径
        line_output: 带标记输出路径
        img: 原始图像
        faces: 检测到的人脸
        gray: 灰度图像
        eye_cascade: 眼睛检测分类器
        
    Returns:
        bool: 保存是否成功
    """
    target_size = (200, 200)
    faces_image = np.zeros((len(faces) * target_size[0], target_size[1], 3), dtype=np.uint8)

    try:
        # 处理每个检测到的人脸
        for i, (x, y, w, h) in enumerate(faces):
            # 绘制人脸框
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # 检测眼睛
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]
            
            for ex, ey, ew, eh in eye_cascade.detectMultiScale(roi_gray):
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            
            img[y:y + h, x:x + w] = roi_color

            # 调整人脸大小并保存
            face_resized = cv2.resize(img[y:y + h, x:x + w], target_size)
            faces_image[i * target_size[0]:(i + 1) * target_size[0], 0:target_size[1]] = face_resized

        # 保存图像
        cv2.imwrite(face_output, faces_image)
        cv2.imwrite(line_output, img)
        
        logger.success(f"Successfully saved: {Path(face_output).name}")
        return True

    except Exception as e:
        logger.error(f"Error saving face: {e}, file: {Path(face_output).name}")
        return False


@logger.catch
def face_detect_result(path: str) -> bool:
    """
    处理目录下所有图像的人脸检测
    
    Args:
        path: 图像目录路径
        
    Returns:
        bool: 处理是否成功
    """
    start_time = time.time()
    
    img_list = find_images(path)
    if not img_list:
        logger.warning("No images found in directory")
        return False

    for img in img_list:
        face_detect(path, img)

    logger.success(f'Processing complete. Path: {path}, Time: {int(time.time() - start_time)}s')
    constants.face_detect_flag = False
