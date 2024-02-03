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
