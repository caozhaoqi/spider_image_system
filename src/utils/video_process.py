import os

import cv2
from PIL import Image, UnidentifiedImageError
from PyQt5.QtWidgets import QMessageBox
from loguru import logger

from gui import constants
from gui.constants import output_video_fps, output_video_width, output_video_height
from utils.async_message_box import show_msg_alert
from utils.time_utils import id_generate_time


@logger.catch
def generate_video_from_images(images_input_path, video_out_path):
    """

    :param images_input_path:
    :param video_out_path:
    :return:
    """
    image_paths = []
    for root, dirs, files in os.walk(images_input_path):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):  # 仅处理jpg和png图片文件
                image_paths.append(os.path.join(root, file))

    logger.debug("scan image length: " + str(len(image_paths)) + ", scan dir: " + str(constants.data_path))
    if len(image_paths) <= 0:
        return False
    width = 0
    height = 0

    for image_path in image_paths:
        try:
            image = cv2.imread(image_path)
            if width == 0:
                width = image.shape[1]
            height = image.shape[0]
        except Exception as e:
            logger.error("error! detail: " + "file name or path: " + image_path + ", error detail: " + str(e))
            continue

        # 检查输出路径是否存在，如果不存在则创建目录
    if not os.path.exists(video_out_path):
        os.makedirs(video_out_path)

    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    # 创建VideoWriter对象
    video_name = video_out_path + id_generate_time() + "test.mp4"
    video = cv2.VideoWriter(video_name, fourcc, int(output_video_fps), (width, height))  # 设置视频帧率、输出视频大小
    if not video.isOpened():
        print("无法打开视频文件写入器")
        return False

    try:
        for image_path in os.listdir(images_input_path):
            image = cv2.imread(os.path.join(images_input_path, image_path))
            if image is None:  # 增加对图像是否正确读取的检查
                logger.error("Image not loaded:" + image_path)
                continue
            resized_image = cv2.resize(image, (width, height))  # 将图像的宽度和高度设置为适合MPEG-4的尺寸
            if image is not None:
                video.write(resized_image)
    finally:  # 确保视频资源被释放，无论是否有异常发生
        video.release()
    return video_name


@logger.catch
def convert_image(images_input_path, target_dir):
    """
    convert images to universal size
    :param images_input_path:
    :param target_dir:
    :return:
    """
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 遍历源目录中的所有文件
    image_paths = []
    for root, dirs, files in os.walk(images_input_path):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):  # 仅处理jpg和png图片文件
                image_paths.append(os.path.join(root, file))
                # 检查文件是否为图片
    logger.debug("convert_image: scan result, images count: " + str(len(image_paths)))
    for filename in image_paths:
        try:
            # 打开图片
            img = Image.open(filename)
            # 调整图片尺寸（例如，调整为800x600像素）
            new_size = (output_video_width, output_video_height)
            resized_img = img.resize(new_size, Image.LANCZOS)
            file_path, file_name = os.path.split(filename)
            # 保存处理后的图片到目标目录
            if os.path.exists(os.path.join(target_dir, "result_" + file_name)) or "result" in file_name:
                logger.info("file exists, skip file: " + str("result_" + file_name))
                continue
            resized_img.save(os.path.join(target_dir, "result_" + file_name))
        except UnidentifiedImageError as uie:
            logger.error("error, image don't support! detail: " + str(uie) + ", file_name or path: " + str(filename))
            continue
        except Exception as e:
            logger.error("error, unknown error! detail: " + str(e) + ", file_name or path: " + str(filename))
            continue
    return True
    pass


@logger.catch
def process_images_thread(self):
    """
    process image to video thread
    :param self:
    :return:
    """
    #  step 1> 处理不同尺寸照片，将其尺寸一直化
    result = convert_image(constants.data_path, constants.data_path + "/img_result")
    #  step 2> 根据处理后的图像，尝试生成视频
    if result:
        ret = generate_video_from_images(constants.data_path + "/img_result", constants.data_path + "/video/")
        if ret:
            self.load_video(ret)
            logger.success("out video success!")
    constants.process_image_flag = False
    self.success_tips()
