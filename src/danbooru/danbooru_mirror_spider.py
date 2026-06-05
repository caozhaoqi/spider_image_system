#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Danbooru镜像站点采集器

支持多个镜像站点和数据源，无需API认证
"""

import os
import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.append(str(Path(__file__).parent.parent))


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
                 max_workers: int = 8):
        """
        初始化采集器
        
        Args:
            site: 站点名称，可选值: danbooru, safebooru, gelbooru, lolibooru, yande.re, konachan
            username: 用户名（仅danbooru需要）
            api_key: API密钥（仅danbooru需要）
            max_workers: 最大并发下载线程数
        """
        self.site = site.lower()
        self.username = username
        self.api_key = api_key
        self.max_workers = max_workers
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
                                   start_from: int = 0) -> Dict[str, Tuple[int, int]]:
        """
        批量下载多个角色的图片
        
        Args:
            character_list: 角色列表，格式为[(中文名, 英文名, 作品名), ...]
            save_dir: 保存目录
            max_count_per_character: 每个角色最大下载数量
            start_from: 从第几个角色开始（用于断点续传）
            
        Returns:
            Dict[str, Tuple[int, int]]: 每个角色的下载结果
        """
        results = {}
        
        for i, (chinese_name, english_name, work_title) in enumerate(character_list[start_from:], start=start_from):
            # 构建完整的Danbooru标签
            danbooru_tag = format_danbooru_tag(english_name, work_title)
            logger.info(f"========== [{i+1}/{len(character_list)}] 正在处理角色: {chinese_name} ({danbooru_tag}) ==========")
            
            try:
                success, fail = self.download_character_images(
                    danbooru_tag, save_dir, max_count_per_character
                )
                results[chinese_name] = (success, fail)
            except Exception as e:
                logger.error(f"处理角色 {chinese_name} 时发生错误: {e}")
                results[chinese_name] = (0, 0)
            
            time.sleep(random.uniform(1, 2))
        
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


# 作品名到Danbooru标签的映射
WORK_TITLE_MAPPING = {
    '蔚蓝档案': 'blue_archive',
    '原神': 'genshin_impact',
    '崩坏星穹铁道': 'honkai:_star_rail',
    '幻塔': 'tower_of_fantasy',
    '东方Project': 'touhou',
    '偶像大师': 'idolmaster',
    'LoveLive': 'love_live',
    'BanG Dream': 'bang_dream',
    '公主连结': 'princess_connect',
    '赛马娘': 'umamusume',
    'Fate': 'fate',
    '明日方舟': 'arknights',
    '碧蓝航线': 'azur_lane',
    'FGO': 'fate/grand_order',
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
    
    parser = argparse.ArgumentParser(description='Danbooru镜像站点采集器')
    parser.add_argument('--site', type=str, default='yande.re',
                        help=f"镜像站点: {', '.join(DanbooruMirrorSpider.MIRROR_SITES.keys())}")
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/danbooru_images',
                        help='图片保存目录')
    parser.add_argument('--max-count', type=int, default=50,
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
        max_workers=args.workers
    )
    
    # 加载角色列表
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
    
    # 开始采集
    logger.info(f"========== 开始采集 {len(characters)} 个角色 (站点: {spider.site_info['name']}) ==========")
    results = spider.download_multiple_characters(
        characters, args.output_dir, args.max_count, args.start_from
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


if __name__ == '__main__':
    main()
