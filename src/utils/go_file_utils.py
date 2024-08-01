"""
go file upload to server
file: go_file_utils.py
author: zq.c
modify time: 2024/8/1 12:00
create time: 2024/7/24 12:00
"""

import json
import os

import requests
from loguru import logger

"""

token: sz6exDf8GuR0yuB38GOerYDspmY5qB7F
id: e6b6dd7f-a89a-4165-af70-9674aab82c18
folderId: f5822db9-1046-4a41-b6f1-3ad3aee6e8fe

"""


@logger.catch
def http_upload(file_path):
    """

    :param file_path:
    :return:
    """
    server_list = detect_go_server()
    server_name = server_list[0]['name']
    upload_api_go = f'https://{server_name}.gofile.io/contents/uploadfile'
    # multipart
    # formData = ["file", open(file_path), "folderId", "5e042945-0e5c-4c1d-9293-4574d376e496"]
    headers = {
        "Authorization": "Bearer sz6exDf8GuR0yuB38GOerYDspmY5qB7F"
    }
    data = {
        "folderId": "f5822db9-1046-4a41-b6f1-3ad3aee6e8fe"
    }
    ret = '!!!No Response!!!'
    files = {"file": open(file_path, "rb")}
    try:
        ret = requests.post(upload_api_go, files=files, data=data, headers=headers)
    except Exception as e:
        logger.error(f"Error, detail: {e}")
        ...
    if not ret:
        logger.warning(f"Unknown Error: {ret}")
        return False
    try:
        res = json.loads(ret.content)
        if res['status'] == 'ok':
            logger.success(res['data'])
        else:
            logger.warning(f"File {file_path} upload gofile server fail!!! detail: {res}")
    except Exception as e:
        logger.warning(f"Warning: unknown. {e}")
    # print(file.page_link)  # View and download file at this link
    ...


@logger.catch
def detect_go_server():
    """

    :return:
    """
    api_server_go = 'https://api.gofile.io/servers'
    server_list = []
    method = 'get'
    try:
        ret = json.loads(requests.get(api_server_go).content)
        if ret['status'] == 'ok':
            server_list = ret['data']['servers']
    except Exception as e:
        logger.error(f"Error, detail: {e}")
        ...
    return server_list


@logger.catch
def scan_files_go(directory):
    """

    :param directory:
    :return:
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_name_path = os.path.join(root, file)
            if os.stat(file_name_path).st_size > 0:
                file_list.append(os.path.join(root, file))
    return file_list


@logger.catch
def save_upload_already(txt_data_path, file_path):
    """

    :param txt_data_path:
    :param file_path:
    :return:
    """
    # file_name = "go_file_img_upload.txt"
    file_name = os.path.join(txt_data_path, "go_file_img_upload.txt")
    with open(file_name, 'a', encoding='utf-8', errors='replace') as f:
        f.write(file_path + "\n")
    logger.success(f"save {file_path} finished, will write txt.")
    return True


@logger.catch
def exists_upload_gofile(txt_path):
    """

    :param txt_path:
    :return:
    """

    file_name = 'go_file_img_upload.txt'
    full_file_path = os.path.join(txt_path, file_name)
    if not os.path.exists(full_file_path):
        # 如果文件不存在，创建它
        with open(full_file_path, 'w', encoding='utf-8', errors='replace') as f:
            logger.warning(f"Current {full_file_path} not exists, will create demo txt!")
    try:
        with open(full_file_path, 'r', encoding='utf-8', errors='replace') as f:
            exists_go_file_img = f.readlines()
        return exists_go_file_img
    except Exception as e:
        logger.error(f"Unknown error, detail {e}")
        return []


@logger.catch
def exists_gofile_img(file_name, txt_list):
    """

    :param file_name:
    :param txt_list:
    :return:
    """
    file_name = os.path.basename(file_name)
    for txt in txt_list:
        if file_name in txt:
            return True
    return False


@logger.catch
def upload_all_gofile(data_path):
    """

    :param data_path:
    :return:
    """
    try:
        list_img_txt = exists_upload_gofile(data_path)
        list_file = scan_files_go(data_path)
        if not list_file:
            logger.warning(f"Current path: {data_path} no files, detail: {list_file}")
            return False
        # 使用示例
        for file in list_file:
            if not exists_gofile_img(file, list_img_txt):
                http_upload(file)
                save_upload_already(data_path, file)
            else:
                logger.warning(f"File: {file} Already upload gofile server, skip upload.")
    except Exception as e:
        logger.error(f"ERROR!!! detail: {e}")


if __name__ == '__main__':
    path = r'./'
    upload_all_gofile(path)
