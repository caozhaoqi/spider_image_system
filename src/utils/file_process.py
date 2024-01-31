import os
from loguru import logger


@logger.catch
def scan_directory(path):
    """
    scan dir
    :param path:
    :return:
    """

    video_files = []
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.mp4') or file.endswith('.avi'):  # 仅处理jpg和png图片文件
                video_files.append(os.path.join(root, file))
    return video_files


@logger.catch
def scan_directory_zip_txt(path):
    """
    scan dir
    :param path:
    :return:
    """

    video_files = []
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt') and "_zip" in file:  # 仅处理jpg和png图片文件
                video_files.append(os.path.join(root, file))
    return video_files


@logger.catch
def scan_directory_zip(path):
    """
    scan dir
    :param path:
    :return:
    """

    video_files = []
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.zip'):  # 仅处理jpg和png图片文件
                video_files.append(os.path.join(root, file))
    return video_files
