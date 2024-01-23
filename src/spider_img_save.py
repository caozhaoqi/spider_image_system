import os
import requests

from loguru import logger

from src.get_url import remove_duplicates_from_txt


@logger.catch
def download_image(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.debug(f"Image downloaded and saved as {filename}")
        else:
            logger.error(f"Error! Failed to download image from {url}" + "detail reason: " + str(response.content))


@logger.catch
def download_images_from_file(file_path):
    (name, suffix) = os.path.splitext(file_path)
    save_img_url = name + "/images"
    with open(file_path, 'r') as f:
        for line in f:
            url = line.strip()
            if url:  # 跳过空行
                if not os.path.exists(save_img_url):
                    os.makedirs(save_img_url)
                filename = os.path.join(name + "/images", f"{os.path.basename(url)}")
                download_image(url, filename)


def download_img_txt(self):
    # log_record()
    cdds = [os.path.join(root, _) for root, dirs, files in os.walk("data/") for _ in files if
            _.endswith("_img.txt")]
    for cdds_path in cdds:
        # file_path = "urls.txt"  # 你的txt文件路径
        logger.debug("download img before , remove duplicate.")
        file_path, file_name = os.path.split(cdds_path)
        base_name, ext = os.path.splitext(file_name)
        new_file_name = file_path + "/" + base_name + "_result.txt"
        remove_duplicates_from_txt(cdds_path,
                                   new_file_name)
        logger.success("remove duplicat success, start new file name :" + new_file_name)
        download_images_from_file(new_file_name)
    logger.success("downloaded all image !")
    # w = UIMainWindows()
    # w.complete()
    self.complete()
    return True
