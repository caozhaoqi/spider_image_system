import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
import os
from loguru import logger


@logger.catch
def convert_txt(input_file_path, output_file_path):
    """

    :param input_file_path:
    :param output_file_path:
    :return:
    """
    read_lines = []
    # 尝试使用UTF-8编码打开文件
    try:
        with codecs.open(input_file_path, 'r', encoding='gbk', errors='replace') as file:
            read_lines = file.readlines()
            file.readline()
            file.read()
        with codecs.open(input_file_path, 'r', encoding='utf-8', errors='replace') as file:
            read_lines.extend(file.readlines())
    except Exception as e:
        logger.debug(f"error, detail: {e}")
        # exit(1)
    # read_lines = remove_non_printable_chars(read_lines)
    with codecs.open(output_file_path, 'w', encoding='utf-8', errors='replace') as cleaned_file:
        for line_num, line in enumerate(read_lines, start=1):
            # if line_num not in corrupt_lines:
            cleaned_file.write(line)

    logger.debug(f"already：cleaned: {output_file_path}")


@logger.catch
def scan_txt_file_all(path):
    """

    :param path:
    :return:

    """
    for txt in scan_txt(path):
        file_path_front, file_name = os.path.split(txt)
        file_name_front, file_ext = os.path.splitext(file_name)
        output_file_path = os.path.join(file_path_front, file_name_front + "_utf8.txt")
        convert_txt(txt, output_file_path)
    # logger.info('convert finish.')


@logger.catch
def scan_txt(path):
    """
    sacn img txt from point path
    :param path:
    :return:
    """

    # txt
    img_txt_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('spider_finished_keyword.txt') or file.endswith('download_finished_txt.txt'):
                img_txt_files.append(os.path.join(root, file))
    return img_txt_files
