import os

from PyQt5.QtWidgets import QMessageBox
from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchWindowException
from selenium.webdriver.common.by import By
import time

from gui import constants
from gui.constants import detail_delta_time, proxy_flag, search_delta_time, r18_mode, all_show, s1_url, \
    visit_url, target_url, s2_url, data_path, spider_images_max_count
from utils.log_record import log_record


@logger.catch
def save_img_url(driver, key_word):
    """
    save img from txt load artwork href
    :param driver:
    :param key_word:
    :return:
    """

    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith("_result_url.txt")]
    for cdds_path in cdds:
        logger.debug("start save img url, artwork href from file name: " + str(cdds_path))
        with open(cdds_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url:
                    driver.get(url)
                    time.sleep(detail_delta_time)
                    image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
                    for image_element in image_elements:
                        image_url = image_element.get_attribute("src")
                        if filter_not_use(image_url):
                            continue
                        else:
                            driver.execute_script("return arguments[0].src;", image_element)
                            image_filename = os.path.basename(image_url)  # 获取图片文件名
                            image_url = image_url.replace(s1_url, target_url)
                            image_url = image_url.replace(s2_url, target_url)
                            write_url_txt(data_path + "/img_url/", key_word + "_img", image_url)
                            logger.debug(f"replace point source url, save img url success: {image_filename}")
    return True


@logger.catch
def spider_artworks_url(self, key_word):
    """
     spider image from point url .
    :param self:
    :parameter key_word 关键字
    :return:
    """
    # 设置代理服务器
    proxy = {
        "proxyType": "manual",
        "httpProxy": "http://192.168.199.26:8080",  # 代理服务器地址和端口
        "ftpProxy": "http://192.168.199.26:8080",
        "sslProxy": "http://192.168.199.26:8080",
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    # 创建浏览器驱动程序并设置代理参数
    options = webdriver.ChromeOptions()
    if proxy_flag == 'True':
        options.set_capability("proxy", proxy)
        logger.info("current use internal proxy.")

    driver = webdriver.Chrome(options=options)
    # key_word = self.filetext.text()
    # tags/娜维娅/artworks?mode=r18&s_mode=s_tag
    mode = ''
    if r18_mode == 'True':
        mode = 'mode=r18&'
        logger.info("current r18 mode!")
    if all_show == 'True':
        other = 'illustrations'
    url = "https://" + visit_url + "/tags/" + key_word + "/artworks?" + mode + "s_mode=s_tag"
    logger.info("current use url : " + str(url))
    driver.get(url)
    # 等待图片加载完成
    time.sleep(search_delta_time)
    logger.debug("start load href save url to txt.")
    load_save_flag = load_href_save(driver, key_word)
    if load_save_flag:
        # 使用函数
        try:
            save_img_url(driver, key_word)
            logger.success("save img all finish, could start download images! ")
        except NoSuchWindowException as nswe:
            logger.warning("chrome force exit! detail:" + str(nswe))
    constants.spider_image_flag = False
    QMessageBox.information(self, u"完成", u"操作完成")
    logger.warning("google chrome will exit! ")
    driver.quit()
    # w = UIMainWindows()
    # self.complete()


@logger.catch
def write_url_txt(path, file_name, url):
    """

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
def load_href_save(driver, key_word):
    """
    load pixiv list href url and save this
    :param driver:
    :param key_word:
    :return:
    """
    image_urls_list = []
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        for image_element in image_elements:
            image_url = image_element.get_attribute("href")
            if filter_not_use_url(image_url):
                continue
            driver.execute_script("return arguments[0].href;", image_element)
            image_urls_list.append(image_url)
            if len(image_urls_list) > spider_images_max_count:
                # 超过最大值 跳出循环 不在保存url地址
                logger.warning("spider image max value, value: " + str(len(image_urls_list)))
                break
            logger.debug("load href and start save img url: " + image_url)
        if len(image_urls_list) > 0:
            for image_url_content in image_urls_list:
                write_url_txt(data_path + "/href_url/", key_word + "_url", image_url_content)
            remove_duplicates_from_txt(data_path + "/href_url/" + key_word + "_url.txt",
                                       data_path + "/href_url/" + key_word + "_result_url.txt")
            logger.success("load_href_save: href remove duplicates content success, result: href_url: _result_url.txt.")
            return True
        else:
            logger.warning("you input key word error or other err, please check log file!")
            return False
    except Exception as un_e:
        logger.error("Error, unknown error, detail:" + str(un_e))
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
                file.write(line)
    except FileNotFoundError as ffe:
        logger.warning("dir not exists , will create dir. detail: " + str(ffe))
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
                file.write(line)
    except Exception as ue:
        logger.error("unknown error, detail: " + str(ue))


@logger.catch
def filter_not_use(url):
    """
    filter not need url
    :param url:
    :return:
    """
    # /emoji/501.png https://pximg.lolicon.ac.cn/user-profile/img/2023/12/11/14/38/09
    # /25260574_6aed493b358851d4d2fbfb53290b5991_50.jpg
    if "js" in url or "emoji" in url or "svq" in url or "_50.png" in url:
        return True


@logger.catch
def filter_not_use_url(image_url):
    """
    filter not need http url
    :param image_url: filter url
    :return:
    """
    # /emoji/501.png
    if "artworks" not in image_url or "s_mode=s_tag" in image_url or "block.2021.host" in image_url:
        return True


if __name__ == '__main__':
    try:
        log_record()
        spider_artworks_url()
    except Exception as e:
        logger.error("Error！ detail msg: " + str(e))
