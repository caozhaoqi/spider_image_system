import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from file.file_process import get_image_keyword
from run import constants
from jmcomic import *
from pypinyin import Style, lazy_pinyin
from utils.file_utils import move_folder_contents

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
def exists_jm_from_finish(content):
    """
    exists txt download finish image
    :param content:
    :return:
    """
    # txt_list = []
    file_name = os.path.join(constants.data_path, "jm_download_finished_txt.txt")
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8', errors='replace') as f:
            f.write("")
        return False
    with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
        txt_list = f.readlines()
    for txt in txt_list:
        if content in txt:
            logger.warning(f"{content} already download finished, will skip keyword!")
            return True


@logger.catch
def write_already_download_jm_finish(actor):
    """

    :param actor:
    :return:
    """
    if exists_jm_from_finish(actor):
        return True
    file_name = os.path.join(constants.data_path, "jm_download_finished_txt.txt")
    with open(file_name, 'a', encoding='utf-8', errors='replace') as f:
        f.write(actor + "\n")
    logger.success(f"Download {actor} finished, will write txt.")
    # pass


@logger.catch
def move_jm_keyword_dir(actor, a_title_list, jm_already_keyword, extra_path=None):
    """

    :param jm_already_keyword:
    :param extra_path:
    :param actor:
    :param a_title_list:
    :return:
    """
    actor = ''.join(lazy_pinyin(actor, style=Style.TONE3))
    root_path = os.path.join(constants.data_path, "jm_image")
    root_path_jm = os.path.join(constants.data_path, "jm_image")
    if extra_path:
        root_path = os.path.join(root_path, extra_path)
        root_path_jm = os.path.join(root_path_jm, extra_path)
    actor_path = os.path.join(root_path, actor)
    if not os.path.exists(actor_path):
        logger.warning(f"Keyword folder not exists, create {actor_path} it.")
        os.makedirs(actor_path)
    for actor_jm_content in a_title_list:
        try:
            src_path = os.path.join(root_path_jm, actor_jm_content)
            if src_path in jm_already_keyword:
                continue
            target_path = os.path.join(actor_path, actor_jm_content)
            move_folder_contents(src_path, target_path)
            #     continue
            # else:
            #     logger.success(f"Move name: {actor_jm_content} Success, move to {target_path}!")
        except Exception as e:
            logger.warning(f"Unknown error, detail: {e}, skip: {actor_jm_content}.")
            continue
    logger.debug(f"Moved keyword: {actor} Finish.")


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
        for aid, a_title, tag_list in page.iter_id_title_tag():  # 使用page的iter_id_title_tag迭代器
            # if actor in tag_list:
            logger.info(f'[角色/{actor}] 发现目标: [{aid}]: [{a_title}]')
            aid_list.append(aid)
            a_title_list.append(a_title)
            if not constants.JM_SD_auto_flag:
                return False
        page_num += 1
    logger.debug("Start download JM image.")
    download_jm_index = 0
    for aid_process in aid_list:
        if search_local_jm_keyword(a_title_list[download_jm_index]):
            logger.warning(f"Keyword JM image title: {a_title_list[download_jm_index]} exists, skip.")
            download_jm_index += 1
            continue
        else:
            try:
                download_album(aid_process, jm_option)
                logger.debug(f"Download jm image: {aid_process}, title: {a_title_list[download_jm_index]},"
                             f" download index: {download_jm_index + 1}, count: {len(aid_list)}, finish.")
                download_jm_index += 1
            except Exception as e:
                logger.warning(f"Unknown Error, detail: {e}")
        if not constants.JM_SD_auto_flag:
            return False
    # logger.success(f"Download JM keyword: {actor} image finish.")
    try:
        write_already_download_jm_finish(actor)
        # 处理文件至同一文件夹中
        # move_jm_keyword_dir(actor, a_title_list)
    except Exception as e:
        logger.warning(f"Unknown error, detail: {e}")
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
                if exists_jm_from_finish(spider_image_keyword_item.strip()):
                    logger.warning(f"Already download JM keyword, skip: {spider_image_keyword_item.strip()}")
                    continue
                else:
                    if not search_download_jm(spider_image_keyword_item.strip()):
                        logger.success("Stop jm spider finished")
                        constants.JM_SD_auto_flag = False
                        return False
            except Exception as e:
                logger.error(f"Unknown error, detail: {e}")
    constants.JM_SD_auto_flag = False
    logger.success(f"Download JM All image finish, set JM_SD_auto_flag = False.")


@logger.catch
def search_local_jm_keyword(jm_title):
    """
    filter exists keyword for jm
    :return: result
    """
    jm_root_dir = os.path.join(constants.data_path, "jm_image")
    for root, dirs, files in os.walk(jm_root_dir):
        for dir_name in dirs:
            if jm_title in dir_name:
                return True
    return False


@logger.catch
def jm_move_category(actor, keyword_cat, jm_already_keyword):
    """
    process  image category
    :param jm_already_keyword:
    :param keyword_cat:
    :param actor: actor
    :return: finish flag
    """
    logger.debug(f"Start category content: {actor}.")

    #     client = JmOption.default().new_jm_client()
    if actor is keyword_cat:
        logger.debug(f"start new category: {actor}")
        return

    jm_option = JmOption.default()
    client = jm_option.new_jm_client()

    page: JmSearchPage = client.search_site(actor, page=1)
    page_list = []
    page_count = page.page_count

    for i in range(page_count):
        page: JmSearchPage = client.search_site(search_query=actor, page=i)
        page_list.append(page)
    a_title_list = []
    page_num = 1
    for page in page_list:
        for aid, title, tag_list in page.iter_id_title_tag():  # 使用page的iter_id_title_tag迭代器
            a_title_list.append(title)
        page_num += 1
    try:
        root_path = os.path.join(constants.data_path, "jm_image")
        for entry in os.listdir(root_path):
            if keyword_cat in entry:
                # and entry not in jm_already_keyword:
                entry_path = os.path.join(root_path, entry)
                if os.path.isdir(entry_path):
                    move_jm_keyword_dir(actor, a_title_list,  jm_already_keyword, extra_path=entry)
    except Exception as e:
        logger.warning(f"Unknown error, detail: {e}")
    return True


@logger.catch
def process_jm_image_category():
    """

    :return
    """
    category = ''
    jm_already_keyword = get_jm_already_image_keyword()
    for jm_keyword_already_content in jm_already_keyword:
        if "gi" in jm_keyword_already_content or "sr" in jm_keyword_already_content \
                or "hk3rd" in jm_keyword_already_content or "cbjq" in jm_keyword_already_content or \
                "blda" in jm_keyword_already_content:
            category = jm_keyword_already_content.strip()
            continue
        jm_move_category(jm_keyword_already_content.strip(), category, jm_already_keyword)
    constants.process_jm_image_category_flag = False
    logger.success("Process ALL Image Success.")


@logger.catch
def get_jm_already_image_keyword():
    """
    get image keyword list
    :return:
    """
    auto_spider_file_path = constants.data_path

    if not os.path.exists(auto_spider_file_path):
        os.makedirs(auto_spider_file_path)

    file_name = 'jm_download_finished_txt.txt'
    full_file_path = os.path.join(auto_spider_file_path, file_name)
    if not os.path.exists(full_file_path):
        # 如果文件不存在，创建它
        with open(full_file_path, 'w', encoding='utf-8', errors='replace') as f:
            logger.warning(f"Current {full_file_path} not exists, will create demo txt!")
            return []
    try:
        # spider_image_keyword = []
        with open(full_file_path, 'r', encoding='utf-8', errors='replace') as f:
            spider_image_keyword = f.readlines()
        return spider_image_keyword
    except Exception as e:
        logger.error(f"Unknown error, detail {e}")
        return []
