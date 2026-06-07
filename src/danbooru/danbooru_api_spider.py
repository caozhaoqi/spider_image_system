#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Danbooru API 采集器

通过Danbooru官方API采集指定角色的图片
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
import requests

sys.path.append(str(Path(__file__).parent.parent))




class DanbooruApiSpider:
    """Danbooru API采集器"""
    
    BASE_URL = "https://danbooru.donmai.us"
    API_URL = "https://danbooru.donmai.us/posts.json"
    
    def __init__(self, username: str = None, api_key: str = None):
        """
        初始化采集器
        
        Args:
            username: Danbooru用户名（可选，用于提高API限制）
            api_key: Danbooru API密钥（可选）
        """
        self.username = username
        self.api_key = api_key
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        })
        
        if self.username and self.api_key:
            session.auth = (self.username, self.api_key)
        
        return session
    
    def search_posts(self, tags: str, page: int = 1, limit: int = 20) -> List[Dict]:
        """
        搜索帖子
        
        Args:
            tags: 搜索标签
            page: 页码
            limit: 每页数量（最大200）
            
        Returns:
            List[Dict]: 帖子列表
        """
        limit = min(limit, 200)
        
        params = {
            'tags': tags,
            'page': page,
            'limit': limit,
        }
        
        try:
            response = self.session.get(self.API_URL, params=params, timeout=30)
            
            if response.status_code == 403:
                logger.error(f"搜索失败 [{tags}]: 403 Forbidden - Danbooru API需要认证。请提供username和api_key参数。")
                logger.info("获取API密钥方法: 登录Danbooru -> 设置 -> API Access -> API Key")
                return []
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索失败 [{tags}]: {e}")
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
        limit = min(200, max_posts)
        
        while len(all_posts) < max_posts:
            posts = self.search_posts(tags, page, limit)
            
            if not posts:
                break
                
            for post in posts:
                if len(all_posts) >= max_posts:
                    break
                all_posts.append(post)
            
            page += 1
            # 添加随机延迟避免触发限流
            time.sleep(random.uniform(0.5, 1.5))
        
        logger.info(f"搜索 '{tags}' 共找到 {len(all_posts)} 条结果")
        return all_posts
    
    def download_image(self, post: Dict, save_dir: str) -> bool:
        """
        下载单张图片
        
        Args:
            post: 帖子信息
            save_dir: 保存目录
            
        Returns:
            bool: 是否下载成功
        """
        # 优先使用原图URL
        image_url = post.get('file_url')
        
        if not image_url:
            # 备选：使用预览图
            image_url = post.get('large_file_url') or post.get('preview_file_url')
            
        if not image_url:
            logger.warning("未找到图片URL")
            return False
        
        # 获取文件扩展名
        ext = image_url.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
            ext = 'jpg'
        
        # 使用md5作为文件名
        md5 = post.get('md5', f"unknown_{post.get('id', '0')}")
        file_path = Path(save_dir) / f"{md5}.{ext}"
        
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
                                 max_count: int = 50) -> Tuple[int, int]:
        """
        下载指定角色的图片
        
        Args:
            character_name: 角色名（英文标签名）
            save_dir: 保存目录
            max_count: 最大下载数量
            
        Returns:
            Tuple[int, int]: (成功数量, 失败数量)
        """
        # Danbooru使用下划线分隔的标签格式
        tag_name = character_name.lower().replace(' ', '_')
        
        # 构建搜索标签：角色标签 + 排除不安全内容
        tags = f"{tag_name} -rating:explicit -rating:questionable"
        
        posts = self.get_all_posts(tags, max_count)
        
        if not posts:
            logger.warning(f"角色 '{character_name}' 未找到匹配的图片")
            return (0, 0)
        
        # 创建保存目录
        character_dir = Path(save_dir) / self._sanitize_filename(character_name)
        character_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        
        for i, post in enumerate(posts, 1):
            logger.info(f"下载 [{i}/{len(posts)}]: {character_name}")
            
            if self.download_image(post, str(character_dir)):
                success_count += 1
            else:
                fail_count += 1
            
            # 添加延迟
            time.sleep(random.uniform(0.3, 0.8))
        
        logger.success(f"{character_name}: 成功 {success_count}, 失败 {fail_count}")
        return (success_count, fail_count)
    
    def download_multiple_characters(self, character_list: List[Tuple[str, str]], 
                                   save_dir: str, max_count_per_character: int = 50,
                                   start_from: int = 0) -> Dict[str, Tuple[int, int]]:
        """
        批量下载多个角色的图片
        
        Args:
            character_list: 角色列表，格式为[(中文名, 英文名), ...]
            save_dir: 保存目录
            max_count_per_character: 每个角色最大下载数量
            start_from: 从第几个角色开始（用于断点续传）
            
        Returns:
            Dict[str, Tuple[int, int]]: 每个角色的下载结果
        """
        results = {}
        
        for i, (chinese_name, english_name) in enumerate(character_list[start_from:], start=start_from):
            logger.info(f"========== [{i+1}/{len(character_list)}] 正在处理角色: {chinese_name} ({english_name}) ==========")
            
            try:
                success, fail = self.download_character_images(
                    english_name, save_dir, max_count_per_character
                )
                results[chinese_name] = (success, fail)
            except Exception as e:
                logger.error(f"处理角色 {chinese_name} 时发生错误: {e}")
                results[chinese_name] = (0, 0)
            
            # 每个角色之间添加更长的延迟
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


def load_character_list(file_path: str) -> List[Tuple[str, str]]:
    """
    从文件加载角色列表
    
    文件格式: 中文名 作品名 英文名 日文名
    
    Args:
        file_path: 角色列表文件路径
        
    Returns:
        List[Tuple[str, str]]: 角色列表[(中文名, 英文名), ...]
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
                        english_name = parts[2]  # 第三列是英文名
                        character_list.append((chinese_name, english_name))
        logger.success(f"从 {file_path} 加载了 {len(character_list)} 个角色")
    except FileNotFoundError:
        logger.error(f"角色列表文件不存在: {file_path}")
    except Exception as e:
        logger.error(f"加载角色列表失败: {e}")
    
    return character_list


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Danbooru API角色图片采集器')
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role-new.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/danbooru_images',
                        help='图片保存目录')
    parser.add_argument('--max-count', type=int, default=50,
                        help='每个角色最大下载数量')
    parser.add_argument('--start-from', type=int, default=0,
                        help='从第几个角色开始（用于断点续传）')
    parser.add_argument('--username', type=str, default=None,
                        help='Danbooru用户名（可选）')
    parser.add_argument('--api-key', type=str, default=None,
                        help='Danbooru API密钥（可选）')
    
    args = parser.parse_args()
    
    # 创建采集器
    spider = DanbooruApiSpider(username=args.username, api_key=args.api_key)
    
    # 加载角色列表
    characters = load_character_list(args.character_file)
    
    if not characters:
        logger.error("未加载到角色列表")
        return
    
    # 创建输出目录
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # 开始采集
    logger.info(f"========== 开始采集 {len(characters)} 个角色 ==========")
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
