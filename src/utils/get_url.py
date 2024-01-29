import os

from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchWindowException
from selenium.webdriver.common.by import By
import time

from gui import constants
from gui.constants import detail_delta_time, proxy_flag, search_delta_time, r18_mode, all_show, s1_url, \
    visit_url, target_url, s2_url, data_path, spider_images_max_count


@logger.catch
def save_img_url(driver, key_word):
    """
    save img from txt load artwork href
    :param driver:
    :param key_word:
    :return:
    """

    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith(key_word + "_result_url.txt")]
    images_cur_count = 0
    for cdds_path in cdds:
        logger.debug("start save img url, artwork href from file name: " + str(cdds_path))
        with open(cdds_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not constants.stop_spider_url_flag:
                    # 允许继续抓取url
                    driver.get(url)
                    time.sleep(detail_delta_time)
                    image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
                    for image_element in image_elements:
                        image_url = image_element.get_attribute("src")
                        if filter_not_use(image_url):
                            continue
                        else:
                            result = filter_exists_images(key_word, image_url, "_img")
                            if result:
                                continue
                            images_cur_count += 1
                            driver.execute_script("return arguments[0].src;", image_element)
                            image_filename = os.path.basename(image_url)  # 获取图片文件名
                            image_url = image_url.replace(s1_url, target_url)
                            image_url = image_url.replace(s2_url, target_url)
                            write_url_txt(data_path + "/img_url/", key_word + "_img", image_url)
                            logger.debug(f"from url: {url}, replace point source url, save _img url success: "
                                         f"{image_filename}, _img txt all save images count(cur spider count and _img "
                                         f"txt count): {constants.spider_images_current_count + images_cur_count}")
                else:
                    logger.warning("stop spider url! save_img url.")
                    return False
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
        "httpProxy": "http://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),  # 代理服务器地址和端口
        "ftpProxy": "http://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "sslProxy": "http://" + constants.proxy_server_ip + ":" + str(constants.proxy_server_port),
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    # 创建浏览器驱动程序并设置代理参数
    options = webdriver.ChromeOptions()
    if proxy_flag == 'True':
        options.set_capability("proxy", proxy)
        logger.info("current use internal proxy, proxy content: " + str(proxy['httpProxy']))

    driver = webdriver.Chrome(options=options)
    # tags/娜维娅/artworks?mode=r18&s_mode=s_tag
    mode = ''
    if r18_mode == 'True':
        mode = 'mode=r18&'
        logger.info("current start use r18 mode!")
    if all_show == 'True':
        other = 'illustrations'
    cur_page = 1
    url = "https://" + visit_url + "/tags/" + key_word + "/artworks?" + mode
    while True:
        if constants.stop_spider_url_flag:
            logger.warning("stop spider url. get url spider artwork url.")
            break
        url_detail = url_process_page(url, current_page=cur_page)
        logger.info("current use url : " + str(url_detail))
        driver.get(url_detail)
        # 等待图片加载完成
        time.sleep(search_delta_time)
        logger.debug("start load href save url to txt.")
        load_save_flag = load_href_save(driver, key_word)
        if load_save_flag:
            # 使用函数
            try:
                if not save_img_url(driver, key_word):
                    # 达到最大值爬虫停止跳出循环
                    break
                # 否则继续爬取下一页包括 当前页图片已存在 继续爬取下一页
                cur_page += 1
                logger.success("save img all finish，current page:  " + str(cur_page))

            except NoSuchWindowException as nswe:
                logger.warning("chrome force exit! detail:" + str(nswe))

        else:
            break
    # 循环抓取结束 断掉浏览器 重置标志位、
    self.success_tips()
    constants.stop_spider_url_flag = True
    logger.warning("google chrome will exit! ")
    driver.quit()


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
def filter_exists_images(key_word, image_url, txt_name):
    """
    filter already exists images
    :param key_word:
    :param image_url:
    :param txt_name: 执行过程：存artwork url 存images url
    过滤当前已存在的images或url
    :return:
    """
    if txt_name == '_url':
        #     处于存artwork url阶段 读取相应keyword txt artwork url save txt
        file_name = constants.data_path + "/href_url/" + key_word + "_url.txt"
        # file_name = r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data\href_url\xianyun_url
        # .txt" txt_url = []
        try:
            with open(file_name, 'r') as f:
                txt_url = f.readlines()
            return find_value(image_url + "\n", txt_url)
        except Exception as e:
            logger.warning("unknown error, detail: " + str(e))
            return False
    elif txt_name == '_img':
        file_name = constants.data_path + "/img_url/" + key_word + "_img.txt"
        # txt_url = []
        try:
            with open(file_name, 'r') as f:
                txt_url = f.readlines()
            return find_value(image_url + "\n", txt_url)
        except Exception as e:
            logger.warning("unknown error, detail: " + str(e))
            return False
    # elif txt_name == '_result':
    #     pass
    # pass
    return False


@logger.catch
def find_value(target_value, data_list):
    """
    查找列表中是否存在目标值
    :param target_value:
    :param data_list:
    :return:
    """
    for item in data_list:
        if item == target_value:
            logger.warning("image url or artwork url exists, will skip, file name: " + target_value)
            return True
    return False


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
            if not constants.stop_spider_url_flag:
                # 是否不停止抓取
                image_url = image_element.get_attribute("href")
                if image_url is None:
                    # 该地址中无图片地址 跳出循环
                    break
                if filter_not_use_url(image_url):
                    continue
                driver.execute_script("return arguments[0].href;", image_element)
                # filter already exists image
                if filter_exists_images(key_word, image_url, "_url"):
                    continue
                image_urls_list.append(image_url)
                constants.spider_images_current_count += 1
                if constants.spider_images_current_count >= int(spider_images_max_count) - 1:
                    # 超过最大值 跳出循环 不在保存url地址 存储现有url地址
                    logger.warning("spider image max value, current value: " + str(constants.spider_images_current_count))
                    constants.spider_images_current_count = 0
                    constants.stop_spider_url_flag = False
                    break
            else:
                logger.warning(f"spider url stop！cur spider image_element {image_element}")
                break
        if url_list_save(key_word, image_urls_list):
            logger.success("save url and remove duplicates content success!")
            return True
    except Exception as un_e:
        logger.error("Error, unknown error, detail:" + str(un_e))
        return False
    return False


@logger.catch
def url_list_save(key_word, image_urls_list):
    """
    save url to txt
    :param key_word: 关键字
    :param image_urls_list: images lists
    :return:
    """
    if not constants.stop_spider_url_flag:
        if len(image_urls_list) > 0:
            for image_url_content in image_urls_list:
                write_url_txt(data_path + "/href_url/", key_word + "_url", image_url_content)
            remove_duplicates_from_txt(data_path + "/href_url/" + key_word + "_url.txt",
                                       data_path + "/href_url/" + key_word + "_result_url.txt")
            logger.success("load_href_save: href remove duplicates content success, result: href_url: _result_url.txt.")
            return True
        elif len(image_urls_list) == 0:
            logger.warning("no image! don't save to url txt, image url all exists set true jump next!")
            return True
        else:
            logger.warning("you input key word error or other err, please check log file!")
            return False
    else:
        logger.warning("stop spider url! url list save")
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
    # filter_url_http = []
    filter_url_http = constants.filter_http_url.split(',')
    # logger.info(f"http url regex content: {constants.filter_http_url}")
    try:
        for filter_url_http_content in filter_url_http:
            if filter_url_http_content in url:
                return True
    except Exception as e:
        # 遇到异常跳过该url
        logger.warning("unknown error! detail: " + str(e))
        return True


@logger.catch
def filter_not_use_url(image_url):
    """
    filter not need http url
    :param image_url: filter url
    :return:
    """
    filter_url_image = constants.filter_image_url.split(',')
    # logger.info(f"image url regex content: {constants.filter_image_url}")
    try:
        # /emoji/501.png
        for filter_url_image_content in filter_url_image:
            if filter_url_image_content in image_url or "artworks" not in image_url:
                return True
    except Exception as e:
        # 遇到异常跳过该url
        logger.warning("unknown error, detail: " + str(e))
        return True


@logger.catch
def url_process_page(url, current_page):
    """
    split page from point url
    :param current_page:
    :param url:
    :return:
    """
    page_url = url + "p=" + str(current_page) + "&s_mode=s_tag"
    return page_url
    # pass


if __name__ == '__main__':
    # ret = filter_exists_images("xianyun", "https://sd.2021.host/artworks/115463073", "_url")
    # logger.info(ret)
    ret = filter_not_use("https://sd.2021.host/artworks/115463073")
    logger.success(ret)
# url_process_page("")
#     try:
#         log_record()
#         spider_artworks_url()
#     except Exception as e:
#         logger.error("Error！ detail msg: " + str(e))
