#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析角色名单，生成采集标签"""

import os
import re

# 作品名到Danbooru标签的映射（包含模糊匹配）
WORK_TITLE_MAPPING = {
    '蔚蓝档案': 'blue_archive',
    '原神': 'genshin_impact',
    '崩坏星穹铁道': 'honkai_star_rail',
    '崩坏3': 'honkai_impact_3rd',
    '崩坏学园2': 'zenless_zone_zero',
    '鸣潮': 'wuthering_waves',
    '异环': '',
    '魔法少女小圆': 'mahou_shoujo_madoka_magica',
    'Re:从零开始的异世界生活': 're_zero',
    '小林家的龙女仆': 'kobayashi_san_chi_no_maid_dragon',
    '约会大作战': 'date_a_live',
    '公主连接': 'princess_connect',
    'Fate/kaleid liner Prisma Illya': 'fate_kaleid_liner_prisma_illya',
    '物语系列': 'monogatari_series',
    '请问您今天要来点兔子吗': 'gochuumon_wa_usagi_desu_ka',
    '干物妹小埋': 'himouto_umaru_chan',
    '埃罗芒阿老师': 'ero_manga_teacher',
    '间谍过家家': 'spy_x_family',
    '明日方舟': 'arknights',
    '明日方舟终末地': 'honkai_arena',
    '阴阳师': 'obey_me',
    'Hololive': 'hololive',
    '东方Project': 'touhou',
    '少女前线2：追放': 'girls_frontline_2',
    '工作细胞': 'hataraku_saibou',
    '天使降临我身边': 'angel_beats',
    '龙王的工作': 'chihayafuru',
    '偶像荣耀': 'idolypride',
    '绝区零': 'zenless_zone_zero',
    '幸运星': 'lucky_star',
    'Love Live': 'love_live',
    '为美好的世界献上祝福': 'konosuba',
    '悠哉日常大王': 'yuru_yuri',
    '你的名字': 'kimi_no_na_wa',
    '声之形': 'koe_no_katachi',
}

def normalize_work(work):
    """规范化作品名"""
    # 移除空格和特殊字符
    work = work.strip()
    
    # 精确匹配
    if work in WORK_TITLE_MAPPING:
        return WORK_TITLE_MAPPING[work]
    
    # 模糊匹配
    for key, value in WORK_TITLE_MAPPING.items():
        if key.lower().replace(' ', '') in work.lower().replace(' ', ''):
            return value
    
    return None

def parse_character_list(filepath):
    """解析角色名单"""
    characters = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                chinese_name = parts[0]
                work_title = parts[1]
                english_name = parts[2]
                
                # 获取Danbooru标签
                work_tag = normalize_work(work_title)
                
                if work_tag:
                    danbooru_tag = f"{english_name}_({work_tag})"
                else:
                    danbooru_tag = english_name
                
                characters.append({
                    'chinese': chinese_name,
                    'english': english_name,
                    'work': work_title,
                    'tag': danbooru_tag
                })
    
    return characters

def main():
    input_file = '/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/auto_spider_img/loli-role-new.txt'
    output_file = '/Users/caozhaoqi/PycharmProjects/anime_role_detect/archived/spider_image_system/角色标签列表.txt'
    
    characters = parse_character_list(input_file)
    
    print(f"解析到 {len(characters)} 个角色")
    
    # 写入标签列表
    with open(output_file, 'w', encoding='utf-8') as f:
        for char in characters:
            f.write(f"{char['tag']}\n")
    
    print(f"已写入 {output_file}")
    
    # 显示前30个
    print("\n前30个角色标签:")
    for i, char in enumerate(characters[:30], 1):
        print(f"  {i}. {char['chinese']} ({char['work']}) -> {char['tag']}")
    
    # 统计各作品角色数
    works = {}
    for char in characters:
        work = char['work']
        works[work] = works.get(work, 0) + 1
    
    print(f"\n各作品角色数:")
    for work, count in sorted(works.items(), key=lambda x: -x[1]):
        print(f"  {work}: {count}")

if __name__ == '__main__':
    main()
