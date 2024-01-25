import os

import cv2
import numpy as np
from PIL import UnidentifiedImageError
from loguru import logger

from gui import constants
from gui.constants import output_video_fps, output_video_height, output_video_width
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
        result = image_fill_black(target_dir, filename)
        if not result:
            continue
    return True
    pass


@logger.catch
def image_fill_black(target_dir, image_path):
    """
    处理输入图像：如果输入尺寸大于输出尺寸则：缩小；如果输入尺寸小于输出尺寸，则用黑边填充。
    :param target_dir:输出图像路径
    :param image_path:输入图像路径
    :return:是否转换成功
    """
    # Step 1： import opencv lib
    import cv2
    try:
        # Step 2: Define the target size
        target_size = (output_video_width, output_video_height)
        # 读取图片
        img = cv2.imread(image_path)

        # 检查图片尺寸
        width, height = img.shape[:2]
        logger.debug(f"Original size: {width}x{height}")

        # 调整图片大小960x959 480 61
        # 如果图像尺寸大于目标尺寸，进行缩放
        if width < target_size[0] or height < target_size[1]:
            # 计算黑边宽度 除2
            border_width = abs(target_size[0] - width) // 2
            border_height = abs(target_size[1] - height) // 2
            # 计算少于目标宽度 目标高度值 ，
            grap_width = output_video_width - (border_width * 2) - width
            grap_height = output_video_height - (border_height * 2) - height
            border = border_width, border_height
            # logger.debug("width: " + str(border_width * 2 + width) + ", height: " + str(border_height * 2 + height))
            # 填充时自动补充至图像底边和右边 以确保输出图像等于目标尺寸 1920 1080
            img = cv2.copyMakeBorder(img, border[1], border[1] + grap_width, border[0], border[0] + grap_height, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            # out_width, out_height = img.shape[:2]
            # logger.debug("width: " + str(out_width) + ", height: " + str(out_height))
            # 如果图像尺寸大于目标尺寸，进行缩放
        elif width > target_size[0] or height > target_size[1]:
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
        # else:
        #     print("Image size matches the target size.")
        #     return img
        # Step 8: Display or save the resized image (optional)
        file_path, file_name = os.path.split(image_path)
        # 保存或显示结果
        cv2.imwrite(os.path.join(target_dir, "result_" + file_name), img)
        # cv2.imshow('Result', new_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except AttributeError as uie:
        logger.error("error, AttributeError: 'NoneType' object has no attribute 'shape'! detail: " + str(uie) +
                     ", ""file_name or path: " + str(image_path))
        return False
    except Exception as e:
        logger.error("error, unknown error! detail: " + str(e) + ", file_name or path: " + str(image_path))
        return False
    return True
    # pass


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


if __name__ == '__main__':
    ret = image_fill_black(os.getcwd(), r"C:\Users\Administrator\Pictures\a.jpg")
    logger.debug(ret)
