import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from file.file_process import get_image_keyword
from run import constants
from jmcomic import *
option = JmOption.default()

meta_data = {
    # 'proxies': ProxyBuilder.clash_proxy()
}

# disable_jm_log()
from loguru import logger


@logger.catch
def get_domain_ls():
    """

    :return:
    """
    template = 'https://jmcmomic.github.io/go/{}.html'
    url_ls = [
        template.format(i)
        for i in range(300, 309)
    ]
    domain_set: Set[str] = set()

    @logger.catch
    def fetch_domain(url):
        """

        :param url:
        :return:
        """
        try:
            from curl_cffi import requests as postman
            text = postman.get(url, allow_redirects=False, **meta_data).text
            for domain in JmcomicText.analyse_jm_pub_html(text):
                if domain.startswith('jm365.work'):
                    continue
                domain_set.add(domain)
        except Exception as e:
            logger.warning(f"Unknown error, detail: {e}")

    multi_thread_launcher(
        iter_objs=url_ls,
        apply_each_obj_func=fetch_domain,
    )
    return domain_set


domain_status_dict = {}


@logger.catch
def test_domain(domain: str):
    """

    :param domain:
    :return:
    """
    client = option.new_jm_client(impl='html', domain_list=[domain], **meta_data)
    status = 'ok'

    try:
        client.get_album_detail('583946')
    except Exception as e:
        status = str(e.args)
        pass

    domain_status_dict[domain] = status


@logger.catch
def jm_domain_test():
    """

    :return:
    """
    domain_set = get_domain_ls()
    logger.info(f'获取到{len(domain_set)}个域名，开始测试')

    multi_thread_launcher(
        iter_objs=domain_set,
        apply_each_obj_func=test_domain,
    )

    for domain, status in domain_status_dict.items():
        logger.debug(f'{domain}: {status}')
    constants.jm_domain_detect_flag = False
    logger.success("Detect jm domain finish.")


@logger.catch
def search_content_jm(keyword, jm_id=None):
    """

    :param jm_id:
    :param keyword:
    :return: finish flag
    """
    # from jmcomic import *

    logger.debug(f"Start search content: {keyword}.")
    client = JmOption.default().new_jm_client()

    # 分页查询，search_site就是禁漫网页上的【站内搜索】

    page: JmSearchPage = client.search_site(search_query=keyword, page=1)
    page_list = []
    page_count = page.page_count
    all_count = page.total
    logger.debug(f"Spider JM image count: {all_count}, start save to list.")
    for i in range(page_count):
        page: JmSearchPage = client.search_site(search_query=keyword, page=i)
        page_list.append(page)
    # page默认的迭代方式是page.iter_id_title()，每次迭代返回 albun_id, title
    page_num = 1
    for page in page_list:
        logger.debug(f"Page num: {page_num}, spider image.")
        for album_id, title in page:
            logger.debug(f'[{album_id}]: {title}')
        page_num += 1

    if jm_id:
        # 直接搜索禁漫车号
        page = client.search_site(search_query=jm_id)
        album: JmAlbumDetail = page.single_album
        logger.info(album.tags)
    return True


@logger.catch
def search_download_jm(actor):
    """

    :param actor: actor
    :return: finish flag
    """
    logger.debug(f"Start search content: {actor}.")

    #     client = JmOption.default().new_jm_client()
    jm_option = JmOption.default()
    client = jm_option.new_jm_client()

    # tag = '無修正'
    # 搜索标签，可以使用search_tag。
    # 搜索第一页。
    page: JmSearchPage = client.search_site(actor, page=1)
    page_list = []
    page_count = page.page_count
    all_count = page.total
    logger.debug(f"Spider JM image count: {all_count}, start save to list.")

    for i in range(page_count):
        page: JmSearchPage = client.search_site(search_query=actor, page=i)
        page_list.append(page)
        if not constants.JM_SD_auto_flag:
            return False

    aid_list = []
    a_title_list = []
    page_num = 1
    for page in page_list:
        logger.debug(f"Page num: {page_num}, spider image.")
        for aid, atitle, tag_list in page.iter_id_title_tag():  # 使用page的iter_id_title_tag迭代器
            # if actor in tag_list:
            logger.info(f'[角色/{actor}] 发现目标: [{aid}]: [{atitle}]')
            aid_list.append(aid)
            a_title_list.append(atitle)
            if not constants.JM_SD_auto_flag:
                return False
        page_num += 1
    logger.debug("Start download JM image.")
    download_jm_index = 0
    for aid_process in aid_list:
        # result[aid_process].
        download_album(aid_process, jm_option)
        logger.debug(f"Download jm image: {aid_process}, title: {a_title_list[download_jm_index]},"
                     f" download index: {download_jm_index + 1}, count: {len(aid_list)}, finish.")
        download_jm_index += 1
        if not constants.JM_SD_auto_flag:
            return False
    logger.success(f"Download JM keyword: {actor} image finish.")
    return True


@logger.catch
def jm_auto_spider_img_thread():
    """
    auto spider img thread
    @:param self.
    :return:
    """
    logger.info("Auto spider JM img thread starting...")
    # detect spider work status spider image threading
    # if constants.log_no_output_flag and not constants.JM_SD_auto_flag:
    #     constants.stop_auto_jm_flag = False
    spider_image_keyword, txt_file_list = get_image_keyword()
    if len(spider_image_keyword) == 0 or spider_image_keyword == [] or spider_image_keyword == [[]]:
        logger.warning("Auto spider image null, please add keyword!")
        # if self:
        #     self.sys_tips("Notice: spider_img_keyword.txt文件为空, 请先点击图像->关键字中添加关键字！")
        return False
    # constants.spider_mode = 'auto'
    txt_index = 0
    for spider_img_keyword_detail in spider_image_keyword:
        logger.debug("Current spider kew word txt: " + str(spider_img_keyword_detail))
        # 读取用户输入路径
        # constants.stop_auto_jm_flag = False
        txt_index += 1
        for spider_image_keyword_item in spider_img_keyword_detail:
            logger.debug("Current spider kew word: " + str(spider_image_keyword_item.strip()))
            try:
                search_download_jm(spider_image_keyword_item.strip())
                if not constants.JM_SD_auto_flag:
                    # logger.warning("stop jm spider.")
                    return False
            except Exception as e:
                logger.error(f"Unknown error, detail: {e}")
    constants.JM_SD_auto_flag = False
    logger.success(f"Download JM All image finish, set JM_SD_auto_flag=False.")


if __name__ == '__main__':
    """
    test use
    """
    search_download_jm("芙宁娜")
