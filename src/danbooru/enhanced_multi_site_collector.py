#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版多站点采集器 - 扩展支持更多站点
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


# 扩展的作品名到Danbooru标签的映射
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
    '少女前线2：追放': 'girls_frontline_2:_exilium',
    '少女前线': 'girls_frontline',
    '绝区零': 'zenless_zone_zero',
    '鸣潮': 'wuthering_waves',
    '异环': 'extraordinary_ones',
    '阴阳师': 'onmyoji',
    
    # 动漫
    '天使降临我身边': 'watashi_ni_tenshi_ga_maiorita!',
    '龙王的工作': 'ryuoh_no_oshigoto!',
    '请问您今天要来点兔子吗': 'gochuumon_wa_usagi_desu_ka?',
    '小林家的龙女仆': 'kobayashi-san_chi_no_maidragon',
    '干物妹小埋': 'himouto!_umaru-chan',
    '埃罗芒阿老师': 'eromanga_sensei',
    'Re:从零开始的异世界生活': 're:zero_kara_hajimeru_isekai_seikatsu',
    '约会大作战': 'date_a_live',
    '魔法少女小圆': 'mahou_shoujo_madoka_magica',
    '东方Project': 'touhou',
    '物语系列': 'monogatari_series',
    '为美好的世界献上祝福': 'kono_subarashii_sekai_ni_shukufuku_wo!',
    '间谍过家家': 'spy_x_family',
    '幸运星': 'lucky_star',
    '悠哉日常大王': 'non_non_biyori',
    '工作细胞': 'hataraku_saibou',
    '声之形': 'koe_no_katachi',
    '你的名字': 'kimi_no_na_wa.',
    'Love': 'love_live',
    'Hololive': 'hololive',
    'Fate/kaleid': 'fate/kaleid_liner_prisma_illya',
    '偶像荣耀': 'idoly_pride',
    '明日方舟终末地': 'arknights:_endfield',
}


# 扩展的站点列表（按优先级排序）
EXTENDED_SITES = [
    # 安全站点（无NSFW内容）
    {'name': 'safebooru', 'label': 'Safebooru', 'safe_only': True},
    {'name': 'lolibooru', 'label': 'Lolibooru', 'safe_only': True},
    {'name': 'konachan', 'label': 'Konachan', 'safe_only': True},
    
    # 混合站点（包含NSFW）
    {'name': 'gelbooru', 'label': 'Gelbooru', 'safe_only': False},
    {'name': 'yande.re', 'label': 'Yande.re', 'safe_only': False},
]


# 特殊角色名映射（处理多词英文名）
# Danbooru标签格式: 姓氏_名字_(作品)
SPECIAL_CHARACTER_MAPPING = {
    ('胡桃', '原神'): 'hu_tao',
    ('符玄', '崩坏星穹铁道'): 'fu_xuan',
    ('三月七', '崩坏星穹铁道'): 'march_7th',
    ('银狼', '崩坏星穹铁道'): 'silver_wolf',
    ('砂狼白子', '蔚蓝档案'): 'sunaookami_shiroko',
    ('阿慈谷日富美', '蔚蓝档案'): 'ajitani_hifumi',
    ('十六夜野乃美', '蔚蓝档案'): 'izayoi_nonomi',
    ('黑馆羽留奈', '蔚蓝档案'): 'kurodate_haruna',
    ('天雨亚子', '蔚蓝档案'): 'amau_ako',
    ('陆八魔爱露', '蔚蓝档案'): 'rikuhachima_aru',
    ('浅黄睦月', '蔚蓝档案'): 'asagi_mutsuki',
    ('鬼方佳代子', '蔚蓝档案'): 'onikata_kayoko',
    ('狐坂若藻', '蔚蓝档案'): 'kosaka_wakamo',
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
                        # 处理包含空格的英文名
                        # 尝试查找特殊映射
                        key = (chinese_name, work_title)
                        if key in SPECIAL_CHARACTER_MAPPING:
                            english_name = SPECIAL_CHARACTER_MAPPING[key]
                        else:
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
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_work ON character_stats(work_title)')
    
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


def get_missing_characters(output_dir: str, character_list: List[Tuple[str, str, str]], 
                          conn: sqlite3.Connection, min_images: int = 30) -> List[Tuple[str, str, str]]:
    """获取需要补充采集的角色"""
    missing = []
    output_path = Path(output_dir)
    
    cursor = conn.cursor()
    
    for chinese_name, english_name, work_title in character_list:
        # 检查数据库中已采集数量
        cursor.execute('''
            SELECT COUNT(*) FROM collected_images 
            WHERE english_name = ? AND work_title = ?
        ''', (english_name, work_title))
        db_count = cursor.fetchone()[0]
        
        # 检查文件系统中已存在的图片数量
        char_dir = output_path / english_name
        fs_count = 0
        if char_dir.exists():
            fs_count = len(list(char_dir.glob('*.jpg'))) + len(list(char_dir.glob('*.png'))) + len(list(char_dir.glob('*.jpeg')))
        
        # 取较大值作为已采集数量
        existing_count = max(db_count, fs_count)
        
        if existing_count < min_images:
            missing.append((chinese_name, english_name, work_title))
            logger.debug(f"需要补充: {chinese_name} (已有 {existing_count}/{min_images})")
    
    return missing


def collect_from_site(conn: sqlite3.Connection, spider: DanbooruMirrorSpider,
                      chinese_name: str, english_name: str, work_title: str,
                      output_dir: str, need_count: int) -> Tuple[int, int]:
    """从单个站点采集角色"""
    tag = format_danbooru_tag(english_name, work_title)
    character_dir = Path(output_dir) / english_name
    character_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    try:
        posts = spider.get_all_posts(tag, max_posts=need_count * 2)  # 获取双倍数量以应对下载失败
        
        if not posts:
            logger.debug(f"[{spider.site_info['name']}] 未找到 {chinese_name} 的图片")
            return (0, 0)
        
        for post in posts[:need_count * 2]:
            if success_count >= need_count:
                break
                
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
                    'site': spider.site,
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
                    'site': spider.site,
                    'image_url': image_url,
                    'local_path': str(file_path),
                    'post_id': post.get('id'),
                    'md5': post.get('md5'),
                    'file_size': file_size
                })
                
                success_count += 1
                logger.debug(f"[{spider.site_info['name']}] 下载成功: {file_path.name}")
                
            except Exception as e:
                logger.debug(f"[{spider.site_info['name']}] 下载失败 [{image_url}]: {e}")
                fail_count += 1
            
            # 下载间隔
            time.sleep(random.uniform(0.3, 0.8))
        
        return (success_count, fail_count)
    
    except Exception as e:
        logger.error(f"[{spider.site_info['name']}] 采集 {chinese_name} 时发生错误: {e}")
        return (0, 1)


def collect_character(conn: sqlite3.Connection, chinese_name: str, english_name: str, 
                     work_title: str, output_dir: str, target_count: int = 30):
    """多站点采集单个角色"""
    character_dir = Path(output_dir) / english_name
    character_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查现有图片数量
    existing_count = len(list(character_dir.glob('*.jpg'))) + len(list(character_dir.glob('*.png'))) + len(list(character_dir.glob('*.jpeg')))
    if existing_count >= target_count:
        logger.info(f"⏭️ {chinese_name} 已有 {existing_count} 张图片，跳过")
        return
    
    need_count = target_count - existing_count
    total_success = 0
    total_fail = 0
    sites_attempted = []
    
    logger.info(f"🎯 {chinese_name}: 需要补充 {need_count} 张图片")
    
    # 按优先级尝试各站点
    for site_info in EXTENDED_SITES:
        if total_success >= need_count:
            break
            
        site_name = site_info['name']
        site_label = site_info['label']
        
        try:
            logger.info(f"🔍 尝试从 {site_label} 采集 {chinese_name}...")
            
            spider = DanbooruMirrorSpider(site=site_name, max_workers=4, include_nsfw=False)
            success, fail = collect_from_site(conn, spider, chinese_name, english_name, 
                                           work_title, output_dir, need_count - total_success)
            
            total_success += success
            total_fail += fail
            sites_attempted.append(site_name)
            
            if success > 0:
                update_character_stats(conn, chinese_name, english_name, work_title, success, fail, site_name)
            
            # 站点间延迟
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as e:
            logger.warning(f"⚠️ 从 {site_label} 采集失败: {e}")
            continue
    
    if total_success > 0:
        logger.success(f"✅ {chinese_name}: 成功采集 {total_success} 张（来自 {len(sites_attempted)} 个站点）")
    else:
        logger.warning(f"❌ {chinese_name}: 所有站点均未采集到图片")
        update_character_stats(conn, chinese_name, english_name, work_title, 0, 1, ",".join(sites_attempted))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='增强版多站点采集器')
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
    parser.add_argument('--delay', type=float, default=5.0,
                        help='角色间延迟（秒）')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # 初始化数据库
    conn = init_database(args.db_path)
    
    # 加载角色列表
    all_characters = load_character_list(args.character_file)
    
    # 获取需要补充的角色
    missing_characters = get_missing_characters(args.output_dir, all_characters, conn, min_images=args.target_count)
    logger.info(f"需要补充采集的角色数: {len(missing_characters)}")
    
    if not missing_characters:
        logger.info("🎉 所有角色都已达到目标数量！")
        conn.close()
        return
    
    # 开始采集
    logger.info(f"========== 开始多站点补充采集 {len(missing_characters)} 个角色 ==========")
    logger.info(f"站点优先级: {' → '.join([s['label'] for s in EXTENDED_SITES])}")
    
    total_success = 0
    completed_characters = 0
    
    for i, (chinese_name, english_name, work_title) in enumerate(missing_characters, 1):
        logger.info(f"========== [{i}/{len(missing_characters)}] 正在处理: {chinese_name} ({work_title}) ==========")
        
        collect_character(conn, chinese_name, english_name, work_title, args.output_dir, args.target_count)
        
        # 统计完成情况
        completed_characters += 1
        
        # 输出进度统计
        if i % 5 == 0:
            logger.info(f"📊 进度: {i}/{len(missing_characters)} | 已完成: {completed_characters}")
        
        # 角色间延迟
        time.sleep(random.uniform(args.delay * 0.5, args.delay * 1.5))
    
    # 关闭数据库
    conn.close()
    
    # 最终统计
    logger.info("========== 多站点采集完成 ==========")
    logger.info(f"📊 统计结果:")
    logger.info(f"   处理角色数: {len(missing_characters)}")
    logger.info(f"   数据库: {args.db_path}")
    
    # 显示数据库统计
    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM collected_images')
    total_images = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM character_stats WHERE success_count > 0')
    collected_chars = cursor.fetchone()[0]
    conn.close()
    
    logger.info(f"   数据库记录数: {total_images}")
    logger.info(f"   已采集角色数: {collected_chars}")


if __name__ == '__main__':
    main()
