from loguru import logger


@logger.catch
def read_gif_url(zip_txt_path, url_list):
    """
    from txt read url download zip to unzip img return img path
    :param url_list:
    :param zip_txt_path: zip url txt save
    :return:
    """
    for url_detail in url_list:
        with open(zip_txt_path, "a") as f:
            f.write(url_detail + "\n")
            # logger.success(f"recognize zip url success! write url {url_detail}")
            #                   "./zip.zip")
    return True
