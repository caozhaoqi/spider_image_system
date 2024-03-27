import requests
from loguru import logger

API_URL = "https://ai.gitee.com/api/endpoints/caozhaoqi/blip2-opt-2-7b-168/inference"
headers = {
    "Authorization": "Bearer eyJpc3MiOiJodHRwczovL2FpLmdpdGVlLmNvbSIsInN1YiI6IjQ3OSJ9"
                     ".rxFDc0Vv5ZoJWdxgpuvsWakiUg_zlE_Ypxc1Gc4LvWrZlI7wBVX5gIB8O_N8gE58w5U0np8L4lKH2d5PYNU6Bg",
    "Content-Type": "image/jpeg"
}


@logger.catch
def query(filename):
    """

    :param filename:
    :return:
    """
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    if response.status_code != '200':
        logger.info(response.content)
        return None
    return response.json()


if __name__ == '__main__':
    output = query(
        r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\data\img_url\qin2_img_result\images"
        r"\master\117144583_p4_master1200.jpg")
