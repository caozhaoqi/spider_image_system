# 设置代理服务器
import time

from loguru import logger
from selenium.common import NoSuchWindowException
from selenium.webdriver.common.by import By

from gui import constants
from gui.constants import proxy_flag, r18_mode, all_show, visit_url, search_delta_time


@logger.catch
def spider_gif_url():
    """

    :return:
    """
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
    url = "https://sd.2021.host/artworks/115574488"
    while True:
        # if constants.stop_spider_url_flag:
        #     logger.warning("stop spider url. get url spider artwork url.")
        #     break
        # url_detail = url_process_page(url, current_page=cur_page)
        logger.info("current use url : " + str(url))
        driver.get(url)
        # 等待图片加载完成
        time.sleep(search_delta_time)
        # logger.debug("start load href save url to txt.")
        load_save_flag = load_href_save(driver, "key_word")
        if load_save_flag:
            # 使用函数
            try:
                # if not load_href_save(driver, key_word):
                #     # 达到最大值爬虫停止跳出循环
                #     break
                # 否则继续爬取下一页包括 当前页图片已存在 继续爬取下一页
                # cur_page += 1
                logger.success("save img all finish，current page:  " + str(cur_page))

            except NoSuchWindowException as nswe:
                logger.warning("chrome force exit! detail:" + str(nswe))

        else:
            break
        # 循环抓取结束 断掉浏览器 重置标志位、
        # self.success_tips()
        constants.stop_spider_url_flag = True
    logger.warning("google chrome will exit! ")
    driver.quit()


@logger.catch
def load_href_save(driver, key_word):
    """
    load pixiv list href url and save this
    :param driver:
    :param key_word:
    :return:
    """
    # key_word_pinyin = ''.join(lazy_pinyin(key_word, style=Style.TONE3))
    image_urls_list = []
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, "a")
        for image_element in image_elements:
            # if not constants.stop_spider_url_flag:
            # 是否不停止抓取
            image_url = image_element.get_attribute("href")
            # if image_url is None:
            #     # 该地址中无图片地址 跳出循环
            #     break
            # if filter_not_use_url(image_url):
            #     continue
            driver.execute_script("return arguments[0].href;", image_element)
            # # filter already exists image
            # if filter_exists_images(key_word_pinyin, image_url, "_url"):
            #     continue
            image_urls_list.append(image_url)
            logger.info(image_url)
        # else:
        # logger.warning(f"spider url stop！cur spider image_element {image_element}")
        # break
        # if url_list_save(key_word_pinyin, image_urls_list):
        #     logger.success("save url and remove duplicates content success!")
        #     return True
    except Exception as un_e:
        logger.error("Error, unknown error, detail:" + str(un_e))
        return False
    return False


from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# 安装Selenium库
# pip install selenium

# 导入所需的模块
# 导入模块时需要根据实际情况进行调整
@logger.catch
def api_spider_link(link):
    """

    :param link:
    :return:
    """
    # 创建一个Chrome浏览器实例，并设置开发者工具选项
    # chrome_options = Options()
    # 创建浏览器驱动程序并设置代理参数
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option("prefs", {
    #     "intl.accept_languages": "en-US,en",
    #     "profile.default_content_setting_values.notifications": 2
    # })
    chrome_options.add_experimental_option("devtools.console.stdout", True)
    driver = webdriver.Chrome(options=chrome_options)

    # 打开目标网页
    driver.get(link)
    import time

    time.sleep(20)
    # 打开开发者工具
    driver.execute_script("window.open();")  # 打开新窗口以打开开发者工具
    driver.switch_to.window(driver.window_handles[-1])  # 切换到新窗口以访问开发者工具

    # 捕获接口记录
    driver.execute_script("console.log(JSON.stringify(performance.getEntriesByType('resource')));")

    # 解析接口记录并保存到文件中
    import json
    import requests
    import time

    with open('../test/resources.json', 'w') as file:
        str_list = driver.execute_script("return window.performance.getEntriesByType('resource');")
        for txt in str_list:
            file.write(str(txt))
        file.close()


@logger.catch
def fun_1(url):
    """

    :return:
    """
    from selenium import webdriver

    # 启动WebDriver并打开目标网页
    driver = webdriver.Chrome()
    driver.get(url)

    # 打开开发者工具
    driver.execute_script("openDevTools();")
    # 如果开发者工具已经打开，则继续执行其他操作

    # 切换到Network标签页
    driver.execute_script("selectNetworkTab();")

    # 执行需要获取API请求信息的操作（例如点击某个按钮或加载某个页面）
    # driver.find_element_by_id("myButton").click()
    time.sleep(20)
    # 等待网络请求完成并获取请求信息
    requests = []
    while True:
        try:
            # 获取当前Network标签页中的所有请求信息
            network_requests = driver.execute_script("return window.networkRequests;")
            for request in network_requests:
                # 将请求信息添加到列表中
                requests.append({
                    "method": request["method"],
                    "url": request["url"],
                    "response": request["response"] if "response" in request else None,
                    "status": request["status"] if "status" in request else None,
                    "timestamp": request["timestamp"] if "timestamp" in request else None,
                })
                logger.info(request)
        except Exception as e:
            logger.warning(str(e))
            break

    # 关闭开发者工具并关闭浏览器窗口
    driver.execute_script("closeDevTools();")
    driver.quit()

    # 将请求信息保存到TXT文件
    with open('../test/api_requests.txt', 'w') as file:
        for request in requests:
            file.write(
                f"Method: {request['method']}\nURL: {request['url']}\nResponse: {request['response']}\nStatus: {request['status']}\nTimestamp: {request['timestamp']}\n\n")


def fun_2(url):
    """

    :param url:
    :return:
    """
    # 导入必要的模块
    from selenium import webdriver
    import time

    options = webdriver.ChromeOptions()
    options.add_argument("--auto-open-devtools-for-tabs")
    driver = webdriver.Chrome(options=options)
    driver.get(url)  # 替换为实际的网页URL

    # 等待网页加载完成
    time.sleep(7)  # 等待5秒钟，确保网页上的资源完全加载完成
    api_urls = []

    # 切换到开发者工具窗口并获取网络请求的API地址
    requests = driver.execute_script("return window.performance.getEntriesByType('resource')")
    for request in requests:
        if request['initiatorType'] == 'img':
            logger.info(f"img: {request}")
        elif request['initiatorType'] == 'link':
            logger.info(f"link: {request}")
        elif request['initiatorType'] == 'fetch':
            logger.info(f"zip url {request}")
            if "img-zip-ugoira" in request['name']:
                api_urls.append(request['name'])
                logger.success(f"zip url {request['name']}")
        else:
            logger.warning(request)
        # print(f"URL: {request['url']}, Status: {request['status']}, Time: {request['time']}")

    with open('../test/api_urls.txt', 'a') as file:
        for url in api_urls:
            file.write(url + '\n')  # 将每个API地址写入txt文件中，每个地址占一行
            logger.info(url)

    # 关闭浏览器和开发者工具窗口
    driver.close()  # 关闭浏览器窗口
    driver.switch_to.window(driver.window_handles[0])  # 返回到正常浏览模式窗口的句柄，这里假设正常浏览模式窗口的句柄是0号窗口句柄。根据实际情况进行调整。
    pass


@logger.catch
def spider_gif_images(url, driver):
    """
    抓取动态资源
    :param url: 抓取url
    :param driver:  chrome驱动
    :return:
    """
    api_urls = []

    # 切换到开发者工具窗口并获取网络请求的API地址
    requests = driver.execute_script("return window.performance.getEntriesByType('resource')")
    for request in requests:
        if request['initiatorType'] == 'img':
            logger.info(f"img: {request}")
        elif request['initiatorType'] == 'link':
            logger.info(f"link: {request}")
        elif request['initiatorType'] == 'fetch':
            logger.info(f"zip url {request}")
            if "img-zip-ugoira" in request['name']:
                api_urls.append(request['name'])
                logger.success(f"zip url {request['name']}")
        else:
            logger.warning(request)
        # print(f"URL: {request['url']}, Status: {request['status']}, Time: {request['time']}")

    with open('../test/api_urls.txt', 'a') as file:
        for url in api_urls:
            file.write(url + '\n')  # 将每个API地址写入txt文件中，每个地址占一行
            logger.info(url)
    return api_urls


if __name__ == '__main__':
    # spider_gif_url()
    # api_spider_link('https://sd.2021.host/artworks/115574488')
    fun_2('https://sd.2021.host/artworks/115574488')
