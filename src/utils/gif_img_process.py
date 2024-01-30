from loguru import logger

from utils.http_request import download_file_fun, unzip_images_url


@logger.catch
def read_gif_url(zip_txt_path):
    """
    from txt read url download zip to unzip img return img path
    :param zip_txt_path: zip url txt save
    :return:
    """
    # url_list = []
    with open(zip_txt_path, "r") as f:
        url_list = f.readlines()
    if len(url_list) > 0:
        for url in url_list:
            unzip_images_url(url)
            logger.info(f"process  gif url... {url}")
        # download_file_fun("https://pximg.lolicon.ac.cn/img-zip-ugoira/img/2024/01/29/02/15/41/115574488_ugoira600x600.zip",
        #                   "./zip.zip")
