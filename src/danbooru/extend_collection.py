#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩充采集脚本 - 补充未采集到的角色并记录到数据库
"""

import os
import sys
import time
import random
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from src.danbooru.danbooru_mirror_spider import DanbooruMirrorSpider


def get_collected_characters(output_dir: str) -> set:
    """获取已采集的角色列表"""
    collected = set()
    output_path = Path(output_dir)
    if output_path.exists():
        for item in output_path.iterdir():
            if item.is_dir():
                collected.add(item.name)
    return collected


def load_character_list(file_path: str) -> List[Tuple[str, str, str]]:
    """加载角色列表"""
    characters = []
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
                        characters.append((chinese_name, english_name, work_title))
        logger.success(f"从 {file_path} 加载了 {len(characters)} 个角色")
    except Exception as e:
        logger.error(f"加载角色列表失败: {e}")
    return characters


# 作品名到Danbooru标签的映射
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
    # 动漫
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
    '莉可丽丝': 'lycoris_recoil',
    '无职转生': 'mushoku_tensei',
    '辉夜大小姐想让我告白': 'kaguya-sama_wa_kokurasetai',
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
    '天使降临我身边': 'watashi_ni_tenshi_ga_maiorita!',
    '龙王的工作': 'ryuoh_no_oshigoto!',
    '偶像荣耀': 'idoly_pride',
    '绝区零': 'zenless_zone_zero',
}

def format_danbooru_tag(character_name: str, work_title: str) -> str:
    """格式化Danbooru标签"""
    work_tag = WORK_TITLE_MAPPING.get(work_title, work_title.lower().replace(' ', '_'))
    return f"{character_name.lower().replace(' ', '_')}_({work_tag})"


def init_database(db_path: str) -> sqlite3.Connection:
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建图片记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collected_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese_name TEXT NOT NULL,
            english_name TEXT NOT NULL,
            work_title TEXT NOT NULL,
            site TEXT NOT NULL,
            image_url TEXT NOT NULL,
            local_path TEXT NOT NULL,
            post_id TEXT,
            md5 TEXT,
            file_size INTEGER,
            download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(image_url)
        )
    ''')
    
    # 创建角色统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese_name TEXT NOT NULL,
            english_name TEXT NOT NULL,
            work_title TEXT NOT NULL,
            total_images INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            sites_used TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(english_name, work_title)
        )
    ''')
    
    conn.commit()
    logger.info(f"数据库已初始化: {db_path}")
    return conn


def insert_image_record(conn: sqlite3.Connection, data: Dict):
    """插入图片记录"""
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO collected_images 
            (chinese_name, english_name, work_title, site, image_url, local_path, post_id, md5, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['chinese_name'],
            data['english_name'],
            data['work_title'],
            data['site'],
            data['image_url'],
            data['local_path'],
            data.get('post_id'),
            data.get('md5'),
            data.get('file_size')
        ))
        conn.commit()
    except Exception as e:
        logger.warning(f"插入记录失败: {e}")


def update_character_stats(conn: sqlite3.Connection, chinese_name: str, english_name: str, 
                          work_title: str, success_count: int, site: str):
    """更新角色统计"""
    cursor = conn.cursor()
    
    # 查询当前统计
    cursor.execute('''
        SELECT total_images, success_count, fail_count, sites_used 
        FROM character_stats 
        WHERE english_name = ? AND work_title = ?
    ''', (english_name, work_title))
    
    row = cursor.fetchone()
    
    if row:
        total, success, fail, sites = row
        new_sites = sites if sites else ""
        if site not in new_sites:
            new_sites = f"{new_sites},{site}" if new_sites else site
        
        cursor.execute('''
            UPDATE character_stats 
            SET total_images = ?, success_count = ?, sites_used = ?, last_updated = CURRENT_TIMESTAMP
            WHERE english_name = ? AND work_title = ?
        ''', (total + success_count, success + success_count, new_sites, english_name, work_title))
    else:
        cursor.execute('''
            INSERT INTO character_stats 
            (chinese_name, english_name, work_title, total_images, success_count, sites_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (chinese_name, english_name, work_title, success_count, success_count, site))
    
    conn.commit()


class ExtendedCollector:
    """扩展采集器"""
    
    def __init__(self, output_dir: str, db_path: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_conn = init_database(db_path)
        
        # 站点优先级排序
        self.sites = [
            ('lolibooru', 4),   # 专门收录萌系内容
            ('gelbooru', 3),    # 内容丰富
            ('konachan', 3),    # 高质量二次元图片
            ('yande.re', 2),    # 高质量但可能有限流
            ('safebooru', 1),   # 安全内容，作为最后尝试
        ]
        
        self.stats = {
            'total_collected': 0,
            'new_characters': 0,
            'total_images': 0
        }
    
    def download_from_site(self, site: str, tag: str, character_dir: Path) -> List[Dict]:
        """从指定站点下载图片"""
        results = []
        
        try:
            spider = DanbooruMirrorSpider(site=site, max_workers=4, include_nsfw=False)
            posts = spider.get_all_posts(tag, max_posts=30)
            
            if not posts:
                return results
            
            for post in posts:
                image_url = spider.get_image_url(post)
                if not image_url:
                    continue
                
                ext = image_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = 'jpg'
                
                post_id = post.get('id', f"unknown_{random.randint(1, 9999)}")
                file_path = character_dir / f"{post_id}.{ext}"
                
                if file_path.exists():
                    # 文件已存在，跳过但记录
                    results.append({
                        'url': image_url,
                        'path': str(file_path),
                        'post_id': post.get('id'),
                        'md5': post.get('md5'),
                        'exists': True
                    })
                    continue
                
                try:
                    response = spider.session.get(image_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = file_path.stat().st_size
                    results.append({
                        'url': image_url,
                        'path': str(file_path),
                        'post_id': post.get('id'),
                        'md5': post.get('md5'),
                        'file_size': file_size,
                        'exists': False
                    })
                    
                except Exception as e:
                    logger.debug(f"下载失败 [{image_url}]: {e}")
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.warning(f"站点 {site} 采集失败: {e}")
        
        return results
    
    def collect_character(self, chinese_name: str, english_name: str, work_title: str) -> int:
        """采集单个角色"""
        tag = format_danbooru_tag(english_name, work_title)
        character_dir = self.output_dir / english_name
        character_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查是否已有足够图片
        existing_count = len(list(character_dir.glob('*.jpg'))) + len(list(character_dir.glob('*.png')))
        if existing_count >= 30:
            logger.info(f"⏭️ {chinese_name} 已有 {existing_count} 张图片，跳过")
            return 0
        
        new_images = 0
        
        for site, priority in self.sites:
            if new_images >= 30:
                break
            
            logger.info(f"🔍 尝试从 {site} 采集 {chinese_name}...")
            results = self.download_from_site(site, tag, character_dir)
            
            for result in results:
                if not result.get('exists', False):
                    # 记录新图片到数据库
                    insert_image_record(self.db_conn, {
                        'chinese_name': chinese_name,
                        'english_name': english_name,
                        'work_title': work_title,
                        'site': site,
                        'image_url': result['url'],
                        'local_path': result['path'],
                        'post_id': result.get('post_id'),
                        'md5': result.get('md5'),
                        'file_size': result.get('file_size')
                    })
                    new_images += 1
            
            if new_images > 0:
                update_character_stats(self.db_conn, chinese_name, english_name, work_title, new_images, site)
                logger.success(f"✅ {chinese_name} 从 {site} 采集到 {new_images} 张图片")
                break
        
        return new_images
    
    def run(self, character_list: List[Tuple[str, str, str]]):
        """执行扩展采集"""
        logger.info(f"========== 开始扩展采集 {len(character_list)} 个角色 ==========")
        
        for i, (chinese_name, english_name, work_title) in enumerate(character_list, 1):
            logger.info(f"========== [{i}/{len(character_list)}] 正在处理: {chinese_name} ==========")
            
            new_count = self.collect_character(chinese_name, english_name, work_title)
            
            if new_count > 0:
                self.stats['new_characters'] += 1
                self.stats['total_images'] += new_count
            
            self.stats['total_collected'] += 1
            
            # 每处理10个角色输出一次统计
            if i % 10 == 0:
                logger.info(f"📊 进度: {i}/{len(character_list)} | 新增角色: {self.stats['new_characters']} | 新增图片: {self.stats['total_images']}")
        
        # 关闭数据库连接
        self.db_conn.close()
        
        logger.info("========== 扩展采集完成 ==========")
        logger.info(f"📊 统计结果:")
        logger.info(f"   处理角色数: {self.stats['total_collected']}")
        logger.info(f"   新增角色数: {self.stats['new_characters']}")
        logger.info(f"   新增图片数: {self.stats['total_images']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='扩展采集脚本 - 补充未采集到的角色')
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role-new.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/final_dataset',
                        help='图片保存目录')
    parser.add_argument('--db-path', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/collection.db',
                        help='数据库文件路径')
    
    args = parser.parse_args()
    
    # 获取已采集的角色
    collected = get_collected_characters(args.output_dir)
    logger.info(f"已采集角色数: {len(collected)}")
    
    # 加载所有角色
    all_characters = load_character_list(args.character_file)
    
    # 筛选未采集的角色
    missing_characters = []
    for chinese_name, english_name, work_title in all_characters:
        # 检查是否已采集（通过目录名判断）
        char_dir = Path(args.output_dir) / english_name
        if not char_dir.exists() or len(list(char_dir.glob('*.jpg'))) + len(list(char_dir.glob('*.png'))) < 10:
            missing_characters.append((chinese_name, english_name, work_title))
    
    logger.info(f"需要补充采集的角色数: {len(missing_characters)}")
    
    if not missing_characters:
        logger.info("🎉 所有角色都已采集完成！")
        return
    
    # 开始扩展采集
    collector = ExtendedCollector(args.output_dir, args.db_path)
    collector.run(missing_characters)


if __name__ == '__main__':
    main()
