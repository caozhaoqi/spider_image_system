import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By
from file.file_process import record_end_spider_image_keyword, record_finish_keyword, \
    exists_image_keyword, keyword_times
from utils.file_utils import filter_exists_images, url_list_save, write_url_txt
from utils.keyword_utils import exists_keyword_finish_txt
from utils.spider_operate import filter_not_use_url, slider_page_down, url_process_page, open_look_all, filter_not_use
from utils.spider_param import spider_param_config
from image.spider_gif_url import spider_gif_images
from loguru import logger
from selenium.common import NoSuchWindowException
import time
from pypinyin import lazy_pinyin, Style
from run import constants
from run.constants import detail_delta_time, search_delta_time, s1_url, target_url, s2_url, data_path, \
    spider_images_max_count, allow_replace_domain_flag
from selenium.webdriver import ActionChains, Keys
from utils.time_utils import sys_sleep_time, get_cur_time


@logger.catch
def save_img_url(self, driver, key_word, cur_page):
    """
    save img from txt load artwork href
    :param cur_page:
    :param self:
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
                    logger.info(f"------start spider pid: {url[-9:]} image, keyword: {key_word_pinyin}.------")
                    if self:
                        self.spider_progress_show_label.setText(f"抓取关键字: {key_word}, 页码: {cur_page},"
                                                                f" 抓取图片名: {url[-9:]},"
                                                                f" 已抓取数目: {constants.spider_images_current_count} ")
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
    try:
        driver.get(url)
        if driver.title == constants.ban_content:
            logger.warning("error! will exit: cur visit domain blocked.")
            constants.firewall_flag = True
            return False
    except Exception as e:
        logger.warning(f"unknown error: type: {type(e).__name__}")
        return False
    if open_look_all(driver):
        logger.success(f"click look all {key_word_pinyin} success! pid: {url[-9:]}")  # 116299335
    # 抓取动图link
    if constants.spider_mode == 'manual':
        # 手动模式滑动页面 自动模式不滑动
        slider_page_down(driver)
    try:
        # driver.implicitly_wait(detail_delta_time)
        sys_sleep_time(driver, detail_delta_time, True)
        spider_gif_images(key_word_pinyin, driver)
        save_img_element(driver, key_word_pinyin)
        # logger.info(f"------end spider pid: {url[-9:]} image, keyword: {key_word_pinyin}.------")
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")
        return False
    return True


@logger.catch
def save_img_element(driver, key_word_pinyin):
    """

    :param driver:
    :param key_word_pinyin:
    :return:
    """
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, "img")
        for image_element in image_elements:
            try:
                image_url = image_element.get_attribute("src")
                if filter_not_use(image_url) or not image_url:
                    # logger.warning(f"no image src and image not match or all exists in {key_word_pinyin}!")
                    continue
                else:
                    result = filter_exists_images(key_word_pinyin, image_url, "_img")
                    if result:
                        logger.warning(f"image src already exists: {key_word_pinyin}!")
                        continue
                    driver.execute_script("return arguments[0].src;", image_element)
                    image_filename = os.path.basename(image_url)  # 获取图片文件名
                    if allow_replace_domain_flag:
                        image_url = image_url.replace(s1_url, target_url)
                        image_url = image_url.replace(s2_url, target_url)
                    constants.spider_images_current_count += 1
                    # 已获取img 数量自增 仅在此统计
                    write_url_txt(data_path + "/img_url/", key_word_pinyin + "_img", image_url)
                    logger.debug(f"save: {image_filename}, save num: {constants.spider_images_current_count}")
            except Exception as e:
                logger.warning(f"unknown error, will skip cur loop, execute next loop detail, type: {type(e).__name__}")
                # driver.quit()
                if type(e).__name__ == "WebDriverException":
                    logger.error("WebDriverException, loop will quit!")
                    break
                continue
    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")


@logger.catch
def clear_cache_refresh(driver):
    """

    :param driver:
    :return:
    """
    # 刷新页面，减少缓存
    try:
        driver.refresh()
        # 设置隐式等待
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.execute_script("window.open('');")
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.switch_to.window(driver.window_handles[-1])
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)  # send right combination
        actions.perform()
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER)  # confirm
        actions.perform()
        # driver.implicitly_wait(constants.detail_delta_time)
        sys_sleep_time(driver, constants.detail_delta_time, False)

        # wait some time to finish
        driver.close()  # close this tab
        driver.switch_to.window(driver.window_handles[0])  # switch back

        logger.info("clear cache finished!")

    except Exception as e:
        logger.warning(f"unknown error, type: {type(e).__name__}")


@logger.catch
def spider_artworks_url(self, key_word):
    """
     spider image from point url.
    :param self:
    :parameter key_word 关键字
    :return:
    """
    driver_start_time = time.time()
    driver, url, cur_page = spider_param_config(key_word)
    if driver is None and url is None and cur_page is None:
        constants.stop_spider_url_flag = True
        logger.info("spider single image end, not execute follow operate!")
        return True
    elif driver is None:
        logger.warning("driver get error, will continue next keyword.")
        return False
    # 处理 当抓取关键词存在于download_finish_txt.txt中,删除该关键词，以方便下次下载
    exists_keyword_finish_txt(key_word)
    while True:
        key_word_flag, last_page = exists_image_keyword(key_word)
        if key_word_flag:
            cur_page = int(last_page) + 1
            logger.warning(
                f"last already spider: {key_word.strip()} and page: {last_page.strip()}, next page: {cur_page}")
        if constants.stop_spider_url_flag:
            logger.warning("stop spider url, get url spider artwork url.")
            break
        url_detail = url_process_page(url, current_page=cur_page)
        if self:
            self.spider_progress_show_label.setText(f"抓取关键字: {key_word}, 页码: {cur_page},"
                                                    f" 已抓取数目: {constants.spider_images_current_count}")
            self.sys_status_label.setText(f"{get_cur_time()}: 抓取关键词: {key_word}中(*^▽^*)...")
        logger.info("current use url: " + str(url_detail))
        try:
            driver.get(url_detail)
            driver_finish_star_time = time.time()
            logger.info(f"keyword: {key_word}, start chrome cost: {driver_finish_star_time - driver_start_time} s")
            # driver.implicitly_wait(search_delta_time)
            sys_sleep_time(driver, search_delta_time, True)
            if driver.title == constants.ban_content or driver.title == constants.visit_url \
                    or driver.title == '' or driver.title == '请稍候…':
                logger.warning(
                    f"error! will exit: cur visit domain blocked, or visit url: {constants.visit_url} not visit!")
                constants.firewall_flag = True
                break
            logger.debug("start load href save url to txt.")
        except Exception as e:
            logger.warning(f"unknown error: type: {type(e).__name__}, will skip spider!")
            break
        load_save_flag = load_href_save(driver, key_word)
        if load_save_flag == 1:
            try:
                if not save_img_url(self, driver, key_word, cur_page):
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
    if self:
        # stop spider image
        self.spider_progress_show_label.setText("0/0")
        self.success_tips(f"关键词: {key_word}, 图片爬取操作")
    else:
        logger.success("spider image operate success finished!")
    if constants.spider_mode == 'manual':
        constants.stop_spider_url_flag = True
    try:
        logger.warning(f"google chrome will exit! chrome title: {driver.title} ")
    except Exception as e:
        logger.warning(f"google chrome will exit! unknown error, type: {type(e).__name__},")
    record_end_spider_image_keyword(cur_page=cur_page, key_word=key_word)
    clear_cache_refresh(driver)
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
            logger.warning(f"cur page image already save, will spider next page! chrome title: {driver.title}")
            return 2
        else:
            return 3
    except Exception as un_e:
        logger.warning(f"unknown error, type: {type(un_e).__name__}.")
        return 0
