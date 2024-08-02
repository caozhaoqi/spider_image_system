import json
import os
import shutil

import requests
from loguru import logger

from image.img_switch import find_images
from run import constants


@logger.catch
def detect_img_py_v1(img_path):
    """

    :param img_path:
    :return:
    """
    url = "http://" + str(constants.proxy_server_ip) + ":" + str(constants.proxy_server_port) + "/detect"
    result_server = "Default response"
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}  # 注意这里的键名应该与服务器期望的键名一致
            # response = requests.post('http://example.com/upload', files=files, data=fields)
            response = requests.post(url, files=files)
            result = json.loads(response.text)
            result_server = result
            if result['code'] == 200:
                score = result['score']
                # {'drawings': 0.9475243, 'hentai': 0.034198754, 'neutral': 0.01824669, 'porn': 1.687202e-05,
                # 'sexy': 1.34658585e-05}
                max_score = max(score['porn'], score['drawings'], score['hentai'], score['neutral'], score['sexy'])
                if score['porn'] == max_score:
                    move_detect_img(img_path, "porn")
                    result = "porn"
                elif score['drawings'] == max_score:
                    move_detect_img(img_path, "drawings")
                    result = "drawings"
                elif score['hentai'] == max_score:
                    move_detect_img(img_path, "hentai")
                    result = "hentai"
                elif score['neutral'] == max_score:
                    move_detect_img(img_path, "neutral")
                    result = "neutral"
                elif score['sexy'] == max_score:
                    move_detect_img(img_path, "sexy")
                    result = "sexy"
                else:
                    move_detect_img(img_path, "other")
                    result = "other"
                return result + ": " + str(max_score)
            else:
                logger.warning(f"Unknown error, server result_server: {result_server}, detail: {img_path}, skied.")
                # constants.detect_model_flag = False
                return False
    except Exception as e:
        logger.warning(
            f"Unknown error, server result_server: {result_server}, detail: {e}, error image_path: {img_path}, skied.")
        # constants.detect_model_flag = False
        return False


@logger.catch
def detect_img_py_local(img_path):
    """
    https://luckycola.com.cn/public/dist/#/
    :param img_path
    :return: result
    """
    user_id = "q52O3c1717064554705xtiQBlHfRQ"
    key_api = "68V6BNlZRnMKB61717064554705xvLYwelki0"
    link_https = "https://luckycola.com.cn/tools/checkImg"
    # method = "post"
    # file = open(img_path).read()
    # ret = requests.post(link_https)
    # if ret["code"] == 0:
    #     logger.info(ret)
    # requests.Request.prepare()
    # 发送POST请求，包含文件
    with open(img_path, 'rb') as file:
        data = {'ColaKey': key_api,
                'file': file}  # 假设服务器期望的字段名是'file'
        files = {'file': ('file.jpg', open(img_path, 'rb'), 'image/jpeg')}
        response = requests.post(link_https, files=file)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON响应
        try:
            data = response.json()
            if data.get("code") == 0:  # 假设成功的响应包含一个"code"键，其值为0
                logger.info("Upload successful: %s", data)
            else:
                logger.error("Upload failed with code %s: %s", data.get("code"),
                             data.get("message", "No message provided"))
        except ValueError as e:
            logger.error("Failed to parse JSON response: %s", e)
    else:
        logger.error("Request failed with status code %s", response.status_code)


safeContent = ['Drawing', 'Neutral']
# // 设置图片内容安全的类型

# // https://github.com/alex000kim/nsfw_data_scraper

imgTypeObj = {
    "Drawing": '艺术性的',
    "Neutral": '中性的',
    "Sexy": '性感的',
    "Porn": '色情的',
    "Hentai": '变态的',
}


@logger.catch
def model_detect_img_java_v1(img_path):
    """

    :param img_path
    :return:
    """
    import requests

    url = "http://" + constants.dmi_api_server + "/check"
    result_server = "Default response"
    try:
        with open(img_path, 'rb') as file:
            files = {'file': file}  # 注意这里的键名应该与服务器期望的键名一致
            # response = requests.post('http://example.com/upload', files=files, data=fields)
            response = requests.post(url, files=files)
            result = json.loads(response.text)
            result_server = result
            if result['code'] == 200:
                score = result['score']
                # {'drawings': 0.9475243, 'hentai': 0.034198754, 'neutral': 0.01824669, 'porn': 1.687202e-05,
                # 'sexy': 1.34658585e-05}
                max_score = max(score['porn'], score['drawings'], score['hentai'], score['neutral'], score['sexy'])
                if score['porn'] == max_score:
                    move_detect_img(img_path, "porn")
                    result = "porn"
                elif score['drawings'] == max_score:
                    move_detect_img(img_path, "drawings")
                    result = "drawings"
                elif score['hentai'] == max_score:
                    move_detect_img(img_path, "hentai")
                    result = "hentai"
                elif score['neutral'] == max_score:
                    move_detect_img(img_path, "neutral")
                    result = "neutral"
                elif score['sexy'] == max_score:
                    move_detect_img(img_path, "sexy")
                    result = "sexy"
                else:
                    move_detect_img(img_path, "other")
                    result = "other"
                return result + ": " + str(max_score)
            else:
                logger.warning(f"Unknown error, server result_server: {result_server}, detail: {img_path}, skied.")
                # constants.detect_model_flag = False
                return False
    except Exception as e:
        logger.warning(
            f"Unknown error, server result_server: {result_server}, detail: {e}, error image_path: {img_path}, skied.")
        # constants.detect_model_flag = False
        return False


@logger.catch
def move_detect_img(img_path, folder_name):
    """

    :param img_path:
    :param folder_name:
    :return:
    """
    dir_path, file_name = os.path.split(img_path)
    if not os.path.exists(dir_path + "/" + folder_name + "/"):
        os.makedirs(dir_path + "/" + folder_name + "/")
    try:
        with open(dir_path + '/' + folder_name + '_image_txt.txt', 'a', encoding='utf-8', errors='replace') as f:
            f.write(img_path + "\n")
        shutil.move(img_path, dir_path + "/" + folder_name + "/" + file_name)
        f.close()
    except Exception as e:
        ...
    return True


@logger.catch
def all_img_detect(path):
    """

    :param path:
    :return:
    """
    img_list = find_images(path)  #
    i = 0
    img_list_folder = []
    count = len(img_list)
    # match_img_result() xx_img
    for img_path in img_list:
        # img_url = match_img_result(img_path)
        # if img_url not in img_list_folder:
        #     img_list_folder.append(img_url)
        i += 1
        if "porn" in img_path or "sexy" in img_path or "other" in img_path or "neutral" in img_path or "drawings" \
                in img_path or "hentai" in img_path:
            continue
        elif constants.detect_img_model == "python":
            ret = detect_img_py_v1(img_path=img_path)
        else:
            ret = model_detect_img_java_v1(img_path=img_path)
        # if not ret:
        #     logger.error(f"Unknown error, content: {ret}, detect img will exit.")
        #     break
        logger.debug(f"{constants.detect_img_model} detect img: {img_path}, cur {i}/{count}, server response: {ret}")
    constants.detect_model_flag = False
    logger.success("Model detect image all success!")

#
# if __name__ == '__main__':
#     all_img_detect(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data")
