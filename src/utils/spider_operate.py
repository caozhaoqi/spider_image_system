"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent.parent))

import random
from loguru import logger
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from run import constants
from utils.time_utils import sys_sleep_time


@logger.catch
def filter_not_use(url: str) -> bool:
    """过滤不需要的URL
    
    Args:
        url: 要过滤的URL
        
    Returns:
        是否需要过滤
    """
    filter_urls = constants.filter_http_url.split(',')
    try:
        return any(filter_url in url for filter_url in filter_urls)
    except Exception as e:
        logger.warning(f"URL过滤出错: {e}")
        return True


@logger.catch 
def filter_not_use_url(image_url: str) -> bool:
    """过滤不需要的图片URL
    
    Args:
        image_url: 要过滤的图片URL
        
    Returns:
        是否需要过滤
    """
    filter_urls = constants.filter_image_url.split(',')
    try:
        return any(filter_url in image_url for filter_url in filter_urls) or "artworks" not in image_url
    except Exception as e:
        logger.warning(f"图片URL过滤出错: {e}")
        return True


@logger.catch
def artwork_filter(url: str) -> bool:
    """过滤用户图片爬取的URL
    
    Args:
        url: 要过滤的URL
        
    Returns:
        是否需要过滤
    """
    parts = url.split("/artworks/")
    if len(parts) > 1:
        return not parts[1].isdigit()
    return True


@logger.catch
def url_process_page(url: str, current_page: int) -> str:
    """处理分页URL
    
    Args:
        url: 基础URL
        current_page: 当前页码
        
    Returns:
        处理后的URL
    """
    return f"{url}p={current_page}&s_mode=s_tag"


@logger.catch
def open_look_all(driver: WebDriver) -> bool:
    """点击"查看全部"或"阅读作品"按钮
    
    Args:
        driver: WebDriver实例
        
    Returns:
        是否点击成功
    """
    try:
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 查找按钮的多种策略
        button_texts = ['查看全部', '阅读作品', '查看更多', '查看全部作品']
        button = None
        
        # 策略1: 使用JavaScript查找
        for text in button_texts:
            button = driver.execute_script(f"""
                return Array.from(document.getElementsByTagName('button'))
                    .find(btn => btn.textContent && btn.textContent.trim().includes('{text}'));
            """)
            if button:
                logger.info(f"找到按钮（JavaScript）: {text}")
                break
        
        # 策略2: 使用XPath查找
        if not button:
            for text in button_texts:
                try:
                    button = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    logger.info(f"找到按钮（XPath）: {text}")
                    break
                except:
                    continue
        
        # 策略3: 使用CSS选择器查找包含特定文本的元素
        if not button:
            for text in button_texts:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, "button, a[role='button'], div[role='button']")
                    for elem in elements:
                        if text in elem.text:
                            button = elem
                            logger.info(f"找到按钮（CSS选择器）: {text}")
                            break
                    if button:
                        break
                except:
                    continue
        
        if button:
            # 滚动到按钮位置
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            sys_sleep_time(driver, 1, False)
            
            # 使用JavaScript点击
            driver.execute_script("arguments[0].click();", button)
            logger.info("按钮点击成功")
            
            sys_sleep_time(driver, constants.detail_delta_time, False)
            random_action(driver)
            return True
        else:
            logger.warning("未找到任何目标按钮")
            # 调试信息：列出所有按钮
            all_buttons = driver.execute_script("""
                return Array.from(document.getElementsByTagName('button'))
                    .map(btn => btn.textContent.trim()).filter(text => text.length > 0);
            """)
            logger.debug(f"页面上的所有按钮文本: {all_buttons}")
            
    except Exception as e:
        logger.warning(f"点击按钮失败: {e}")
        logger.exception(e)
        
    return False


@logger.catch
def slider_page_down(driver: WebDriver) -> None:
    """页面滑动操作
    
    Args:
        driver: WebDriver实例
    """
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")
        actions = ActionChains(driver)

        for key in [Keys.END, Keys.PAGE_DOWN, Keys.HOME, Keys.PAGE_DOWN]:
            actions.send_keys(key).perform()
            sys_sleep_time(driver, constants.detail_delta_time, False)

        logger.info(f"页面滑动完成,页面高度: {page_height}px")
        random_action(driver)
        
    except Exception as e:
        logger.warning(f"页面滑动失败: {type(e).__name__}")


@logger.catch
def random_action(driver: WebDriver) -> None:
    """执行随机页面操作
    
    Args:
        driver: WebDriver实例
    """
    try:
        page_height = driver.execute_script("return document.body.scrollHeight")
        actions = ActionChains(driver)
        
        random_delay = random.uniform(1, 5)
        random_keys = [Keys.END, Keys.PAGE_DOWN, Keys.HOME]
        random_key_order = random.sample(random_keys, len(random_keys))
        random_key_repeats = random.randint(1, 5)

        for key in random_key_order:
            for _ in range(random_key_repeats):
                actions.send_keys(key).perform()
                sys_sleep_time(driver, random.random() * random_delay, False)

        sys_sleep_time(driver, random.random() * random_delay, False)
        actions.send_keys(Keys.HOME).perform()
        actions.send_keys(Keys.PAGE_DOWN).perform()
        sys_sleep_time(driver, random.random() * random_delay, False)
        
        logger.info(f"随机页面操作完成,页面高度: {page_height}px")
        
    except Exception as e:
        logger.warning(f"随机操作失败: {type(e).__name__}")
