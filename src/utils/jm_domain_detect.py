import os
import sys
from pathlib import Path
from typing import Set, List, Optional
from pypinyin import Style, lazy_pinyin
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from file.file_process import get_image_keyword
from run import constants
from jmcomic import *
from utils.file_utils import move_folder_contents
from utils.wx_push import wx_push_content

option = JmOption.default()
meta_data = {}

@logger.catch
def get_domain_ls() -> Set[str]:
    """获取禁漫域名列表
    
    Returns:
        Set[str]: 域名集合
    """
    template = 'https://jmcmomic.github.io/go/{}.html'
    url_ls = [template.format(i) for i in range(300, 309)]
    domain_set: Set[str] = set()

    @logger.catch
    def fetch_domain(url: str) -> None:
        try:
            from curl_cffi import requests as postman
            text = postman.get(url, allow_redirects=False, **meta_data).text
            for domain in JmcomicText.analyse_jm_pub_html(text):
                if not domain.startswith('jm365.work'):
                    domain_set.add(domain)
        except Exception as e:
            logger.warning(f"获取域名失败: {e}")

    multi_thread_launcher(
        iter_objs=url_ls,
        apply_each_obj_func=fetch_domain,
    )
    return domain_set

domain_status_dict = {}

@logger.catch
def test_domain(domain: str) -> None:
    """测试域名是否可用
    
    Args:
        domain: 要测试的域名
    """
    client = option.new_jm_client(impl='html', domain_list=[domain], **meta_data)
    status = 'ok'

    try:
        client.get_album_detail('583946')
    except Exception as e:
        status = str(e.args)

    domain_status_dict[domain] = status

@logger.catch
def jm_domain_test() -> None:
    """测试所有域名并推送结果"""
    domain_set = get_domain_ls()
    logger.info(f'获取到{len(domain_set)}个域名，开始测试')

    multi_thread_launcher(
        iter_objs=domain_set,
        apply_each_obj_func=test_domain,
    )
    
    content = '\n'.join(f'{domain}: {status}' for domain, status in domain_status_dict.items())
    wx_push_content(content)
    
    for domain, status in domain_status_dict.items():
        logger.debug(f'{domain}: {status}')
        
    constants.jm_domain_detect_flag = False
    logger.success("域名检测完成")

@logger.catch
def get_page_content(client, keyword: str, page_num: int) -> Optional[JmSearchPage]:
    """根据搜索类型获取页面内容
    
    Args:
        client: JM客户端
        keyword: 搜索关键词
        page_num: 页码
        
    Returns:
        Optional[JmSearchPage]: 搜索结果页面,失败返回None
    """
    search_type = constants.search_content
    search_funcs = {
        'site': client.search_site,
        'work': client.search_work, 
        'author': client.search_author,
        'tag': client.search_tag,
        'actor': client.search_actor
    }
    
    if search_type not in search_funcs:
        logger.warning('未配置search_content参数')
        return None
        
    return search_funcs[search_type](search_query=keyword, page=page_num)

@logger.catch 
def search_content_jm(keyword: str, jm_id: Optional[str] = None) -> bool:
    """搜索内容
    
    Args:
        keyword: 搜索关键词
        jm_id: JM漫画ID
        
    Returns:
        bool: 是否搜索成功
    """
    logger.debug(f"开始搜索: {keyword}")
    client = JmOption.default().new_jm_client()

    page = get_page_content(client, keyword, 1)
    if not page:
        return False
        
    page_list = []
    page_count = page.page_count
    all_count = page.total
    
    logger.debug(f"找到{all_count}个结果,开始保存")
    
    for i in range(page_count):
        page = get_page_content(client, keyword, i)
        if page:
            page_list.append(page)

    for page_num, page in enumerate(page_list, 1):
        logger.debug(f"第{page_num}页搜索结果:")
        for album_id, title in page:
            logger.debug(f'[{album_id}]: {title}')

    if jm_id:
        page = client.search_site(search_query=jm_id)
        album: JmAlbumDetail = page.single_album
        logger.info(album.tags)
        
    return True

@logger.catch
def exists_jm_from_finish(content: str) -> bool:
    """检查是否已下载完成
    
    Args:
        content: 要检查的内容
        
    Returns:
        bool: 是否已下载
    """
    file_path = Path(constants.data_path) / "jm_download_finished_txt.txt"
    
    if not file_path.exists():
        file_path.write_text("", encoding='utf-8')
        return False
        
    txt_list = file_path.read_text(encoding='utf-8').splitlines()
    
    if content in txt_list:
        logger.warning(f"{content}已下载完成,跳过")
        return True
        
    return False

@logger.catch
def write_already_download_jm_finish(actor: str) -> None:
    """记录下载完成
    
    Args:
        actor: 要记录的内容
    """
    if exists_jm_from_finish(actor):
        return
        
    file_path = Path(constants.data_path) / "jm_download_finished_txt.txt"
    with file_path.open('a', encoding='utf-8') as f:
        f.write(f"{actor}\n")
        
    wx_push_content(f"{actor} 下载完成")
    logger.success(f"{actor}下载完成,已记录")

@logger.catch
def move_jm_keyword_dir(actor: str, a_title_list: List[str], jm_already_keyword: List[str], 
                       extra_path: Optional[str] = None) -> None:
    """移动文件到关键词目录
    
    Args:
        actor: 作者/关键词
        a_title_list: 标题列表
        jm_already_keyword: 已处理关键词列表
        extra_path: 额外路径
    """
    actor = ''.join(lazy_pinyin(actor, style=Style.TONE3))
    root_path = Path(constants.data_path) / "jm_image"
    root_path_jm = root_path.copy()
    
    if extra_path:
        root_path = root_path / extra_path
        root_path_jm = root_path_jm / extra_path
        
    actor_path = root_path / actor
    actor_path.mkdir(parents=True, exist_ok=True)
    
    for title in a_title_list:
        try:
            src_path = root_path_jm / title
            if str(src_path) in jm_already_keyword:
                continue
                
            target_path = actor_path / title
            move_folder_contents(str(src_path), str(target_path))
            
        except Exception as e:
            logger.warning(f"移动{title}失败: {e}")
            continue
            
    logger.debug(f"移动{actor}完成")

@logger.catch
def search_download_jm(actor: str) -> bool:
    """搜索并下载
    
    Args:
        actor: 搜索关键词
        
    Returns:
        bool: 是否成功
    """
    logger.debug(f"开始搜索: {actor}")

    jm_option = JmOption.default()
    client = jm_option.new_jm_client()

    page = get_page_content(client, actor, 1)
    if not page:
        return False
        
    page_list = []
    page_count = page.page_count
    all_count = page.total
    
    logger.debug(f"找到{all_count}个结果,开始保存")

    for i in range(page_count):
        page = get_page_content(client, actor, i)
        if page:
            page_list.append(page)
        if not constants.JM_SD_auto_flag:
            return False

    aid_list = []
    a_title_list = []
    
    for page_num, page in enumerate(page_list, 1):
        logger.debug(f"第{page_num}页搜索结果:")
        for aid, title, tag_list in page.iter_id_title_tag():
            logger.info(f'[角色/{actor}] 发现: [{aid}]: [{title}]')
            aid_list.append(aid)
            a_title_list.append(title)
            if not constants.JM_SD_auto_flag:
                return False
                
    logger.debug("开始下载")
    
    for i, (aid, title) in enumerate(zip(aid_list, a_title_list)):
        if search_local_jm_keyword(title):
            logger.warning(f"{title}已存在,跳过")
            continue
            
        try:
            download_album(aid, jm_option)
            logger.debug(f"下载完成: {aid}, {title}, {i+1}/{len(aid_list)}")
        except Exception as e:
            logger.warning(f"下载失败: {e}")
            
        if not constants.JM_SD_auto_flag:
            return False

    try:
        write_already_download_jm_finish(actor)
    except Exception as e:
        logger.warning(f"记录失败: {e}")
        
    return True

@logger.catch
def jm_auto_spider_img_thread() -> bool:
    """自动爬取线程"""
    logger.info("开始自动爬取...")
    
    spider_image_keyword, txt_file_list = get_image_keyword()
    
    if not spider_image_keyword:
        logger.warning("关键词为空,请添加关键词")
        return False

    for keyword_group in spider_image_keyword:
        logger.debug(f"当前关键词组: {keyword_group}")
        
        for keyword in keyword_group:
            keyword = keyword.strip()
            logger.debug(f"当前关键词: {keyword}")
            
            try:
                if exists_jm_from_finish(keyword):
                    logger.warning(f"{keyword}已下载,跳过")
                    continue
                    
                if not search_download_jm(keyword):
                    logger.success("停止爬取")
                    constants.JM_SD_auto_flag = False
                    return False
                    
            except Exception as e:
                logger.error(f"爬取失败: {e}")

    constants.JM_SD_auto_flag = False
    logger.success("全部下载完成")
    return True

@logger.catch
def search_local_jm_keyword(jm_title: str) -> bool:
    """检查本地是否存在
    
    Args:
        jm_title: 标题
        
    Returns:
        bool: 是否存在
    """
    jm_root_dir = Path(constants.data_path) / "jm_image"
    return any(jm_title in d.name for d in jm_root_dir.glob("**/*") if d.is_dir())

@logger.catch
def jm_move_category(actor: str, keyword_cat: str, jm_already_keyword: List[str]) -> bool:
    """移动到分类目录
    
    Args:
        actor: 作者/关键词
        keyword_cat: 分类关键词
        jm_already_keyword: 已处理关键词列表
        
    Returns:
        bool: 是否成功
    """
    if actor == keyword_cat:
        logger.debug(f"开始新分类: {actor}")
        return True

    logger.debug(f"开始分类: {actor}")

    jm_option = JmOption.default()
    client = jm_option.new_jm_client()

    page = client.search_site(actor, page=1)
    page_list = []
    page_count = page.page_count

    for i in range(page_count):
        page = client.search_site(search_query=actor, page=i)
        page_list.append(page)
        
    titles = []
    for page in page_list:
        titles.extend(title for _, title, _ in page.iter_id_title_tag())

    try:
        root_path = Path(constants.data_path) / "jm_image"
        for entry in root_path.iterdir():
            if keyword_cat in entry.name and entry.is_dir():
                move_jm_keyword_dir(actor, titles, jm_already_keyword, extra_path=entry.name)
    except Exception as e:
        logger.warning(f"移动失败: {e}")
        
    return True

@logger.catch
def process_jm_image_category() -> None:
    """处理图片分类"""
    category = ''
    jm_already_keyword = get_jm_already_image_keyword()
    
    categories = ['gi', 'sr', 'hk3rd', 'cbjq', 'blda']
    
    for keyword in jm_already_keyword:
        keyword = keyword.strip()
        if any(cat in keyword for cat in categories):
            category = keyword
            continue
            
        jm_move_category(keyword, category, jm_already_keyword)
        
    constants.process_jm_image_category_flag = False
    logger.success("分类处理完成")

@logger.catch
def get_jm_already_image_keyword() -> List[str]:
    """获取已处理关键词列表
    
    Returns:
        List[str]: 关键词列表
    """
    file_path = Path(constants.data_path) / 'jm_download_finished_txt.txt'
    
    if not file_path.exists():
        file_path.write_text("", encoding='utf-8')
        logger.warning(f"{file_path}不存在,已创建")
        return []
        
    try:
        return file_path.read_text(encoding='utf-8').splitlines()
    except Exception as e:
        logger.error(f"读取失败: {e}")
        return []
