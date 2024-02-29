import os
import re
import sys

from loguru import logger

from run import constants
from run.constants import data_path
from utils.http_tools import image_url_re
import shutil
from pypinyin import lazy_pinyin, Style


@logger.catch
def write_url_txt(path, file_name, url):
    """
    write url to txt file
    :param path:
    :param file_name:
    :param url:
    :return:
    """
    try:
        with open(path + file_name + ".txt", "a") as f:
            f.write(str(url) + "\n")
        f.close()
    except FileNotFoundError as ffe:
        logger.warning("dir not exists , will create dir. detail: " + str(ffe))
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + file_name + ".txt", "a") as f:
            f.write(str(url) + "\n")
        f.close()
    except Exception as ue:
        logger.error("unknown error, detail: " + str(ue))


@logger.catch
def filter_exists_images(key_word, image_url, txt_name):
    """
    filter already exists images
    :param key_word:
    :param image_url:
    :param txt_name: 执行过程：存artwork url 存images url
    过滤当前已存在的images或url
    :return:
    """
    if txt_name == '_url':
        file_name = constants.data_path + "/href_url/" + key_word + "_url.txt"
        try:
            with open(file_name, 'r') as f:
                txt_url = f.readlines()
            return find_value(image_url + "\n", txt_url)
        except Exception as e:
            return False
    elif txt_name == '_img':
        file_name = constants.data_path + "/img_url/" + key_word + "_img.txt"
        image_url = image_url_re(image_url)
        try:
            with open(file_name, 'r') as f:
                txt_url = f.readlines()
            return find_value(image_url + "\n", txt_url)
        except Exception as e:
            return False
    return False


@logger.catch
def find_value(target_value, data_list):
    """
    查找列表中是否存在目标值
    :param target_value:
    :param data_list:
    :return:
    """
    for item in data_list:
        if item == target_value:
            logger.warning("item exists will skip, pid: " + target_value[-9:])
            return True
    return False


@logger.catch
def url_list_save(key_word, image_urls_list):
    """
    save url to txt
    :param key_word: 关键字
    :param image_urls_list: images lists
    :return:
    """
    if not constants.stop_spider_url_flag:
        if len(image_urls_list) > 0:
            for image_url_content in image_urls_list:
                write_url_txt(data_path + "/href_url/", key_word + "_url", image_url_content)
            remove_duplicates_from_txt(data_path + "/href_url/" + key_word + "_url.txt",
                                       data_path + "/href_url/" + key_word + "_result_url.txt")
            # logger.success("function load_href_save(): href remove duplicates content success, result: href_url: "
            #                "_result_url.txt.")
            return True
        elif len(image_urls_list) == 0:
            logger.warning("no image! don't save to url txt, chrome will exit!")
            return False
        else:
            logger.warning("you input key word error or other err, please check log file!")
            return False
    else:
        logger.warning("stop spider url! url list save will exit.")
        return False


@logger.catch
def remove_duplicates_from_txt(input_file, output_file):
    """
    remove duplicates content from txt
    :param input_file: input
    :param output_file: result
    :return:
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 使用集合去重
        unique_lines = set(lines)

        with open(output_file, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                if line.strip():
                    file.write(line)
    except FileNotFoundError as ffe:
        logger.warning("dir not exists, will create dir. detail: " + str(ffe))
        if not os.path.exists(input_file):
            os.makedirs(input_file)
        if not os.path.exists(output_file):
            os.makedirs(output_file)
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 使用集合去重
        unique_lines = set(lines)

        with open(output_file, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                if line.strip():
                    file.write(line)
    except Exception as ue:
        logger.error("unknown error, detail: " + str(ue))


@logger.catch
def get_data_file(filename):
    """

    获取数据文件的路径，无论是直接运行还是通过 PyInstaller 打包
    :param filename
    :return
    """
    if getattr(sys, 'frozen', False):
        # 如果程序是“冷冻的”，即打包后的 exe
        basedir = sys._MEIPASS
    else:
        # 如果程序是直接运行的，即没有打包
        basedir = os.path.dirname(__file__)

    return os.path.join(basedir, filename)


@logger.catch
def get_all_folders(directory):
    """

    :param directory:
    :return:
    """
    folders = []
    for root, dirs, files in os.walk(directory):
        folders.extend(dirs)
    return folders


@logger.catch
def convert_and_move_folder(folder_path):
    """

    :param folder_path:
    :return:
    """
    # 获取文件夹名称
    all_folders = get_all_folders(folder_path)
    for folder in all_folders:
        folder_name = os.path.basename(folder)

        if contains_chinese(folder_name):
            # 将文件夹名称转换为拼音
            pinyin_folder_name = ''.join(lazy_pinyin(folder_name, style=Style.TONE3))

            # base_path = os.path.join(folder_path, folder)
            # 创建新的拼音文件夹路径
            pinyin_folder_path = os.path.join(os.path.join(os.path.join(folder_path, pinyin_folder_name), 'images'),
                                              'master')

            # 检查新文件夹是否已存在
            if os.path.exists(pinyin_folder_path):
                logger.warning(f"Folder '{pinyin_folder_name}' already exists. Moving content to the existing folder.")
                # 移动文件夹内容到已存在的文件夹
                move_content_to_existing_folder(os.path.join(folder_path, folder), pinyin_folder_path)
            else:
                # 如果新文件夹不存在，则创建它，并移动文件夹内容到新文件夹
                os.makedirs(pinyin_folder_path)
                move_sou_dir = os.path.join(folder_path, folder)
                for img in os.listdir(move_sou_dir):
                    # if os.path.isfile(os.path.join(path, filename)):
                    shutil.move(os.path.join(move_sou_dir, img), pinyin_folder_path)
                logger.success(
                    f"Folder '{folder_name}' has been converted to '{pinyin_folder_name}' and moved successfully.")
                # os.remove(move_sou_dir)
        else:
            if "master" in folder_name or "images" in folder_name:
                logger.info(f"no chinese path: {folder_name}")
    constants.convert_folder_name_flag = False
    logger.success("all folder convert success!")


@logger.catch
def move_content_to_existing_folder(source_folder_path, target_folder_path):
    """

    :param source_folder_path:
    :param target_folder_path:
    :return:
    """
    # 获取源文件夹中的所有文件和子文件夹
    for item in os.listdir(source_folder_path):
        source_item_path = os.path.join(source_folder_path, item)
        target_item_path = os.path.join(target_folder_path, item)

        # 如果是文件夹，则递归调用此函数
        if os.path.isdir(source_item_path):
            move_content_to_existing_folder(source_item_path, target_item_path)
        else:
            # 如果是文件，则直接移动文件
            shutil.move(source_item_path, target_item_path)
    # os.remove(source_folder_path)


@logger.catch
def contains_chinese(folder_name):
    """

    :param folder_name:
    :return:
    """
    # 使用正则表达式匹配中文字符
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(pattern.search(folder_name))

# 示例使用
# # 示例使用
# folder_to_convert = '/path/to/your/folder'  # 替换成你要转换的文件夹路径
# convert_and_move_folder(folder_to_convert)
