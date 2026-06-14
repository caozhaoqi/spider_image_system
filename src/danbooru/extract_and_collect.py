#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从关键词文件中提取女角色并采集
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from src.danbooru.danbooru_mirror_spider import DanbooruMirrorSpider


# 已知角色映射（中文名 -> 英文名 -> 作品名）
KNOWN_CHARACTERS = {
    # 原神
    '琴': ('jean', 'genshin_impact'),
    '安柏': ('amber', 'genshin_impact'),
    '丽莎': ('lisa', 'genshin_impact'),
    '芭芭拉': ('barbara', 'genshin_impact'),
    '可莉': ('klee', 'genshin_impact'),
    '诺艾尔': ('noelle', 'genshin_impact'),
    '菲谢尔': ('fischl', 'genshin_impact'),
    '砂糖': ('sucrose', 'genshin_impact'),
    '莫娜': ('mona', 'genshin_impact'),
    '迪奥娜': ('diona', 'genshin_impact'),
    '罗莎莉亚': ('rosaria', 'genshin_impact'),
    '优菈': ('eula', 'genshin_impact'),
    '闲云': ('cloud_retainer', 'genshin_impact'),
    '瑶瑶': ('yaoyao', 'genshin_impact'),
    '夜兰': ('yelan', 'genshin_impact'),
    '申鹤': ('shenhe', 'genshin_impact'),
    '云堇': ('yunjin', 'genshin_impact'),
    '北斗': ('beidou', 'genshin_impact'),
    '凝光': ('ningguang', 'genshin_impact'),
    '香菱': ('xiangling', 'genshin_impact'),
    '刻晴': ('keqing', 'genshin_impact'),
    '七七': ('qiqi', 'genshin_impact'),
    '辛焱': ('xinyan', 'genshin_impact'),
    '甘雨': ('ganyu', 'genshin_impact'),
    '胡桃': ('hu_tao', 'genshin_impact'),
    '烟绯': ('yanfei', 'genshin_impact'),
    '神里绫华': ('ayaka', 'genshin_impact'),
    '宵宫': ('yoimiya', 'genshin_impact'),
    '早柚': ('sayu', 'genshin_impact'),
    '雷电将军': ('raiden_shogun', 'genshin_impact'),
    '九条裟罗': ('sara', 'genshin_impact'),
    '珊瑚宫心海': ('kokomi', 'genshin_impact'),
    '八重神子': ('yae_miko', 'genshin_impact'),
    '荒泷一斗': ('itto', 'genshin_impact'),
    '五郎': ('gorou', 'genshin_impact'),
    '散兵': ('scaramouche', 'genshin_impact'),
    '雷电真': ('baal', 'genshin_impact'),
    '纳西妲': ('nahida', 'genshin_impact'),
    '妮露': ('nilou', 'genshin_impact'),
    '赛诺': ('cyno', 'genshin_impact'),
    '提纳里': ('tighnari', 'genshin_impact'),
    '多莉': ('dori', 'genshin_impact'),
    '柯莱': ('collei', 'genshin_impact'),
    '珐露珊': ('faruzan', 'genshin_impact'),
    '艾尔海森': ('alhaitham', 'genshin_impact'),
    '迪希雅': ('dehya', 'genshin_impact'),
    '米卡': ('mika', 'genshin_impact'),
    '白术': ('baizhu', 'genshin_impact'),
    '卡维': ('kaveh', 'genshin_impact'),
    '琳妮特': ('lynette', 'genshin_impact'),
    '菲米尼': ('freminet', 'genshin_impact'),
    '芙宁娜': ('furina', 'genshin_impact'),
    '夏洛蒂': ('charlotte', 'genshin_impact'),
    '那维莱特': ('neuvillette', 'genshin_impact'),
    '克洛琳德': ('clorinde', 'genshin_impact'),
    '希格雯': ('sigewinne', 'genshin_impact'),
    '卡齐娜': ('kachina', 'genshin_impact'),
    '绮良良': ('kirara', 'genshin_impact'),
    '派蒙': ('paimon', 'genshin_impact'),
    
    # 崩坏：星穹铁道
    '艾丝妲': ('asta', 'honkai:_star_rail'),
    '三月七': ('march_7th', 'honkai:_star_rail'),
    '希露瓦': ('serval', 'honkai:_star_rail'),
    '黑塔': ('herta', 'honkai:_star_rail'),
    '大丽花': ('dahlia', 'honkai:_star_rail'),
    '银狼': ('silver_wolf', 'honkai:_star_rail'),
    '希儿': ('seele', 'honkai:_star_rail'),
    '卡芙卡': ('kafka', 'honkai:_star_rail'),
    '素裳': ('sushang', 'honkai:_star_rail'),
    '姬子': ('himeko', 'honkai:_star_rail'),
    '布洛妮娅': ('bronya', 'honkai:_star_rail'),
    '克拉拉': ('clara', 'honkai:_star_rail'),
    '佩拉': ('pelagia', 'honkai:_star_rail'),
    '虎克': ('hook', 'honkai:_star_rail'),
    '黑天鹅': ('black_swan', 'honkai:_star_rail'),
    '花火': ('sparkle', 'honkai:_star_rail'),
    '阮梅': ('ruan_mei', 'honkai:_star_rail'),
    '娜塔莎': ('natasha', 'honkai:_star_rail'),
    '寒鸦': ('raven', 'honkai:_star_rail'),
    '镜流': ('jingliu', 'honkai:_star_rail'),
    '雪衣': ('xueyi', 'honkai:_star_rail'),
    '黄泉': ('huangquan', 'honkai:_star_rail'),
    '符玄': ('fu_xuan', 'honkai:_star_rail'),
    '白露': ('bai_lu', 'honkai:_star_rail'),
    '霍霍': ('huohuo', 'honkai:_star_rail'),
    '玲妮': ('lynne', 'honkai:_star_rail'),
    '青雀': ('qingque', 'honkai:_star_rail'),
    '停云': ('tingyun', 'honkai:_star_rail'),
    '托帕': ('topaz', 'honkai:_star_rail'),
    '驭空': ('yukong', 'honkai:_star_rail'),
    '云璃': ('yunli', 'honkai:_star_rail'),
    '缇宝': ('tingbao', 'honkai:_star_rail'),
    '流萤': ('firefly', 'honkai:_star_rail'),
    
    # 崩坏3
    '布洛妮娅': ('bronya', 'honkai_impact_3rd'),
    '符华': ('fu_hua', 'honkai_impact_3rd'),
    '希儿': ('seele', 'honkai_impact_3rd'),
    '格蕾修': ('griseo', 'honkai_impact_3rd'),
    '丽塔': ('rita', 'honkai_impact_3rd'),
    '爱莉希雅': ('elysia', 'honkai_impact_3rd'),
    '琪亚娜': ('kiana', 'honkai_impact_3rd'),
    '雷电芽衣': ('mei', 'honkai_impact_3rd'),
    '识之律者': ('herrscher_of_sentience', 'honkai_impact_3rd'),
    '雷之律者': ('herrscher_of_thunder', 'honkai_impact_3rd'),
    '空之律者': ('herrscher_of_the_void', 'honkai_impact_3rd'),
    '死生之律者': ('herrscher_of_life_and_death', 'honkai_impact_3rd'),
    '薪炎之律者': ('herrscher_of_flamescion', 'honkai_impact_3rd'),
    '始源之律者': ('herrscher_of_origin', 'honkai_impact_3rd'),
    '人之律者': ('herrscher_of_humanity', 'honkai_impact_3rd'),
    '无量塔姬子': ('himeko', 'honkai_impact_3rd'),
    '八重樱': ('yae_sakura', 'honkai_impact_3rd'),
    '德丽莎': ('theresa', 'honkai_impact_3rd'),
    '卡莲': ('kallen', 'honkai_impact_3rd'),
    '萝莎莉娅': ('rozaliya', 'honkai_impact_3rd'),
    '莉莉娅': ('liliya', 'honkai_impact_3rd'),
    '时雨绮罗': ('shigure_kira', 'honkai_impact_3rd'),
    '普罗米修斯': ('prometheus', 'honkai_impact_3rd'),
    '苏莎娜': ('susannah', 'honkai_impact_3rd'),
    '李素裳': ('li_sushang', 'honkai_impact_3rd'),
    '维尔薇': ('vill_v', 'honkai_impact_3rd'),
    '梅比乌斯': ('mobius', 'honkai_impact_3rd'),
    '帕朵菲莉丝': ('pardofelis', 'honkai_impact_3rd'),
    '阿波尼亚': ('aponia', 'honkai_impact_3rd'),
    '伊甸': ('eden', 'honkai_impact_3rd'),
    '比安卡': ('bianka', 'honkai_impact_3rd'),
    '明日香': ('asuka', 'honkai_impact_3rd'),
}


# 作品名映射：中文 -> 英文（用于Danbooru标签搜索）
WORK_TITLE_MAPPING = {
    '原神': 'genshin_impact',
    '崩坏星穹铁道': 'honkai:_star_rail',
    '崩坏3': 'honkai_impact_3rd',
}


def load_keywords_from_files(base_dir: str) -> List[str]:
    """从关键词文件中加载所有内容（包括子目录）"""
    keywords = set()
    dir_path = Path(base_dir)
    
    # 读取当前目录和子目录下的所有txt文件
    for file_path in dir_path.rglob('*.txt'):
        if file_path.name.startswith('.'):
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and len(line) >= 2 and len(line) <= 15:
                        keywords.add(line)
            logger.info(f"从 {file_path} 加载了关键词")
        except Exception as e:
            logger.warning(f"读取 {file_path} 失败: {e}")
    
    logger.info(f"共加载 {len(keywords)} 个关键词")
    return sorted(list(keywords))


def extract_characters(keywords: List[str]) -> List[Tuple[str, str, str]]:
    """从关键词中提取已知角色"""
    characters = []
    seen = set()
    
    for keyword in keywords:
        if keyword in KNOWN_CHARACTERS:
            english_name, work_tag = KNOWN_CHARACTERS[keyword]
            work_title = WORK_TITLE_MAPPING.get(work_tag, work_tag)
            key = (keyword, english_name, work_title)
            if key not in seen:
                characters.append(key)
                seen.add(key)
                logger.debug(f"识别角色: {keyword} -> {english_name} ({work_title})")
    
    logger.success(f"从关键词中识别出 {len(characters)} 个已知角色")
    return characters


def init_database(db_path: str) -> sqlite3.Connection:
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
        logger.debug(f"插入记录失败: {e}")


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


def collect_character(conn: sqlite3.Connection, spider: DanbooruMirrorSpider,
                     chinese_name: str, english_name: str, work_title: str,
                     output_dir: str, target_count: int = 30):
    """采集单个角色"""
    import random
    import time
    
    character_dir = Path(output_dir) / english_name
    character_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查现有图片数量
    existing_count = len(list(character_dir.glob('*.jpg'))) + len(list(character_dir.glob('*.png')))
    if existing_count >= target_count:
        logger.info(f"⏭️ {chinese_name} 已有 {existing_count} 张图片，跳过")
        return
    
    need_count = target_count - existing_count
    
    # 构建搜索标签
    work_tag = WORK_TITLE_MAPPING.get(work_title, work_title.lower().replace(' ', '_'))
    tag = f"{english_name}({work_tag})" if '_' in english_name else f"{english_name}_({work_tag})"
    
    try:
        posts = spider.get_all_posts(tag, max_posts=need_count * 2)
        
        if not posts:
            logger.warning(f"⚠️ {chinese_name} 未找到匹配图片")
            update_character_stats(conn, chinese_name, english_name, work_title, 0, 0, 'safebooru')
            return
        
        success_count = 0
        fail_count = 0
        
        for post in posts[:need_count * 2]:
            if success_count >= need_count:
                break
            
            image_url = spider.get_image_url(post)
            if not image_url:
                fail_count += 1
                continue
            
            ext = image_url.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                ext = 'jpg'
            
            post_id = post.get('id', f"unknown_{random.randint(1, 9999)}")
            file_path = character_dir / f"{post_id}.{ext}"
            
            if file_path.exists():
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
            
            time.sleep(random.uniform(0.3, 0.8))
        
        update_character_stats(conn, chinese_name, english_name, work_title, success_count, fail_count, 'safebooru')
        
        if success_count > 0:
            logger.success(f"✅ {chinese_name}: 成功采集 {success_count} 张")
        else:
            logger.warning(f"❌ {chinese_name}: 未采集到图片")
    
    except Exception as e:
        logger.error(f"采集 {chinese_name} 时发生错误: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='从关键词文件提取女角色并采集')
    parser.add_argument('--keywords-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img',
                        help='关键词文件目录')
    parser.add_argument('--output-dir', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/final_dataset',
                        help='图片保存目录')
    parser.add_argument('--db-path', type=str, 
                        default='/Users/caozhaoqi/PycharmProjects/anime_role_detect/data/collection.db',
                        help='数据库文件路径')
    parser.add_argument('--target-count', type=int, default=50,
                        help='每个角色目标图片数量')
    
    args = parser.parse_args()
    
    # 加载关键词
    logger.info(f"正在从 {args.keywords_dir} 加载关键词...")
    keywords = load_keywords_from_files(args.keywords_dir)
    logger.info(f"共加载 {len(keywords)} 个关键词")
    
    # 提取角色
    characters = extract_characters(keywords)
    
    if not characters:
        logger.warning("未识别到任何已知角色")
        return
    
    # 初始化数据库
    conn = init_database(args.db_path)
    
    # 创建采集器
    spider = DanbooruMirrorSpider(site='safebooru', max_workers=4, include_nsfw=False)
    
    # 开始采集
    logger.info(f"========== 开始采集 {len(characters)} 个角色 ==========")
    
    for i, (chinese_name, english_name, work_title) in enumerate(characters, 1):
        logger.info(f"========== [{i}/{len(characters)}] 正在处理: {chinese_name} ({work_title}) ==========")
        collect_character(conn, spider, chinese_name, english_name, work_title, args.output_dir, args.target_count)
    
    # 关闭数据库
    conn.close()
    
    logger.info("========== 采集完成 ==========")


if __name__ == '__main__':
    main()
