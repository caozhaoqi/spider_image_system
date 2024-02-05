import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.mp4') or file.endswith('.avi'):
                video_files.append(os.path.join(root, file))
    return video_files


@logger.catch
def scan_directory_zip_txt(path):
    """
    scan dir
    :param path:
    :return:
    """

    zip_txt_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt') and "_zip" in file:
                zip_txt_files.append(os.path.join(root, file))
    return zip_txt_files


@logger.catch
def scan_directory_zip(path):
    """
    scan dir
    :param path:
    :return:
    """

    zip_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.zip'):
                zip_files.append(os.path.join(root, file))
    return zip_files


@logger.catch
def count_lines(filename):
    """
    count txt file line
    :param filename:
    :return:
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    return len(lines)


@logger.catch
def scan_img_txt(path):
    """
    sacn img txt from point path
    :param path:
    :return:
    """

    # txt
    img_txt_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('_img.txt') or file.endswith('_img_result.txt'):
                img_txt_files.append(os.path.join(root, file))
    # single txt
    img_list_set = []
    for img_txt in img_txt_files:
        with open(img_txt, 'r') as f:
            img_list_set.append(f.readlines())
    # img
    img_list = []
    for img in img_list_set:
        for img_detail in img:
            img_list.append(img_detail)
    return list(set(img_list))


@logger.catch
def write_error_image(txt_path, image_path):
    """
    写入下载错误图片数据至txt
    :param txt_path:
    :param image_path:
    :return:
    """
    with open(txt_path, 'a') as f:
        f.write(image_path + "\n")
    return True


@logger.catch
def record_end_download_image(file_name, data):
    """
    记录最后一次下载数据
    :param file_name: file name
    :param data: data
    :return: 
    """
    # .__dict__
    json_str = json.dumps(data.__dict__)
    with open(file_name, 'w') as f:
        f.write(json_str)
    return True


@logger.catch
def look_end_download_image(file_name):
    if not os.path.exists(file_name):
        logger.warning("not found image record json data file! ")
        return None
    else:
        # 打开JSON文件并读取其内容
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data
