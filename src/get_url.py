import os

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from src.gui.constants import detail_delta_time, proxy_flag, search_delta_time, r18_mode, all_show, s1_url, \
    visit_url
from src.utils.log_record import log_record


@logger.catch
def save_img_url(driver, key_word):
    """
    save img from txt load artwork href
    :param driver:
    :param key_word:
    :return:
    """

    cdds = [os.path.join(root, _) for root, dirs, files in os.walk("data/") for _ in files if
            _.endswith("_result_url.txt")]
    for cdds_path in cdds:
        logger.debug("start save img url,artwork href from file name: " + str(cdds_path))
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
                            image_url = image_url.replace("i.pximg.net", "pixiv.322333.xyz")
                            image_url = image_url.replace("s.pximg.net", "pixiv.322333.xyz")
                            write_url_txt("data/img_url/", key_word + "_img", image_url)
                            logger.debug(f"save img url success: {image_filename}")
    return True


@logger.catch
def spider_artworks_url(self, key_word):
    """

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
    if proxy_flag:
        options.set_capability("proxy", proxy)
        logger.info("current use internal proxy.")

    driver = webdriver.Chrome(options=options)
    # key_word = self.filetext.text()
    # tags/娜维娅/artworks?mode=r18&s_mode=s_tag
    mode = ''
    if r18_mode:
        mode = 'mode=r18&'
        logger.info("current r18 mode!")
    if all_show:
        other = 'illustrations'
    url = "https://"+visit_url+"/tags/" + key_word + "/artworks?" + mode + "s_mode=s_tag"
    logger.info("current use url : " + str(url))
    driver.get(url)
    # 等待图片加载完成
    time.sleep(search_delta_time)
    logger.debug("start load href save url to txt .")
    load_save_flag = load_href_save(driver, key_word)
    if load_save_flag:
        # 使用函数
        save_img_url(driver, key_word)
    logger.success("save img all finish, google chrome will exit! start download img.")
    driver.quit()
    # w = UIMainWindows()
    self.complete()


@logger.catch
def write_url_txt(path, file_name, url):
    """

    :param path:
    :param file_name:
    :param url:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)
    # for url in img_list:
    with open(path + file_name + ".txt", "a") as f:
        f.write(str(url) + "\n")
    f.close()


@logger.catch
def load_href_save(driver, key_word):
    """
    load pixiv list href url and save this
    :param driver:
    :param key_word:
    :return:
    """
    image_elements = driver.find_elements(By.CSS_SELECTOR, "a")
    for image_element in image_elements:
        image_url = image_element.get_attribute("href")
        if "artworks" not in image_url:
            continue
        driver.execute_script("return arguments[0].href;", image_element)
        logger.debug("load href and start save img url: " + image_url)
        write_url_txt("data/href_url/", key_word + "_url", image_url)
    remove_duplicates_from_txt("./data/href_url/" + key_word + "_url.txt",
                               "./data/href_url/" + key_word + "_result_url.txt")
    logger.success("remove duplicates content success!")
    return True


@logger.catch
def remove_duplicates_from_txt(input_file, output_file):
    """
    remove duplicates content from txt
    :param input_file: input
    :param output_file: result
    :return:
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 使用集合去重
    unique_lines = set(lines)

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in unique_lines:
            file.write(line)


@logger.catch
def filter_not_use(url):
    """
    filter not need url
    :param url:
    :return:
    """
    # /emoji/501.png
    if "js" in url or "emoji" in url or "svq" in url:
        return True


if __name__ == '__main__':
    try:
        log_record()
        spider_artworks_url()
    except Exception as e:
        logger.error("Error！ detail msg: " + str(e))
