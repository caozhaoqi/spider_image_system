import os
import sys
import threading
from pathlib import Path
import time
from typing import Tuple, Optional, List

sys.path.append(str(Path(__file__).parent.parent))

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common import NoSuchWindowException
from selenium.webdriver import ActionChains, Keys
from selenium.common.exceptions import WebDriverException
from loguru import logger
from pypinyin import lazy_pinyin, Style

from file.file_process import (
    record_end_spider_image_keyword, record_finish_keyword,
    exists_image_keyword, keyword_times
)
from utils.file_utils import (
    filter_exists_images, url_list_save, write_url_txt
)
from utils.keyword_utils import exists_keyword_finish_txt
from utils.spider_operate import (
    filter_not_use_url, slider_page_down, url_process_page,
    open_look_all, filter_not_use
)
from utils.spider_param import spider_param_config
from utils.time_utils import sys_sleep_time
from image.spider_gif_url import spider_gif_images
from image.spider_img_save import download_img_txt
from run import constants
from run.constants import (
    detail_delta_time, search_delta_time, s1_url, target_url,
    s2_url, data_path, spider_images_max_count, allow_replace_domain_flag
)


@logger.catch
def save_img_url(self, driver: WebDriver, key_word: str, cur_page: int) -> bool:
    """Save images from txt file containing artwork URLs"""
    key_word_pinyin = ''.join(lazy_pinyin(key_word, style=Style.TONE3))
    txt_files = [os.path.join(root, f) for root, _, files in os.walk(data_path) 
                for f in files if f.endswith(f"{key_word_pinyin}_result_url.txt")]

    for txt_path in txt_files:
        logger.debug(f"Processing file: {txt_path}")
        with open(txt_path, 'r', encoding='utf-8') as f:
            for url in f:
                url = url.strip()
                if not url or constants.SpiderConfig.stop_spider_url_flag:
                    logger.warning("Spider URL stopped")
                    return False

                pid = url[-9:]
                logger.info(f"Starting spider PID: {pid}, keyword: {key_word_pinyin}")

                if self:
                    self.spider_progress_show_label.setText(
                        f"抓取关键字: {key_word}, 页码: {cur_page},"
                        f" 抓取图片名: {pid},"
                        f" 已抓取数目: {constants.spider_images_current_count}"
                    )

                if not artwork_to_image(key_word_pinyin, driver, url):
                    return False

    return True


@logger.catch 
def artwork_to_image(key_word_pinyin: str, driver: WebDriver, url: str) -> bool:
    """Spider images from specific artwork URL"""
    try:
        driver.get(url)
        if driver.title == constants.ban_content:
            logger.warning("Domain blocked - exiting")
            constants.ProcessingConfig.firewall_flag = True
            return False

        if open_look_all(driver):
            logger.success(f"Opened all images for {key_word_pinyin}, PID: {url[-9:]}")

        if constants.SpiderConfig.spider_mode == 'manual':
            slider_page_down(driver)

        sys_sleep_time(driver, detail_delta_time, True)
        spider_gif_images(key_word_pinyin, driver)
        save_img_element(driver, key_word_pinyin)
        return True

    except Exception as e:
        logger.warning(f"Error processing URL: {type(e).__name__}")
        return False


@logger.catch
def save_img_element(driver: WebDriver, key_word_pinyin: str) -> None:
    """Save individual image elements from page"""
    try:
        for img in driver.find_elements(By.CSS_SELECTOR, "img"):
            try:
                image_url = img.get_attribute("src")
                if not image_url or filter_not_use(image_url):
                    continue

                if filter_exists_images(key_word_pinyin, image_url, "_img"):
                    logger.warning(f"Image already exists: {key_word_pinyin}")
                    continue

                driver.execute_script("return arguments[0].src;", img)
                
                if allow_replace_domain_flag:
                    image_url = image_url.replace(s1_url, target_url).replace(s2_url, target_url)

                constants.spider_images_current_count += 1
                write_url_txt(f"{data_path}/img_url/", f"{key_word_pinyin}_img", image_url)
                logger.debug(f"Saved image {os.path.basename(image_url)}, count: {constants.spider_images_current_count}")

            except Exception as e:
                if isinstance(e, WebDriverException):
                    logger.error("WebDriver error - stopping")
                    break
                logger.warning(f"Error saving image: {type(e).__name__}")
                continue

    except Exception as e:
        logger.warning(f"Error processing images: {type(e).__name__}")


@logger.catch
def clear_cache_refresh(driver: WebDriver) -> None:
    """Clear browser cache and refresh page"""
    try:
        driver.refresh()
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.execute_script("window.open('');")
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.switch_to.window(driver.window_handles[-1])
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.get('chrome://settings/clearBrowserData')
        sys_sleep_time(driver, constants.detail_delta_time, False)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3).perform()
        sys_sleep_time(driver, constants.detail_delta_time, False)

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER).perform()
        sys_sleep_time(driver, constants.detail_delta_time, False)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        logger.info("Cache cleared successfully")

    except Exception as e:
        logger.warning(f"Error clearing cache: {type(e).__name__}")


@logger.catch
def detect_download_working(self) -> None:
    """Check and start download thread if needed"""
    if constants.scheduled_download_program_flag and constants.SpiderConfig.stop_download_image_flag:
        logger.debug("Starting download thread")
        threading.Thread(target=download_img_txt, args=(None,)).start()
        constants.SpiderConfig.stop_download_image_flag = False
        logger.info("Download thread started")


@logger.catch
def spider_artworks_url(self, key_word: str) -> bool:
    """Spider images for given keyword"""
    driver_start_time = time.time()
    driver, url, cur_page = spider_param_config(key_word)

    if driver is None and url is None and cur_page is None:
        constants.SpiderConfig.stop_spider_url_flag = True
        logger.info("Spider completed - no more work")
        return True
    elif driver is None:
        logger.warning("Driver error - continuing to next keyword")
        return False

    exists_keyword_finish_txt(key_word)

    try:
        while True:
            if constants.SpiderConfig.stop_spider_url_flag:
                break

            key_word_flag, last_page = exists_image_keyword(key_word)
            if key_word_flag:
                cur_page = int(last_page) + 1
                logger.warning(f"Continuing from page {cur_page} for {key_word}")

            url_detail = url_process_page(url, current_page=cur_page)
            if self:
                self.spider_progress_show_label.setText(
                    f"抓取关键字: {key_word}, 页码: {cur_page},"
                    f" 已抓取数目: {constants.spider_images_current_count}"
                )
                self.sys_tips(f"抓取关键词: {key_word}中(*^▽^*)...")

            try:
                driver.get(url_detail)
                logger.info(f"Chrome startup took {time.time() - driver_start_time:.2f}s")
                sys_sleep_time(driver, search_delta_time, True)

                detect_download_working(self)

                if driver.title in (constants.ban_content, constants.visit_url, '', '请稍候…'):
                    logger.warning("Page access blocked or invalid")
                    constants.ProcessingConfig.firewall_flag = True
                    break

            except Exception as e:
                logger.warning(f"Error accessing URL: {type(e).__name__}")
                break

            load_result = load_href_save(driver, key_word)
            if load_result == 1:
                if not save_img_url(self, driver, key_word, cur_page):
                    break
                record_finish_keyword(key_word, cur_page)
                logger.success(f"Completed page {cur_page}")

            elif load_result == 2:
                record_finish_keyword(key_word, cur_page)
                if keyword_times(key_word, cur_page) > 2:
                    logger.warning("Keyword limit reached - moving to next")
                    break

            else:
                logger.warning("Skipping spider loop")
                break

    finally:
        if self:
            self.spider_progress_show_label.setText("0/0")
            self.success_tips(f"关键词: {key_word}, 图片爬取操作")
        else:
            logger.success("Spider completed successfully")

        if constants.SpiderConfig.spider_mode == 'manual':
            constants.SpiderConfig.stop_spider_url_flag = True

        try:
            logger.warning(f"Closing Chrome ({driver.title})")
        except Exception as e:
            logger.warning(f"Error closing Chrome: {type(e).__name__}")

        record_end_spider_image_keyword(str(cur_page), key_word)
        clear_cache_refresh(driver)
        driver.quit()

    return True


@logger.catch
def load_href_save(driver: WebDriver, key_word: str) -> int:
    """Load and save artwork URLs from page"""
    key_word_pinyin = ''.join(lazy_pinyin(key_word, style=Style.TONE3))
    image_urls: List[str] = []
    existing_urls: List[str] = []

    try:
        for link in driver.find_elements(By.CSS_SELECTOR, "a"):
            if constants.SpiderConfig.stop_spider_url_flag:
                break

            url = link.get_attribute("href")
            if not url or filter_not_use_url(url):
                continue

            driver.execute_script("return arguments[0].href;", link)

            if filter_exists_images(key_word_pinyin, url, "_url"):
                existing_urls.append(url)
                continue

            image_urls.append(url)

            if (constants.spider_images_current_count >= int(spider_images_max_count) and 
                constants.SpiderConfig.spider_mode == 'manual'):
                logger.warning(f"Reached max images: {constants.spider_images_current_count}")
                constants.spider_images_current_count = 0
                constants.SpiderConfig.stop_spider_url_flag = False
                break

        if url_list_save(key_word_pinyin, image_urls):
            logger.success("URLs saved successfully")
            return 1
        elif len(image_urls) == len(existing_urls):
            logger.warning("All images already saved - moving to next page")
            return 2
        else:
            return 3

    except Exception as e:
        logger.warning(f"Error loading URLs: {type(e).__name__}")
        return 0
