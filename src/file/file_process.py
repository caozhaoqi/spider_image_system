import json
import os
import sys
import time

from model.ImageModel import ImageModel
from model.SpiderKeywordModel import SpiderKeyWordModel
from run import constants
from utils.http_tools import image_url_re
from utils.time_utils import time_to_utc

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
    with open(filename, 'r', encoding='utf-8') as file:
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
        with open(img_txt, 'r', encoding='utf-8') as f:
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
    with open(txt_path, 'a', encoding='utf-8') as f:
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
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(json_str)
    return True


@logger.catch
def look_end_download_image(file_name):
    if not os.path.exists(file_name):
        logger.warning("not found image record json data file! ")
        return None
    else:
        # 打开JSON文件并读取其内容
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data


@logger.catch
def read_end_download_image():
    """
    return download msg for last download
    :return:
    """
    download_final_flag = look_end_download_image(os.path.join(constants.data_path, "download_final_image.json"))
    if download_final_flag:
        download_final_flag_model = ImageModel(download_final_flag['image_index'], download_final_flag['txt_name'],
                                               download_final_flag['image_url'], download_final_flag['image_name'],
                                               download_final_flag['download_date'], download_final_flag['txt_index'],
                                               download_final_flag['continue_flag'])
        final_download_txt_name = download_final_flag_model.txt_name
        final_download_url = download_final_flag_model.image_url
        final_cdds_index = download_final_flag_model.txt_index
        continue_download_flag = download_final_flag_model.continue_flag
        return download_final_flag_model, final_download_txt_name, final_download_url, final_cdds_index, \
               continue_download_flag
    return None, None, None, None, None


@logger.catch
def save_download_end(index, file_path, url, cdds_index):
    """
    save data to json file
    :param index:
    :param file_path:
    :param url:
    :param cdds_index:
    :return:
    """
    data = ImageModel(index, file_path, url, image_url_re(url),
                      time_to_utc(time.time()), cdds_index, True)
    record_end_download_image(os.path.join(constants.data_path, "download_final_image.json"), data)
    logger.warning(
        f"set stop image stop_download_image_flag True! save result: {data.image_url}, txt name: {file_path}.")


@logger.catch
def update_download_continue_flag():
    """
    update json file
    :return:
    """
    data = ImageModel(None, None, None, None,
                      time_to_utc(time.time()), None, False)
    record_end_download_image(os.path.join(constants.data_path, "download_final_image.json"), data)
    logger.info("download final image json continue_flag update success!")
    # constants.con


@logger.catch
def record_download_finish_txt(content):
    """
    record already download txt
    :param content:
    :return:
    """
    if exists_txt_from_finish(content):
        return True
    file_name = os.path.join(constants.data_path, "download_finished_txt.txt")
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write(content + "\n")
    logger.success(f"download {content} finished, will write txt.")
    return True


@logger.catch
def exists_txt_from_finish(content):
    """
    exists txt download finish image
    :param content:
    :return:
    """
    # txt_list = []
    file_name = os.path.join(constants.data_path, "download_finished_txt.txt")
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("")
        return False
    with open(file_name, 'r', encoding='utf-8') as f:
        txt_list = f.readlines()
    for txt in txt_list:
        if content in txt:
            logger.warning(f"{content} already download finished, will skip txt!")
            return True


@logger.catch
def record_end_spider_image_keyword(key_word, cur_page):
    """
    record end spider image keyword
    :param key_word:
    :param cur_page:
    :return:
    """
    spider_image_keyword, txt_file_list = get_image_keyword()
    cur_keyword_txt = find_keyword_txt(key_word, txt_file_list, spider_image_keyword)
    file_name = constants.data_path + '/spider_img_keyword_final.json'
    if cur_keyword_txt:
        data = SpiderKeyWordModel(cur_keyword_txt, key_word, cur_page, True)
        json_str = json.dumps(data.__dict__, ensure_ascii=False)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json_str)
        logger.success("stop spider, spider end keyword already write txt.")
        return True
    else:
        logger.warning("new keyword! txt not save.")
        return False


@logger.catch
def get_image_keyword():
    """
    get image keyword list
    :return:
    """
    auto_spider_file_path = os.path.join(constants.data_path, "auto_spider_img")

    if not os.path.exists(auto_spider_file_path):
        os.makedirs(auto_spider_file_path)

    txt_file_list = []
    for root, dirs, files in os.walk(auto_spider_file_path):
        for file in files:
            if file.endswith('spider_img_keyword.txt'):
                txt_file_list.append(os.path.join(root, file))

    file_name = 'spider_img_keyword.txt'
    full_file_path = os.path.join(auto_spider_file_path, file_name)
    if not os.path.exists(full_file_path):
        # 如果文件不存在，创建它
        with open(full_file_path, 'w', encoding='utf-8') as f:
            logger.warning(f"{full_file_path} not exists, will create demo txt!")
    try:
        if len(txt_file_list) == 0:
            logger.warning("spider_img_keyword txt length null!")
            return [], []
        spider_image_keyword = []
        for txt_name in txt_file_list:
            with open(txt_name, 'r', encoding='utf-8') as f:
                spider_image_keyword.append(f.readlines())
        return spider_image_keyword, txt_file_list
    except Exception as e:
        logger.error(f"unknown error, detail {e}")
        return [], []


@logger.catch
def find_keyword_txt(key_word, txt_file_list, spider_image_keyword):
    """
    find point keyword in txt
    :param spider_image_keyword:
    :param key_word:
    :param txt_file_list:
    :return:
    """
    cur_keyword_txt = None
    for spider_image in txt_file_list:
        with open(spider_image, 'r', encoding='utf-8') as f:
            spider_image_keyword.append(f.readlines())
            for spider_image_k in spider_image_keyword:
                for s_i_k in spider_image_k:
                    if key_word in s_i_k:
                        cur_keyword_txt = spider_image
                        break
    return cur_keyword_txt


@logger.catch
def record_finish_keyword(keyword, cur_page):
    """
    record finish spider keyword and page
    :param keyword:
    :param cur_page:
    :return:
    """
    file_name = "/spider_finished_keyword.txt"
    content = keyword + "," + str(cur_page)
    file_name = constants.data_path + file_name
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("")
        return False
    with open(file_name, "a", encoding='utf-8') as f:
        f.write(content + "\n")
    logger.success(f"record finish keyword {keyword}, page {cur_page}!")


@logger.catch
def keyword_times(keyword, cur_page):
    """
    多次写入同一keyword+cur_page
    :param keyword:
    :param cur_page:
    :return:
    """
    same_count = 0
    file_name = "/spider_finished_keyword.txt"
    file_name = constants.data_path + file_name
    content = keyword + "," + str(cur_page)

    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("")
        return False
    with open(file_name, "r", encoding='utf-8') as f:
        keyword_list = f.readlines()

    for keyword_con in keyword_list:
        if content in keyword_con:
            same_count += 1
    return same_count


@logger.catch
def exists_image_keyword(key_word):
    """
    get image keyword list
    :return:
    """
    file_name = '/spider_finished_keyword.txt'
    try:
        exists_record = []
        with open(constants.data_path + file_name, 'r', encoding='utf-8') as f:
            spider_image_keyword = f.readlines()
        if not spider_image_keyword:
            return False, 0
        for spider_image in spider_image_keyword:
            sik_w = spider_image.split(',')[0]
            sik_page = spider_image.split(',')[1]
            if key_word in sik_w:
                exists_record.append(sik_page)
                # logger.success()
        if exists_record:
            return True, max(exists_record)
    except Exception as e:
        # logger.warning(f"unknown error, detail {e}")
        return False, 0
    return False, 0
