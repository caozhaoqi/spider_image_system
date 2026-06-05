#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Danbooru2024 数据集采集客户端

用于从Danbooru2024数据集中采集指定角色的图片
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from http_tools.http_request import download_file_fun


class DanbooruClient:
    """Danbooru2024数据集采集客户端"""
    
    def __init__(self, dataset_path: str = None):
        """
        初始化Danbooru客户端
        
        Args:
            dataset_path: Danbooru2024数据集路径，包含metadata.json和images目录
        """
        self.dataset_path = Path(dataset_path) if dataset_path else None
        self.metadata = None
        self.image_url_cache = {}
        
    def load_metadata(self, metadata_file: str = None) -> bool:
        """
        加载Danbooru数据集的metadata.json
        
        Args:
            metadata_file: metadata.json文件路径，默认为dataset_path/metadata.json
            
        Returns:
            bool: 是否加载成功
        """
        if metadata_file is None:
            if self.dataset_path is None:
                logger.error("未指定数据集路径或metadata文件")
                return False
            metadata_file = str(self.dataset_path / "metadata.json")
        
        try:
            logger.info(f"正在加载metadata: {metadata_file}")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.success(f"metadata加载成功，共 {len(self.metadata)} 条记录")
            return True
        except FileNotFoundError:
            logger.error(f"metadata文件不存在: {metadata_file}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"metadata解析失败: {e}")
            return False
        except Exception as e:
            logger.error(f"加载metadata时发生错误: {e}")
            return False
    
    def search_by_character(self, character_name: str, 
                           include_aliases: bool = True) -> List[Dict]:
        """
        根据角色名搜索图片
        
        Args:
            character_name: 角色名（支持中文、英文、日文罗马音）
            include_aliases: 是否包含别名匹配
            
        Returns:
            List[Dict]: 匹配的图片记录列表
        """
        if self.metadata is None:
            logger.error("请先加载metadata")
            return []
            
        results = []
        character_name_lower = character_name.lower().strip()
        
        for record in self.metadata:
            tags = record.get('tags', '')
            tags_lower = tags.lower()
            
            # 检查标签中是否包含角色名
            if character_name_lower in tags_lower:
                results.append(record)
                continue
                
            # 如果启用别名匹配，检查更多变体
            if include_aliases:
                # 检查是否有精确匹配的角色标签
                tag_list = tags.split()
                for tag in tag_list:
                    tag_lower = tag.lower()
                    # 精确匹配或包含匹配
                    if tag_lower == character_name_lower or \
                       character_name_lower in tag_lower or \
                       tag_lower in character_name_lower:
                        results.append(record)
                        break
        
        logger.info(f"搜索角色 '{character_name}' 找到 {len(results)} 张图片")
        return results
    
    def get_image_url(self, record: Dict) -> Optional[str]:
        """
        从记录中获取图片URL
        
        Args:
            record: 图片记录
            
        Returns:
            Optional[str]: 图片URL
        """
        # Danbooru2024的图片URL格式
        # 通常为: https://danbooru.donmai.us/data/<md5>.jpg
        md5 = record.get('md5')
        if md5:
            return f"https://danbooru.donmai.us/data/{md5}.jpg"
        return None
    
    def download_images(self, records: List[Dict], save_dir: str, 
                       max_count: int = 50, timeout: int = 30) -> Tuple[int, int]:
        """
        批量下载图片
        
        Args:
            records: 图片记录列表
            save_dir: 保存目录
            max_count: 最大下载数量
            timeout: 超时时间（秒）
            
        Returns:
            Tuple[int, int]: (成功下载数量, 失败数量)
        """
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        downloaded = set()
        
        for i, record in enumerate(records[:max_count], 1):
            image_url = self.get_image_url(record)
            if not image_url:
                fail_count += 1
                continue
                
            # 避免重复下载
            if image_url in downloaded:
                continue
            
            md5 = record.get('md5', f"unknown_{i}")
            file_path = Path(save_dir) / f"{md5}.jpg"
            
            logger.info(f"下载 [{i}/{min(max_count, len(records))}]: {image_url}")
            
            try:
                if download_file_fun(image_url, str(file_path)):
                    success_count += 1
                    downloaded.add(image_url)
                else:
                    fail_count += 1
            except Exception as e:
                logger.error(f"下载失败 {image_url}: {e}")
                fail_count += 1
        
        logger.success(f"下载完成: 成功 {success_count}, 失败 {fail_count}")
        return (success_count, fail_count)
    
    def download_character_images(self, character_name: str, save_dir: str,
                                 max_count: int = 50, include_aliases: bool = True) -> Tuple[int, int]:
        """
        下载指定角色的图片
        
        Args:
            character_name: 角色名
            save_dir: 保存目录
            max_count: 最大下载数量
            include_aliases: 是否包含别名匹配
            
        Returns:
            Tuple[int, int]: (成功下载数量, 失败数量)
        """
        records = self.search_by_character(character_name, include_aliases)
        
        if not records:
            logger.warning(f"角色 '{character_name}' 未找到匹配的图片")
            return (0, 0)
        
        character_save_dir = Path(save_dir) / self._sanitize_filename(character_name)
        return self.download_images(records, str(character_save_dir), max_count)
    
    def download_multiple_characters(self, character_list: List[str], save_dir: str,
                                   max_count_per_character: int = 50) -> Dict[str, Tuple[int, int]]:
        """
        批量下载多个角色的图片
        
        Args:
            character_list: 角色名列表
            save_dir: 保存目录
            max_count_per_character: 每个角色最大下载数量
            
        Returns:
            Dict[str, Tuple[int, int]]: 每个角色的下载结果
        """
        results = {}
        
        for character_name in character_list:
            logger.info(f"========== 正在处理角色: {character_name} ==========")
            success, fail = self.download_character_images(
                character_name, save_dir, max_count_per_character
            )
            results[character_name] = (success, fail)
        
        return results
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除非法字符
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # 移除首尾空格和下划线
        sanitized = sanitized.strip().strip('_')
        # 限制长度
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized


def load_character_list(file_path: str) -> List[str]:
    """
    从文件加载角色列表
    
    Args:
        file_path: 角色列表文件路径
        
    Returns:
        List[str]: 角色名列表
    """
    character_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取角色名（第一列）
                    parts = line.split()
                    if parts:
                        character_list.append(parts[0])
        logger.success(f"从 {file_path} 加载了 {len(character_list)} 个角色")
    except FileNotFoundError:
        logger.error(f"角色列表文件不存在: {file_path}")
    except Exception as e:
        logger.error(f"加载角色列表失败: {e}")
    
    return character_list


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Danbooru2024角色图片采集器')
    parser.add_argument('--metadata', type=str, help='metadata.json文件路径')
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/danbooru_images',
                        help='图片保存目录')
    parser.add_argument('--max-count', type=int, default=50,
                        help='每个角色最大下载数量')
    parser.add_argument('--characters', type=str, nargs='+',
                        help='指定要采集的角色（可选，不指定则采集全部）')
    
    args = parser.parse_args()
    
    # 创建客户端
    client = DanbooruClient()
    
    # 加载metadata
    if not client.load_metadata(args.metadata):
        return
    
    # 加载角色列表
    all_characters = load_character_list(args.character_file)
    
    # 如果指定了角色，则只处理这些角色
    if args.characters:
        target_characters = args.characters
    else:
        target_characters = all_characters
    
    # 开始采集
    logger.info(f"========== 开始采集 {len(target_characters)} 个角色 ==========")
    results = client.download_multiple_characters(
        target_characters, args.output_dir, args.max_count
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
