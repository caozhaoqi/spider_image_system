from loguru import logger


@logger.catch
def read_gif_url(zip_txt_path, url_list):
    """
    from txt read url download zip to unzip img return img path
    :param url:
    :param zip_txt_path: zip url txt save
    :return:
    """
    # url_list = []
    for url_detail in url_list:
        with open(zip_txt_path, "a") as f:
            f.write(url_detail + "\n")
            logger.success(f"recognize zip url success! write url {url_detail}")
            # download_file_fun("https://pximg.lolicon.ac.cn/img-zip-ugoira/img/2024/01/29/02/15/41/115574488_ugoira600x600.zip",
            #                   "./zip.zip")
    return True
