#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safebooru 补充采集脚本 - 专注于使用 Safebooru 站点补充未采集的角色
所有图片链接记录到 SQLite 数据库以便追溯
"""

import os
import sys
import time
import random
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from src.danbooru.danbooru_mirror_spider import DanbooruMirrorSpider


# 作品名到Danbooru标签的映射
WORK_TITLE_MAPPING = {
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
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_english_name ON collected_images(english_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_site ON collected_images(site)')
    
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
        logger.debug(f"插入记录失败（可能重复）: {e}")


def update_character_stats(conn: sqlite3.Connection, chinese_name: str, english_name: str, 
                          work_title: str, success_count: int, fail_count: int, site: str):
    """更新角色统计"""
    cursor = conn.cursor()
    
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
            SET total_images = ?, success_count = ?, fail_count = ?, sites_used = ?, last_updated = CURRENT_TIMESTAMP
            WHERE english_name = ? AND work_title = ?
        ''', (total + success_count + fail_count, success + success_count, fail + fail_count, new_sites, english_name, work_title))
    else:
        cursor.execute('''
            INSERT INTO character_stats 
            (chinese_name, english_name, work_title, total_images, success_count, fail_count, sites_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (chinese_name, english_name, work_title, success_count + fail_count, success_count, fail_count, site))
    
    conn.commit()


def get_missing_characters(output_dir: str, character_list: List[Tuple[str, str, str]], min_images: int = 10) -> List[Tuple[str, str, str]]:
    """获取需要补充采集的角色"""
    missing = []
    output_path = Path(output_dir)
    
    for chinese_name, english_name, work_title in character_list:
        char_dir = output_path / english_name
        if char_dir.exists():
            jpg_count = len(list(char_dir.glob('*.jpg')))
            png_count = len(list(char_dir.glob('*.png')))
            total = jpg_count + png_count
            if total < min_images:
                missing.append((chinese_name, english_name, work_title))
        else:
            missing.append((chinese_name, english_name, work_title))
    
    return missing


def collect_character(conn: sqlite3.Connection, spider: DanbooruMirrorSpider, 
                     chinese_name: str, english_name: str, work_title: str, 
                     output_dir: str, target_count: int = 30) -> Tuple[int, int]:
    """采集单个角色"""
    tag = format_danbooru_tag(english_name, work_title)
    character_dir = Path(output_dir) / english_name
    character_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查现有图片数量
    existing_count = len(list(character_dir.glob('*.jpg'))) + len(list(character_dir.glob('*.png')))
    if existing_count >= target_count:
        logger.info(f"⏭️ {chinese_name} 已有 {existing_count} 张图片，跳过")
        return (0, 0)
    
    need_count = target_count - existing_count
    
    try:
        posts = spider.get_all_posts(tag, max_posts=need_count)
        
        if not posts:
            logger.warning(f"⚠️ {chinese_name} 未找到匹配图片")
            update_character_stats(conn, chinese_name, english_name, work_title, 0, 0, 'safebooru')
            return (0, 0)
        
        success_count = 0
        fail_count = 0
        
        for post in posts:
            image_url = spider.get_image_url(post)
            if not image_url:
                fail_count += 1
                continue
            
            ext = image_url.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                ext = 'jpg'
            
            post_id = post.get('id', f"unknown_{random.randint(1, 9999)}")
            file_path = character_dir / f"{post_id}.{ext}"
            
            if file_path.exists():
                # 文件已存在，记录到数据库但不重复下载
                insert_image_record(conn, {
                    'chinese_name': chinese_name,
                    'english_name': english_name,
                    'work_title': work_title,
                    'site': 'safebooru',
                    'image_url': image_url,
                    'local_path': str(file_path),
                    'post_id': post.get('id'),
                    'md5': post.get('md5')
                })
                success_count += 1
                continue
            
            try:
                response = spider.session.get(image_url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = file_path.stat().st_size
                
                # 记录到数据库
                insert_image_record(conn, {
                    'chinese_name': chinese_name,
                    'english_name': english_name,
                    'work_title': work_title,
                    'site': 'safebooru',
                    'image_url': image_url,
                    'local_path': str(file_path),
                    'post_id': post.get('id'),
                    'md5': post.get('md5'),
                    'file_size': file_size
                })
                
                success_count += 1
                logger.debug(f"下载成功: {file_path.name}")
                
            except Exception as e:
                logger.debug(f"下载失败 [{image_url}]: {e}")
                fail_count += 1
            
            # 下载间隔
            time.sleep(random.uniform(0.3, 0.8))
        
        update_character_stats(conn, chinese_name, english_name, work_title, success_count, fail_count, 'safebooru')
        
        if success_count > 0:
            logger.success(f"✅ {chinese_name}: 成功 {success_count} 张")
        elif fail_count > 0:
            logger.warning(f"⚠️ {chinese_name}: 全部失败 ({fail_count} 次尝试)")
        
        return (success_count, fail_count)
    
    except Exception as e:
        logger.error(f"采集 {chinese_name} 时发生错误: {e}")
        update_character_stats(conn, chinese_name, english_name, work_title, 0, 1, 'safebooru')
        return (0, 1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Safebooru补充采集脚本')
    parser.add_argument('--character-file', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role-new.txt',
                        help='角色列表文件路径')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/final_dataset',
                        help='图片保存目录')
    parser.add_argument('--db-path', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/collection.db',
                        help='数据库文件路径')
    parser.add_argument('--target-count', type=int, default=30,
                        help='每个角色目标图片数量')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='角色间延迟（秒）')
    
    args = parser.parse_args()
    
    # 初始化数据库
    conn = init_database(args.db_path)
    
    # 加载角色列表
    all_characters = load_character_list(args.character_file)
    
    # 获取需要补充的角色
    missing_characters = get_missing_characters(args.output_dir, all_characters, min_images=args.target_count)
    logger.info(f"需要补充采集的角色数: {len(missing_characters)}")
    
    if not missing_characters:
        logger.info("🎉 所有角色都已达到目标数量！")
        conn.close()
        return
    
    # 创建采集器
    spider = DanbooruMirrorSpider(site='safebooru', max_workers=4, include_nsfw=False)
    
    # 统计
    total_success = 0
    total_fail = 0
    new_characters = 0
    
    # 开始采集
    logger.info(f"========== 开始补充采集 {len(missing_characters)} 个角色 ==========")
    
    for i, (chinese_name, english_name, work_title) in enumerate(missing_characters, 1):
        logger.info(f"========== [{i}/{len(missing_characters)}] 正在处理: {chinese_name} ==========")
        
        success, fail = collect_character(conn, spider, chinese_name, english_name, 
                                         work_title, args.output_dir, args.target_count)
        
        total_success += success
        total_fail += fail
        
        if success > 0:
            new_characters += 1
        
        # 输出进度统计
        if i % 10 == 0:
            logger.info(f"📊 进度: {i}/{len(missing_characters)} | 新增角色: {new_characters} | 成功: {total_success} | 失败: {total_fail}")
        
        # 角色间延迟
        time.sleep(random.uniform(args.delay * 0.5, args.delay * 1.5))
    
    # 关闭数据库
    conn.close()
    
    # 最终统计
    logger.info("========== 补充采集完成 ==========")
    logger.info(f"📊 统计结果:")
    logger.info(f"   处理角色数: {len(missing_characters)}")
    logger.info(f"   成功采集角色: {new_characters}")
    logger.info(f"   成功下载图片: {total_success}")
    logger.info(f"   下载失败: {total_fail}")
    logger.info(f"   数据库: {args.db_path}")


if __name__ == '__main__':
    main()
