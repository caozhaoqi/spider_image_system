# import this
import fnmatch
import json
import os

import requests
# from gofilepy import GofileClient
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
            if os.path.getsize(file_name_path) > 0:
            	file_list.append(os.path.join(root, file))
    return file_list


@logger.catch
def upload_all_gofile(path):
    """

    :param path:
    :return:
    """
    try:
        list_file = scan_files_go(path)
        if not list_file:
            logger.warning(f"Current path: {path} no files, detail: {list_file}")
            return False
        # 使用示例
        for file in list_file:
            http_upload(file)
    except Exception as e:
        logger.error(f"ERROR!!! detail: {e}")


if __name__ == '__main__':
    upload_all_gofile('./')