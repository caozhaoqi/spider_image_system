#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Danbooru镜像站点采集器 - 优化版
支持多个镜像站点和数据源，无需API认证，内置丰富的中日作品名标签映射
支持飞书通知推送采集进度
"""

import os
import sys
import time
import random
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.append(str(Path(__file__).parent.parent))

# 加载飞书配置
# 当前文件路径: .../archived/spider_image_system/src/danbooru/danbooru_mirror_spider.py
# 目标配置文件: .../scripts/notification_config.json
# 需要向上5级到项目根目录
config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
    "scripts", "notification_config.json"
)
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        notification_config = json.load(f)
    
    # 设置飞书通知环境变量
    os.environ["NOTIFICATION_ENABLED"] = "true"
    os.environ["NOTIFICATION_PLATFORM"] = notification_config["platform"]
    os.environ["FEISHU_APP_ID"] = notification_config["feishu"]["app_id"]
    os.environ["FEISHU_APP_SECRET"] = notification_config["feishu"]["app_secret"]
    os.environ["FEISHU_RECEIVE_ID"] = notification_config["feishu"]["receive_id"]
    os.environ["FEISHU_RECEIVE_ID_TYPE"] = notification_config["feishu"]["receive_id_type"]
    logger.info(f"已加载通知配置: {config_path}")
else:
    logger.warning(f"未找到通知配置文件: {config_path}")

# 导入统一通知服务
try:
    # 添加项目根目录到sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from src.services.notification_service import get_notification_manager
    NOTIFICATION_AVAILABLE = True
except ImportError as e:
    NOTIFICATION_AVAILABLE = False
    logger.warning(f"通知服务未找到: {e}")

notification_manager = None

def init_notification():
    """初始化通知服务"""
    global notification_manager
    if NOTIFICATION_AVAILABLE:
        try:
            notification_manager = get_notification_manager()
            logger.info("通知服务初始化成功")
            return True
        except Exception as e:
            logger.warning(f"通知服务初始化失败: {e}")
            return False
    return False

def send_notification(message, title=None, level="info"):
    """发送通知"""
    if notification_manager:
        try:
            return notification_manager.send(message, title, level)
        except Exception as e:
            logger.warning(f"发送通知失败: {e}")
            return False
    return False


class DanbooruMirrorSpider:
    """支持镜像站点的Danbooru采集器"""
    
    # 支持的镜像站点列表
    MIRROR_SITES = {
        'danbooru': {
            'name': 'Danbooru官方',
            'api_url': 'https://danbooru.donmai.us/posts.json',
            'requires_auth': True,
            'rate_limit': 2,  # 每秒请求数
        },
        'safebooru': {
            'name': 'Safebooru',
            'api_url': 'https://safebooru.org/index.php?page=dapi&s=post&q=index',
            'requires_auth': False,
            'rate_limit': 1,
            'format': 'xml',
        },
        'gelbooru': {
            'name': 'Gelbooru',
            'api_url': 'https://gelbooru.com/index.php?page=dapi&s=post&q=index',
            'requires_auth': False,
            'rate_limit': 1,
            'format': 'xml',
        },
        'lolibooru': {
            'name': 'Lolibooru',
            'api_url': 'https://lolibooru.moe/post.json',
            'requires_auth': False,
            'rate_limit': 2,
            'format': 'json',
        },
        'yande.re': {
            'name': 'Yande.re',
            'api_url': 'https://yande.re/post.json',
            'requires_auth': False,
            'rate_limit': 2,
            'format': 'json',
        },
        'konachan': {
            'name': 'Konachan',
            'api_url': 'https://konachan.com/post.json',
            'requires_auth': False,
            'rate_limit': 2,
            'format': 'json',
        },
    }
    
    def __init__(self, site: str = 'lolibooru', username: str = None, api_key: str = None,
                 max_workers: int = 8, include_nsfw: bool = False):
        """
        初始化采集器
        
        Args:
            site: 站点名称，可选值: danbooru, safebooru, gelbooru, lolibooru, yande.re, konachan
            username: 用户名（仅danbooru需要）
            api_key: API密钥（仅danbooru需要）
            max_workers: 最大并发下载线程数
            include_nsfw: 是否包含非安全内容（默认False，只搜索安全内容）
        """
        self.site = site.lower()
        self.username = username
        self.api_key = api_key
        self.max_workers = max_workers
        self.include_nsfw = include_nsfw
        self._download_lock = threading.Lock()
        self._progress_counter = 0
        
        if self.site not in self.MIRROR_SITES:
            raise ValueError(f"不支持的站点: {site}。支持的站点: {list(self.MIRROR_SITES.keys())}")
        
        self.site_info = self.MIRROR_SITES[self.site]
        self.session = self._create_session()
        
        logger.info(f"使用采集站点: {self.site_info['name']}, 并发线程数: {max_workers}")
    
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/xml, */*',
        })
        
        # 如果需要认证
        if self.site_info['requires_auth'] and self.username and self.api_key:
            session.auth = (self.username, self.api_key)
        
        return session
    
    def search_posts(self, tags: str, page: int = 1, limit: int = 20) -> List[Dict]:
        """
        搜索帖子
        
        Args:
            tags: 搜索标签
            page: 页码
            limit: 每页数量
            
        Returns:
            List[Dict]: 帖子列表
        """
        site_info = self.site_info
        api_url = site_info['api_url']
        
        try:
            if site_info.get('format') == 'xml':
                # XML格式站点 (Safebooru, Gelbooru)
                params = {
                    'tags': tags,
                    'pid': page - 1,  # Safebooru使用pid从0开始
                    'limit': min(limit, 100),
                }
                response = self.session.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                return self._parse_xml_response(response.text)
            else:
                # JSON格式站点
                params = {
                    'tags': tags,
                    'page': page,
                    'limit': min(limit, 200),
                }
                response = self.session.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索失败 [{tags}] @ {self.site_info['name']}: {e}")
            return []
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict]:
        """解析XML响应为字典列表"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(xml_text)
            posts = []
            for post in root.findall('post'):
                post_dict = {}
                for attr in post.attrib:
                    post_dict[attr] = post.attrib[attr]
                posts.append(post_dict)
            return posts
        except Exception as e:
            logger.error(f"XML解析失败: {e}")
            return []
    
    def get_all_posts(self, tags: str, max_posts: int = 100) -> List[Dict]:
        """
        获取所有匹配的帖子
        
        Args:
            tags: 搜索标签
            max_posts: 最大获取数量
            
        Returns:
            List[Dict]: 帖子列表
        """
        all_posts = []
        page = 1
        limit = min(100, max_posts)
        
        while len(all_posts) < max_posts:
            posts = self.search_posts(tags, page, limit)
            
            if not posts:
                break
                
            for post in posts:
                if len(all_posts) >= max_posts:
                    break
                all_posts.append(post)
            
            page += 1
            # 添加延迟避免触发限流
            time.sleep(random.uniform(0.5, 1.5))
        
        logger.info(f"[{self.site_info['name']}] 搜索 '{tags}' 共找到 {len(all_posts)} 条结果")
        return all_posts
    
    def get_image_url(self, post: Dict) -> Optional[str]:
        """
        从帖子中提取图片URL
        
        Args:
            post: 帖子信息
            
        Returns:
            Optional[str]: 图片URL
        """
        # 不同站点的字段名可能不同
        url_fields = ['file_url', 'source', 'image', 'url']
        
        for field in url_fields:
            if field in post:
                url = post[field]
                # 处理相对URL
                if url and not url.startswith('http'):
                    url = f"https://{self.site}.donmai.us{url}" if self.site == 'danbooru' else url
                return url
        
        return None
    
    def download_image(self, post: Dict, save_dir: str) -> bool:
        """
        下载单张图片
        
        Args:
            post: 帖子信息
            save_dir: 保存目录
            
        Returns:
            bool: 是否下载成功
        """
        image_url = self.get_image_url(post)
        if not image_url:
            logger.warning("未找到图片URL")
            return False
        
        # 获取文件扩展名
        ext = image_url.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
            ext = 'jpg'
        
        # 生成文件名
        post_id = post.get('id', post.get('md5', f"unknown_{random.randint(1, 9999)}"))
        file_path = Path(save_dir) / f"{post_id}.{ext}"
        
        # 如果文件已存在则跳过
        if file_path.exists():
            logger.debug(f"文件已存在，跳过: {file_path.name}")
            return True
        
        try:
            response = self.session.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"下载成功: {file_path.name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"下载失败 [{image_url}]: {e}")
            return False
    
    def download_character_images(self, character_name: str, save_dir: str,
                                 max_count: int = 50, safe_only: bool = True) -> Tuple[int, int]:
        """
        下载指定角色的图片
        
        Args:
            character_name: 角色名（英文标签名）
            save_dir: 保存目录
            max_count: 最大下载数量
            safe_only: 是否只下载安全内容
            
        Returns:
            Tuple[int, int]: (成功数量, 失败数量)
        """
        # 构建搜索标签
        tag_name = character_name.lower().replace(' ', '_')
        tags = tag_name
        
        # 添加安全过滤（如果需要）
        if safe_only:
            if self.site == 'danbooru':
                tags += ' -rating:explicit -rating:questionable'
            elif self.site in ['safebooru', 'lolibooru']:
                # Safebooru和Lolibooru默认只返回安全内容
                pass
            else:
                # 默认添加安全内容限制，可通过参数关闭
                if hasattr(self, 'include_nsfw') and not self.include_nsfw:
                    tags += ' rating:safe'
        
        posts = self.get_all_posts(tags, max_count)
        
        if not posts:
            logger.warning(f"角色 '{character_name}' 未找到匹配的图片")
            return (0, 0)
        
        # 创建保存目录
        character_dir = Path(save_dir) / self._sanitize_filename(character_name)
        character_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        self._progress_counter = 0
        
        def download_with_progress(post_info: Tuple[int, Dict]) -> bool:
            """带进度显示的下载函数"""
            idx, post = post_info
            result = self.download_image(post, str(character_dir))
            with self._download_lock:
                self._progress_counter += 1
                if self._progress_counter % 5 == 0 or self._progress_counter == len(posts):
                    logger.info(f"下载 [{self._progress_counter}/{len(posts)}]: {character_name}")
            return result
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_with_progress, (i, post)) 
                      for i, post in enumerate(posts, 1)]
            
            for future in as_completed(futures):
                try:
                    if future.result():
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    logger.error(f"下载任务异常: {e}")
                    fail_count += 1
        
        logger.success(f"{character_name}: 成功 {success_count}, 失败 {fail_count}")
        return (success_count, fail_count)
    
    def download_multiple_characters(self, character_list: List[Tuple[str, str, str]], 
                                   save_dir: str, max_count_per_character: int = 50,
                                   start_from: int = 0, delay: float = 2.0) -> Dict[str, Tuple[int, int]]:
        """
        批量下载多个角色的图片
        
        Args:
            character_list: 角色列表，格式为[(中文名, 英文名, 作品名), ...]
            save_dir: 保存目录
            max_count_per_character: 每个角色最大下载数量
            start_from: 从第几个角色开始（用于断点续传）
            delay: 角色间请求间隔延迟（秒），避免触发限流
            
        Returns:
            Dict[str, Tuple[int, int]]: 每个角色的下载结果
        """
        results = {}
        total_success = 0
        total_fail = 0
        
        for i, (chinese_name, english_name, work_title) in enumerate(character_list[start_from:], start=start_from):
            # 构建完整的Danbooru标签
            danbooru_tag = format_danbooru_tag(english_name, work_title)
            logger.info(f"========== [{i+1}/{len(character_list)}] 正在处理角色: {chinese_name} ({danbooru_tag}) ==========")
            
            try:
                success, fail = self.download_character_images(
                    danbooru_tag, save_dir, max_count_per_character
                )
                results[chinese_name] = (success, fail)
                total_success += success
                total_fail += fail
                
                # 每10个角色发送一次进度通知
                if (i + 1) % 10 == 0 and notification_manager:
                    progress_msg = f"""**📊 采集进度更新**

**当前进度**: {i+1}/{len(character_list)} 个角色
**本批次**: {chinese_name} ✅ {success}张

**累计统计**:
- 成功: {total_success} 张
- 失败: {total_fail} 张

**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
                    send_notification(progress_msg, "采集进度", "info")
                    
            except Exception as e:
                logger.error(f"处理角色 {chinese_name} 时发生错误: {e}")
                results[chinese_name] = (0, 0)
            
            # 使用可配置的延迟
            time.sleep(random.uniform(delay * 0.5, delay * 1.5))
        
        return results
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        import re
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        sanitized = sanitized.strip().strip('_')
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized
    
    @classmethod
    def list_sites(cls):
        """列出所有支持的站点"""
        print("支持的镜像站点:")
        for key, info in cls.MIRROR_SITES.items():
            auth = "需要认证" if info['requires_auth'] else "无需认证"
            print(f"  {key}: {info['name']} ({auth})")


# 作品名到Danbooru标签的全面映射（包含中英文常见动漫电影作品对照）
WORK_TITLE_MAPPING = {
    # 游戏
    '蔚蓝档案': 'blue_archive',
    '原神': 'genshin_impact',
    '崩坏星穹铁道': 'honkai:_star_rail',
    '幻塔': 'tower_of_fantasy',
    '公主连结': 'princess_connect',
    '赛马娘': 'umamusume',
    '明日方舟': 'arknights',
    '碧蓝航线': 'azur_lane',
    'FGO': 'fate/grand_order',
    'Fate': 'fate',
    '偶像大师': 'idolmaster',
    'LoveLive': 'love_live',
    'BanG Dream': 'bang_dream',
    
    # 动漫电影与长篇经典
    '你的名字': 'kimi_no_na_wa.',
    '声之形': 'koe_no_katachi',
    '天气之子': 'tenki_no_ko',
    '铃芽之旅': 'suzume_no_tojimari',
    '五等分的新娘': '5-toubun_no_hanayome',
    '咒术回战': 'jujutsu_kaisen',
    '鬼灭之刃': 'kimetsu_no_yaiba',
    '间谍过家家': 'spy_x_family',
    '电锯人': 'chainsaw_man',
    '孤独摇滚': 'bocchi_the_rock!',
    '孤独摇滚!': 'bocchi_the_rock!',
    '莉可丽丝': 'lycoris_recoil',
    '无职转生': 'mushoku_tensei',
    '关于我转生变成史莱姆这档事': 'tensei_shitara_slime_datta_ken',
    '辉夜大小姐想让我告白': 'kaguya-sama_wa_kokurasetai',
    '知晓天空之蓝的人啊': 'sora_no_aosa_wo_shiru_hito_yo',
    '青春猪头少年不会梦到兔女郎学姐': 'seishun_buta_yarou_series',
    '刀剑神域': 'sword_art_online',
    '进击的巨人': 'shingeki_no_kyojin',
    '命运石之门': 'steins;gate',
    '从零开始的异世界生活': 're:zero_kara_hajimeru_isekai_seikatsu',
    '紫罗兰永恒花园': 'violet_evergarden',
    '轻音少女': 'k-on!',
    '未闻花名': 'ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.',
    '魔卡少女樱': 'cardcaptor_sakura',
    '魔法少女小圆': 'mahou_shoujo_madoka_magica',
    '东方Project': 'touhou',
}


def load_character_list(file_path: str) -> List[Tuple[str, str, str]]:
    """
    从文件加载角色列表
    
    Args:
        file_path: 角色列表文件路径
        
    Returns:
        List[Tuple[str, str, str]]: 角色列表[(中文名, 英文名, 作品名), ...]
    """
    character_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 3:
                        chinese_name = parts[0]
                        work_title = parts[1]
                        english_name = parts[2]
                        character_list.append((chinese_name, english_name, work_title))
        logger.success(f"从 {file_path} 加载了 {len(character_list)} 个角色")
    except FileNotFoundError:
        logger.error(f"角色列表文件不存在: {file_path}")
    except Exception as e:
        logger.error(f"加载角色列表失败: {e}")
    
    return character_list


def format_danbooru_tag(character_name: str, work_title: str) -> str:
    """
    格式化Danbooru标签
    
    Args:
        character_name: 角色英文名
        work_title: 作品名
        
    Returns:
        str: 格式化后的标签，如 arona_(blue_archive)
    """
    # 获取作品的Danbooru标签
    work_tag = WORK_TITLE_MAPPING.get(work_title, work_title.lower().replace(' ', '_'))
    
    # 构建完整标签
    if work_tag:
        return f"{character_name.lower().replace(' ', '_')}_({work_tag})"
    return character_name.lower().replace(' ', '_')


def main():
    import argparse
    
    # 初始化通知服务
    init_notification()
    
    parser = argparse.ArgumentParser(description='Danbooru镜像站点采集器')
    parser.add_argument('--site', type=str, default='yande.re',
                        help=f"镜像站点: {', '.join(DanbooruMirrorSpider.MIRROR_SITES.keys())}")
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role-new.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/danbooru_images',
                        help='图片保存目录')
    parser.add_argument('--max-count', type=int, default=100,
                        help='每个角色最大下载数量')
    parser.add_argument('--start-from', type=int, default=0,
                        help='从第几个角色开始')
    parser.add_argument('--username', type=str, default=None,
                        help='Danbooru用户名（仅danbooru站点需要）')
    parser.add_argument('--api-key', type=str, default=None,
                        help='Danbooru API密钥（仅danbooru站点需要）')
    parser.add_argument('--list-sites', action='store_true',
                        help='列出所有支持的站点')
    parser.add_argument('--workers', type=int, default=16,
                        help='并发下载线程数（默认16）')
    parser.add_argument('--tags-file', type=str, default=None,
                        help='直接使用Danbooru标签格式的角色列表文件（每行一个标签）')
    parser.add_argument('--include-nsfw', action='store_true',
                        help='是否包含非安全内容（扩大搜索范围）')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='请求间隔延迟（秒），避免触发限流，默认2.0秒')
    
    args = parser.parse_args()
    
    # 如果只是列出站点
    if args.list_sites:
        DanbooruMirrorSpider.list_sites()
        return
    
    # 创建采集器
    spider = DanbooruMirrorSpider(
        site=args.site,
        username=args.username,
        api_key=args.api_key,
        max_workers=args.workers,
        include_nsfw=args.include_nsfw
    )
    
    # 加载角色列表
    if args.tags_file:
        # 直接使用标签格式
        characters = []
        with open(args.tags_file, 'r', encoding='utf-8') as f:
            for line in f:
                tag = line.strip()
                if tag and not tag.startswith('#'):
                    characters.append((tag, tag, ''))  # (显示名, 标签, 作品)
        logger.success(f"从 {args.tags_file} 加载了 {len(characters)} 个标签")
    else:
        characters = load_character_list(args.character_file)
    
    if not characters:
        logger.error("未加载到角色列表")
        return
    
    # 创建输出目录
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # 显示加载的角色信息
    logger.info(f"加载的角色列表（前5个）:")
    for i, (chinese_name, english_name, work_title) in enumerate(characters[:5], 1):
        tag = format_danbooru_tag(english_name, work_title)
        logger.info(f"  {i}. {chinese_name} -> {tag}")
    
    # 发送开始通知
    start_message = f"""**🚀 角色图片采集任务开始**

**配置信息**:
- 采集站点: {spider.site_info['name']}
- 角色总数: {len(characters)}
- 每角色数量: {args.max_count}
- 并发线程: {args.workers}
- 请求延迟: {args.delay}秒

**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
    send_notification(start_message, "角色图片采集任务开始", "info")
    
    # 开始采集
    logger.info(f"========== 开始采集 {len(characters)} 个角色 (站点: {spider.site_info['name']}) ==========")
    results = spider.download_multiple_characters(
        characters, args.output_dir, args.max_count, args.start_from, args.delay
    )
    
    # 输出汇总
    logger.info("========== 采集完成 ==========")
    total_success = 0
    total_fail = 0
    
    for character, (success, fail) in results.items():
        logger.info(f"{character}: 成功 {success}, 失败 {fail}")
        total_success += success
        total_fail += fail
    
    logger.success(f"总计: 成功 {total_success}, 失败 {total_fail}")
    
    # 发送完成通知
    success_count = sum(1 for _, (s, f) in results.items() if s > 0)
    fail_count = len(results) - success_count
    
    complete_message = f"""**✅ 角色图片采集任务完成**

**统计信息**:
- 总角色数: {len(results)}
- 成功角色: {success_count}
- 失败角色: {fail_count}
- 总图片数: {total_success + total_fail}
- 成功图片: {total_success}
- 失败图片: {total_fail}

**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}"""
    send_notification(complete_message, "角色图片采集任务完成", "success")


if __name__ == '__main__':
    main()