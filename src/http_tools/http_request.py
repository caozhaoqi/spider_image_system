import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.file_process import scan_directory_zip
from utils.file_utils import remove_duplicates_from_txt
import threading
import urllib.request
import cv2
import zipfile
import os
import urllib.request
import time
from loguru import logger
from requests import HTTPError, Timeout, TooManyRedirects
from run import constants
from run.constants import output_video_fps


@logger.catch
def download_all_zip(url, save_dir):
    """
    下载指定url zip 文件
    :param url: 下载地址
    :param save_dir: 保存路径
    :return:
    """
    try:
        file_name = url.split("/")[-1]  # 获取文件名
        save_path = os.path.join(save_dir, "gif_zip")  # 构建保存路径
        if not os.path.exists(save_path):  # 如果目录不存在则创建目录
            os.makedirs(save_path)
        download_file_gif_thread_obj = threading.Thread(
            target=download_file_fun,
            args=(url, os.path.join(save_path, file_name),))
        download_file_gif_thread_obj.start()
        if constants.download_finish_flag:
            return True
        return False
    except FileNotFoundError as fnee:  # 处理文件不存在错误
        logger.warning(f"target file not exists: {fnee}")
        return False
    except HTTPError as errh:  # 处理HTTP错误
        logger.error(f"http error: {errh}")
        return False
    except Timeout:  # 处理请求超时错误
        logger.error("connection time out.")
        return False
    except TooManyRedirects:  # 处理过多重定向错误
        logger.error("max redirects.")
        return False
    except Exception as e:  # 处理其他未知错误
        logger.error(f"unknown error, detail: {e}")
        return False


@logger.catch
def extract_file(save_path, file_name):
    """
    解压指定zip文件并检查解压出的文件大小是否符合预期
    :param save_path: 保存路径
    :param file_name: 文件名
    :return: 提取路径或None（如果未找到符合预期的文件）
    """
    result_path = os.path.join(save_path, "gif_unzip")  # 构建提取路径
    _, result_name = os.path.split(file_name)
    result_name, ext = os.path.splitext(result_name)
    result_path = os.path.join(result_path, result_name)
    if not os.path.exists(result_path):  # 如果目录不存在则创建目录
        os.makedirs(result_path)

    zip_size = os.path.getsize(file_name)
    expected_size = zip_size

    if zip_size == expected_size:
        logger.debug(f"Zip file size is {zip_size} bytes, which matches the expected size of {expected_size} bytes.")
        try:
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(result_path)  # 解压到指定目录
                logger.debug(f"Files extracted to {result_path}")
                return result_path
        except Exception as e:
            logger.warning(f"unknown error! detail: {e}")
            return None
    else:
        logger.debug(
            f"Zip file size is {zip_size} bytes, which does not match the expected size of {expected_size} bytes.")
        return None


@logger.catch
def generate_gif_video(zip_file_list):
    """
    解压压缩包并生成video
    :param zip_file_list:
    :return:
    """
    result_path_list = []
    for zip_file_name_detail in zip_file_list:
        folder_path, folder_name = os.path.split(zip_file_name_detail)
        folder_path = folder_path.replace("gif_zip", "")
        unzip_path = extract_file(folder_path, zip_file_name_detail)
        if unzip_path is None:
            logger.error(f"Failed to extract the file: {unzip_path}")
        else:
            result_path_list.append(unzip_path)
            logger.success(f"File extracted successfully to {unzip_path}.")
    logger.info("start scan zip unzip img file.")
    output_video_path = os.path.join(constants.data_path, zip_file_list[0].replace("zip", "video"))
    if not os.path.exists(output_video_path):
        logger.warning("output video exists not, creating.")
        os.makedirs(output_video_path)
    for result_path_list_detail in result_path_list:
        img_list = []
        files_and_dirs = os.listdir(result_path_list_detail)
        # 遍历文件和子目录
        for img_path in files_and_dirs:
            # 获取文件的完整路径
            full_path = os.path.join(result_path_list_detail, img_path)
            # print(full_path)
            if img_path.endswith(".jpg") or img_path.endswith(".png"):
                img_list.append(full_path)
        if len(img_list) > 0:
            point_path, point_gif_name = os.path.split(result_path_list_detail)
            point_gif_video_name, ext = os.path.splitext(point_gif_name)
            logger.info(f"start generate mp4 video. folder name: {point_gif_video_name}")
            video_name = img_video_convert(img_list, output_video_path, point_gif_video_name)
            logger.success(f"video generate success! flag {video_name}")
    constants.unzip_generate_video_flag = False
    logger.success(f"generate gif video success! file length: {len(result_path_list)}")
    return True


@logger.catch
def img_video_convert(image_path_list, video_out_path, point_gif_video_name):
    """
    img to video
    :param point_gif_video_name:
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

    if not os.path.exists(video_out_path):
        os.makedirs(video_out_path)

    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    video_name = video_out_path + "/" + point_gif_video_name + "_test.mp4"
    if os.path.exists(video_name):
        logger.warning(f"video exists! name and path: {video_name}")
        return False
    video = cv2.VideoWriter(video_name, fourcc, int(output_video_fps), (width, height))  # 设置视频帧率、输出视频大小
    if not video.isOpened():
        logger.debug("无法打开视频文件写入器")
        return False

    try:
        export_index = 0
        # image_size_len = len(image_path_list)
        for image_path in image_path_list:
            export_index += 1
            # percent_cur = int((export_index / image_size_len) * 100)
            image = cv2.imread(image_path)
            if image is None:  # 增加对图像是否正确读取的检查
                logger.error("Image not loaded:" + image_path)
                continue
            resized_image = cv2.resize(image, (width, height))  # 将图像的宽度和高度设置为适合MPEG-4的尺寸
            if image is not None:
                video.write(resized_image)
            # if percent_cur / 10:
            #     logger.info(f"export process to export_index / image_size_len：{export_index} / {image_size_len} * "
            #                 f"100 /10 {percent_cur}%")
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
    url = url.replace("\n", "")
    filename = filename.replace("\n", "")
    # 记录开始时间
    start_time = time.time()
    constants.download_finish_flag = False
    if os.path.exists(filename):
        logger.warning(f"zip file already download! skip file name: {filename}")
        constants.download_finish_flag = True
        return True
    try:
        with urllib.request.urlopen(url, timeout=10) as response:  # Add timeout parameter for https connections
            with open(filename, 'wb') as out_file:
                chunk_size = 1024  # Adjust chunk size as needed
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    out_file.flush()
        file_size = os.path.getsize(filename)
        end_time = time.time()
        download_time = end_time - start_time
        logger.info(f"Download of {filename} completed in {download_time:.2f} seconds, size: {file_size}")
        constants.download_finish_flag = True
        return True
    except Exception as e:
        logger.warning(f"Error downloading {filename}: {e}")
        return False


@logger.catch
def url_zip_all_process(zip_url_txt_list):
    """
    zip url process : download zip to local file dir
    :param zip_url_txt_list:
    :return:
    """
    logger.info("get zip url txt in zip url.")
    if len(zip_url_txt_list) == 0:
        logger.warning("current data path null zip_txt file!")
        return False
    for zip_url_detail in zip_url_txt_list:
        txt_path, txt_name = os.path.split(zip_url_detail)
        txt_file_name, ext = os.path.splitext(zip_url_detail)
        # 去重
        old_file_name = os.path.join(txt_path, zip_url_detail)
        if "_result" not in txt_file_name:
            new_file_name = os.path.join(txt_path, txt_file_name + "_result" + ext)
            logger.warning(f"file: {new_file_name} not exists, create it.")

        else:
            new_file_name = txt_file_name + ext
            # logger.warning(f"file: {new_file_name} already exists, not create.")
        # if not os.path.exists(new_file_name):
        remove_duplicates_from_txt(old_file_name, new_file_name)
        logger.success(f"remove duplicate file success: {zip_url_detail}")
        with open(new_file_name, 'r', encoding='utf-8', errors='replace') as f:
            zip_url_list = f.readlines()
        if len(zip_url_list) == 0:
            logger.warning(f"txt file null, name：{zip_url_detail}")
            continue
        logger.info(f"start download all zip file! txt file name: {zip_url_detail}")
        for zip_url in zip_url_list:
            if not download_all_zip(zip_url, txt_path):
                continue
    constants.download_gif_zip_flag = False
    logger.success(f"zip download file success! zip file length: {len(zip_url_txt_list)}")
    return True


@logger.catch
def unzip_generate_gif():
    """
    unzip file from zip file
    :param :
    :return:
    """
    zip_file_list = scan_directory_zip(constants.data_path)
    if len(zip_file_list) == 0:
        logger.warning("zip file not exists.")
        return False
    return generate_gif_video(zip_file_list)
