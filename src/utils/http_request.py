import socket
import threading
import time
import urllib.request

import cv2
import zipfile
import os
import urllib.request
import socket
import time

from loguru import logger
from requests import HTTPError, Timeout, TooManyRedirects

from gui import constants
from gui.constants import output_video_fps, download_flag
from utils.time_utils import id_generate_time


@logger.catch
def download_and_extract(url, save_dir, extract_dir):
    try:

        file_name = url.split("/")[-1]  # 获取文件名
        save_path = os.path.join(save_dir, "gif_zip")  # 构建保存路径
        if not os.path.exists(save_path):  # 如果目录不存在则创建目录
            os.makedirs(save_path)
        download_file__thread_obj = threading.Thread(
                target=download_file_fun,
                args=(url, os.path.join(save_path, file_name), ))
        download_file__thread_obj.start()
        if constants.download_flag:
            unzip_path = extract_file(save_path, extract_dir, file_name)
            return unzip_path
        # return None
    except FileNotFoundError as fnee:  # 处理文件不存在错误
        logger.warning(f"目标文件不存在 {fnee}")
        return None
    except HTTPError as errh:  # 处理HTTP错误
        logger.error(f"HTTP错误: {errh}")
        return None
    except Timeout:  # 处理请求超时错误
        logger.error("请求超时")
        return None
    except TooManyRedirects:  # 处理过多重定向错误
        logger.error("过多重定向")
        return None
    except Exception as e:  # 处理其他未知错误
        logger.error(f"发生未知错误: {e}")
        return None


# 使用函数时，你需要提供url、save_dir和extract_dir的值。例如：
@logger.catch
def extract_file(save_path, extract_dir, file_name):
    """
    解压指定zip文件
    :param save_path:
    :param extract_dir:
    :param file_name:
    :return:
    """
    result_path = os.path.join(extract_dir, "gif_unzip")  # 构建提取路径
    folder_name, file_ext = os.path.splitext(file_name)
    unzip_path = os.path.join(result_path, folder_name)
    if not os.path.exists(unzip_path):  # 如果目录不存在则创建目录
        os.makedirs(unzip_path)
    with zipfile.ZipFile(os.path.join(save_path, file_name), 'w') as zip_ref:  # 打开zip文件进行解压
        zip_ref.extractall(unzip_path)  # 解压到指定目录
        # download_flag = False
    return unzip_path


@logger.catch
def unzip_images_url(url):
    """
    :param url:
        "https://pximg.lolicon.ac.cn/img-zip-ugoira/img/2024/01/29/02/15/41/115574488_ugoira600x600.zip"
    :return:
    """

    unzip_path = download_and_extract(url,
                                      constants.data_path, constants.data_path)
    result_path = os.path.join(constants.data_path, "gif_unzip")
    if unzip_path is None:
        logger.error("Failed to download or extract the file.")
    else:
        with open(result_path + "/unzip_image.txt", "a") as f:
            f.write(unzip_path + "\n")
        # logger.success(f"unzip success! unzip path: {unzip_path}")
        logger.success(f"File downloaded and extracted successfully to {unzip_path}.")
        # logger.info(unzip_path)
        img_list = []
        for img_path in os.listdir(unzip_path):
            if img_path.endswith(".jpg") or img_path.endswith(".png"):
                img_list.append(img_path)
        if len(img_list) > 0:
            logger.info("start generate mp4 video.")
            video_name = img_video_convert(img_list, constants.data_path)
            logger.success(f"video generate success! name {video_name}")


@logger.catch
def img_video_convert(image_path_list, video_out_path):
    """
    img to video
    :param video_out_path:
    :param image_path_list:
    :return:
    """
    width = 0
    height = 0
    for image_path in image_path_list:
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
    video_name = video_out_path + "/" + id_generate_time() + "test.mp4"
    video = cv2.VideoWriter(video_name, fourcc, int(output_video_fps), (width, height))  # 设置视频帧率、输出视频大小
    if not video.isOpened():
        print("无法打开视频文件写入器")
        return False

    try:
        export_index = 0
        # image_size = ()
        image_size_len = len(image_path_list)
        for image_path in image_path_list:
            export_index += 1
            percent_cur = int((export_index / image_size_len) * 100)
            image = cv2.imread(os.path.join(image_path_list, image_path))
            if image is None:  # 增加对图像是否正确读取的检查
                logger.error("Image not loaded:" + image_path)
                continue
            resized_image = cv2.resize(image, (width, height))  # 将图像的宽度和高度设置为适合MPEG-4的尺寸
            if image is not None:
                video.write(resized_image)
            if percent_cur / 10:
                logger.info(f"export process to export_index / image_size_len：{export_index} / {image_size_len} * "
                            f"100 /10 {percent_cur}%")
    finally:  # 确保视频资源被释放，无论是否有异常发生
        video.release()
    return video_name


@logger.catch
def download_file_fun(url, filename):
    """
    download file from url save point folder
    :param url:
    :param filename:
    :return:
    """

    # 记录开始时间
    start_time = time.time()

    if os.path.exists(filename):
        logger.warning(f"zip file already download! skip file name: {filename}")
        constants.download_flag = True
        return True
    try:
        # 建立连接并读取数据块
        with urllib.request.urlopen(url, timeout=10) as response:  # Add timeout parameter for https connections
            with open(filename, 'wb') as out_file:
                chunk_size = 1024  # Adjust chunk size as needed
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    out_file.flush()
        # 获取文件大小
        file_size = os.path.getsize(filename)
        # 记录结束时间
        end_time = time.time()
        # 计算下载时间
        download_time = end_time - start_time
        # 记录日志信息
        logger.info(f"Download of {filename} completed in {download_time:.2f} seconds, size: {file_size}")
        constants.download_flag = True
        return True
    except Exception as e:
        # 记录错误日志信息
        logger.error(f"Error downloading {filename}: {e}")
        return False


if __name__ == '__main__':
    unzip_images_url("https://pximg.lolicon.ac.cn/img-zip-ugoira/img/2024/01/29/02/15/41/115574488_ugoira600x600.zip")
    # download_file_fun("https://pximg.lolicon.ac.cn/img-zip-ugoira/img/2024/01/29/02/15/41/115574488_ugoira600x600.zip",
    #                   "./zip.zip")
