import os
import sys

from selenium.webdriver.common.by import By

from file.file_process import record_end_spider_image_keyword, record_finish_keyword, \
    exists_image_keyword, keyword_times
from utils.file_utils import filter_exists_images, url_list_save, write_url_txt
from utils.keyword_utils import exists_keyword_finish_txt
from utils.spider_operate import filter_not_use_url, slider_page_down, url_process_page, open_look_all, filter_not_use
from utils.spider_param import spider_param_config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image.spider_gif_url import spider_gif_images
from loguru import logger
from selenium.common import NoSuchWindowException
import time
from pypinyin import lazy_pinyin, Style

from run import constants
from run.constants import detail_delta_time, search_delta_time, s1_url, target_url, s2_url, data_path, \
    spider_images_max_count


@logger.catch
def save_img_url(driver, key_word):
    """
    save img from txt load artwork href
    :param driver:
    :param key_word:
    :return:
    """
    key_word_pinyin = ''.join(lazy_pinyin(key_word, style=Style.TONE3))
    cdds = [os.path.join(root, _) for root, dirs, files in os.walk(data_path) for _ in files if
            _.endswith(key_word_pinyin + "_result_url.txt")]
    for cdds_path in cdds:
        logger.debug("save name: " + str(cdds_path))
        with open(cdds_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not constants.stop_spider_url_flag:
                    # 允许继续抓取url
                    if not artwork_to_image(key_word_pinyin, driver, url):
                        break
                else:
                    logger.warning("stop spider url! save_img url.")
                    return False
    return True


@logger.catch
def artwork_to_image(key_word_pinyin, driver, url):
    """
    spider point url image from url
    :param key_word_pinyin:
    :param driver:
    :param url:
    :return:
    """
    driver.get(url)
    if driver.title == '【国家反诈中心、工信部反诈中心、中国电信、中国联通、中国移动联合提醒】':
        logger.warning("error! will exit: cur visit domain blocked.")
        constants.firewall_flag = True
        return False
    if open_look_all(driver):
        logger.success(f"click look all {key_word_pinyin} success! pid: {url[-9:]}")  # 116299335
    # 抓取动图link
    if constants.spider_mode == 'manual':
        # 手动模式滑动页面 自动模式不滑动
        slider_page_down(driver)
    time.sleep(detail_delta_time)
    spider_gif_images(key_word_pinyin, driver)
    # logger.success("gif url txt save success!")
    image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
    for image_element in image_elements:
        image_url = image_element.get_attribute("src")
        if filter_not_use(image_url):
            continue
        else:
            result = filter_exists_images(key_word_pinyin, image_url, "_img")
            if result:
                continue
            driver.execute_script("return arguments[0].src;", image_element)
            image_filename = os.path.basename(image_url)  # 获取图片文件名
            image_url = image_url.replace(s1_url, target_url)
            image_url = image_url.replace(s2_url, target_url)
            constants.spider_images_current_count += 1
            # 已获取img 数量自增 仅在此统计
            write_url_txt(data_path + "/img_url/", key_word_pinyin + "_img", image_url)
            logger.debug(f"save: {image_filename}, save num: {constants.spider_images_current_count}")
    return True


@logger.catch
def spider_artworks_url(self, key_word):
    """
     spider image from point url.
    :param self:
    :parameter key_word 关键字
    :return:
    """
    driver, url, cur_page = spider_param_config(key_word)
    if driver is None or url is None or cur_page is None:
        constants.stop_spider_url_flag = True
        logger.info("spider single image end, not execute follow operate!")
        return True
    # 处理 当抓取关键词存在于download_finish_txt.txt中,删除该关键词，以方便下次下载
    exists_keyword_finish_txt(key_word)
    while True:
        key_word_flag, last_page = exists_image_keyword(key_word)
        if key_word_flag:
            cur_page = int(last_page) + 1
            logger.warning(f"last already spider: {key_word} and page: {last_page}, next page: {cur_page}")
        if constants.stop_spider_url_flag:
            logger.warning("stop spider url, get url spider artwork url.")
            break
        url_detail = url_process_page(url, current_page=cur_page)
        logger.info("current use url: " + str(url_detail))
        driver.get(url_detail)
        time.sleep(search_delta_time)
        if driver.title == '【国家反诈中心、工信部反诈中心、中国电信、中国联通、中国移动联合提醒】':
            logger.warning("error! will exit: cur visit domain blocked.")
            constants.firewall_flag = True
            break
        logger.debug("start load href save url to txt.")
        load_save_flag = load_href_save(driver, key_word)
        if load_save_flag == 1:
            try:
                if not save_img_url(driver, key_word):
                    break
                record_finish_keyword(key_word, cur_page)
                # cur_page += 1
                logger.success("save img all finish, current page:  " + str(cur_page))

            except NoSuchWindowException as nswe:
                logger.warning("chrome force exit! detail:" + str(nswe))
        elif load_save_flag == 2:
            # all pid exists skip, spider next page image
            record_finish_keyword(key_word, cur_page)
            # cur_page += 1
            logger.warning("all pid exists skip, spider next page image, current page:  " + str(cur_page))

            keyword_count = keyword_times(key_word, cur_page)
            if keyword_count > 2:
                logger.warning(f"cur keyword count: {keyword_count} > 2 , will spider next keyword! ")
                break
        else:
            logger.warning("skip spider loop!")
            break
    self.success_tips()
    if constants.spider_mode == 'manual':
        constants.stop_spider_url_flag = True
    logger.warning("google chrome will exit! ")
    record_end_spider_image_keyword(cur_page=cur_page, key_word=key_word)
    driver.quit()


@logger.catch
def load_href_save(driver, key_word):
    """
    load pixiv list href url and save this
    :param driver:
    :param key_word:
    :return:
    """
    key_word_pinyin = ''.join(lazy_pinyin(key_word, style=Style.TONE3))
    image_urls_list = []
    image_urls_exists_list = []
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        for image_element in image_elements:
            if not constants.stop_spider_url_flag:
                image_url = image_element.get_attribute("href")
                if image_url is None:
                    break
                if filter_not_use_url(image_url):
                    continue
                driver.execute_script("return arguments[0].href;", image_element)
                # filter already exists image
                if filter_exists_images(key_word_pinyin, image_url, "_url"):
                    image_urls_exists_list.append(image_url)
                    continue
                image_urls_list.append(image_url)
                if constants.spider_images_current_count >= int(spider_images_max_count) and constants.spider_mode \
                        == 'manual':
                    logger.warning(
                        "spider image max value, current value: " + str(constants.spider_images_current_count))
                    constants.spider_images_current_count = 0
                    constants.stop_spider_url_flag = False
                    break
            else:
                # logger.warning(f"spider url stop！cur spider image_element {image_element}")
                break
        if url_list_save(key_word_pinyin, image_urls_list):
            logger.success("save url and remove duplicates content success!")
            return 1
        elif len(image_urls_list) == len(image_urls_exists_list):
            logger.warning("cur page image already save, will spider next page!")
            return 2
        else:
            return 3
    except Exception as un_e:
        logger.error("Error, unknown error, detail:" + str(un_e))
        return 0
