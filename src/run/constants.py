"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.ini_file_spider import check_ini_config, read_ini_config, INI_FILE_PATH
from image.image_scan import scan_img_txt

# Check default configuration
check_ini_config()

@dataclass
class SpiderConfig:
    """Spider configuration settings"""
    app_port: int = 33334
    web_flag_start: bool = False
    stop_spider_url_flag: bool = True
    stop_download_image_flag: bool = True
    spider_mode: str = 'manual'
    process_image_flag: bool = False
    download_finish_flag: bool = True
    download_video_link_flag: bool = False
    download_gif_zip_flag: bool = False
    unzip_generate_video_flag: bool = False
    uploading_image_flag: bool = False
    download_image_re_flag: bool = False
    unzip_file_flag: bool = False
    max_urls_per_keyword: int = 200  # 每个角色最大采集URL数量
    current_keyword: str = None        # 当前爬取的关键字
    current_count: int = 0           # 当前已采集URL数量

# WebSocket connections for real-time progress
websocket_connections = []  # Store active WebSocket connections

@dataclass 
class UIConfig:
    """UI visibility configuration"""
    edit_config_msg_visible: bool = False
    about_message_lookup_visible: bool = False
    online_look_image_visible: bool = False
    auto_play_image_visible: bool = False
    log_check_visible: bool = False
    start_auto_play_flag: bool = False
    performance_monitor_visible: bool = False
    log_analyze_visible: bool = False
    jm_dialog_visible: bool = False
    img_analyze_visible: bool = False

@dataclass
class ProcessingConfig:
    """Image processing configuration"""
    face_detect_flag: bool = False
    convert_folder_name_flag: bool = False
    online_show_image: bool = False
    firewall_flag: bool = False
    check_images_flag: bool = False
    category_image_flag: bool = False
    single_flag: bool = False
    add_keyword_finish_flag: bool = False
    log_no_output_flag: bool = False
    detect_model_flag: bool = False
    jm_sd_auto_flag: bool = False
    internet_connect_status: bool = False
    process_jm_image_category_flag: bool = False
    go_file_upload_flag: bool = False
    jm_domain_detect_flag: bool = False

# Path configurations
data_path = Path('./data').resolve()
basic_path = Path(__file__).parent.resolve()

# Image tracking
online_img_list = scan_img_txt(str(data_path))
cur_show_img_index = 0
spider_images_current_count = 0

# Content filtering
ban_content = '【国家反诈中心、工信部反诈中心、中国电信、中国联通、中国移动联合提醒】'

# Read configuration from INI file
def read_config_int(section: str, key: str) -> int:
    return int(read_ini_config(INI_FILE_PATH, section, key))

def read_config_float(section: str, key: str) -> float:
    return float(read_ini_config(INI_FILE_PATH, section, key))

def read_config_str(section: str, key: str) -> str:
    return read_ini_config(INI_FILE_PATH, section, key)

# Video output settings
output_video_fps = read_config_int("spider_config", "output_video_fps")
output_video_width = read_config_int("spider_config", "output_video_width") 
output_video_height = read_config_int("spider_config", "output_video_height")
spider_images_max_count = read_config_int("spider_config", "spider_images_max_count")

# Spider configuration
sis_log_level = read_config_str("spider_config", "sis_log_level")
visit_url = read_config_str("spider_config", "visit_url")
s1_url = read_config_str("spider_config", "s1_url")
s2_url = read_config_str("spider_config", "s2_url")
target_url = read_config_str("spider_config", "target_url")
r18_mode = read_config_str("spider_config", "r18_mode")
all_show = read_config_str("spider_config", "all_show")

# Proxy settings
proxy_flag = read_config_str("spider_config", "proxy_flag")
proxy_website = read_config_str("spider_config", "proxy_website")
proxy_mode = read_config_str("spider_config", "proxy_mode")
proxy_server_ip = read_config_str("spider_config", "proxy_server_ip")
proxy_server_port = read_config_int("spider_config", "proxy_server_port")

# Timing settings
search_delta_time = read_config_int("spider_config", "search_delta_time")
detail_delta_time = read_config_int("spider_config", "detail_delta_time")

# Automatic configuration
filter_http_url = read_config_str("automatic_config", "filter_http_url")
filter_image_url = read_config_str("automatic_config", "filter_image_url")
zoom_in_scale = read_config_float("automatic_config", "zoom_in_scale")
zoom_out_scale = read_config_float("automatic_config", "zoom_out_scale")
scheduled_download_program_flag = read_config_str("automatic_config", "scheduled_download_program_flag")

# Chrome settings
chrome_path = read_config_str("automatic_config", "chrome_path")
chrome_exe_path = read_config_str("automatic_config", "chrome_exe_path")
chrome_version = read_config_str("automatic_config", "chrome_version")

# Additional settings
upload_minio_image_flag = read_config_str("automatic_config", "upload_minio_image_flag")
allow_replace_domain_flag = read_config_str("automatic_config", "allow_replace_domain_flag")
fire_wall_delay_time = read_config_int("automatic_config", "fire_wall_delay_time")
download_img_retry_times = read_config_int("automatic_config", "download_img_retry_times")
download_img_time_out = read_config_int("automatic_config", "download_img_time_out")
detect_timeout_auto = read_config_int("automatic_config", "detect_timeout_auto")
wechat_push_flag = read_config_str("automatic_config", "wechat_push_flag")
search_content = read_config_str("automatic_config", "search_content")
dmi_api_server = read_config_str("automatic_config", "dmi_api_server")
detect_img_model = read_config_str("automatic_config", "detect_img_model")

# MinIO configuration
minio_config_id = read_config_str("minio_config_selected", "minio_config_id")
minio_server_ip = read_config_str("minio_config_selected", "minio_server_ip")
minio_server_port = read_config_str("minio_config_selected", "minio_server_port")
minio_account = read_config_str("minio_config_selected", "minio_account")
minio_password = read_config_str("minio_config_selected", "minio_password")
mark_msg = read_config_str("minio_config_selected", "mark_msg")
enable = read_config_str("minio_config_selected", "enable")

# Unzip configuration
seven_zip_path = read_config_str("unzip_config", "seven_zip_path")
password = read_config_str("unzip_config", "password")

# Version information
sis_server_version = "v1.2.5.260305"

PINYIN_MAPPING = {
    '阿洛娜': 'a1luo4na4',
    '普拉娜': 'pu3la1na4',
    '纳西妲': 'na4xi1da2',
    '缇宝': 'ti2bao3',
    '可莉': 'ke3li4',
    '迪奥娜': 'di2ao4na4',
    '瑶瑶': 'yao2yao2',
    '希格雯': 'xi1ge2wen2',
    '蕾贝': 'lei3bei4',
    '黑塔': 'hei1ta3',
    '符玄': 'fu2xuan2',
    '七七': 'qi1qi1',
    '早柚': 'zao3you4',
    '多莉': 'duo1li4',
    '卡齐娜': 'ka3qi2na4',
    '三月七': 'san1yue4qi1',
    '花火': 'hua1huo3',
    '银狼': 'yin2lang2',
    '天童爱丽丝': 'tian1tong2ai4li4si1',
    '早雾': 'zao3wu4',
    '维里奈': 'wei2li3nai4',
    '安可': 'an1ke3',
    '釉壶': 'you4hu2',
    '洛可可': 'luo4ke4ke4',
    '鹿目圆': 'lu4mu4yuan2',
    '晓美焰': 'xiao3mei3yan4',
    '血小板': 'xue4xiao3ban3',
    '雷姆': 'lei2mu3',
    '拉姆': 'la1mu3',
    '康娜': 'kang1na4',
    '四糸乃': 'si4mi4nai3',
    '凯露': 'kai3lu4',
    '克萝萝': 'ke4luo2luo2',
    '小闪': 'xiao3shan3',
    '伊莉雅': 'yi1li4ya3',
    '忍野忍': 'ren3ye3ren3',
    '智乃': 'zhi4nai3',
    '小埋': 'xiao3mai2',
    '纱雾': 'sha1wu4',
    '猫宫又奈': 'mao1gong1you4nai4',
    '德丽莎': 'de2li4sha1',
    '布洛妮娅': 'bu4luo4ni2ya4',
    '可琳': 'ke3lin2',
    '爱丽儿': 'ai4li4er3',
    '神乐': 'shen1yue4',
    '白上吹雪': 'bai2shang4chui1xue3',
    '月千夜': 'yue4qian1ye4',
    '芙丽希娅': 'fu2li4xi1ya4',
    '莉塔拉': 'li4ta3la1',
    '维普蕾': 'wei2pu3lei3',
    '夏克里': 'xia4ke4li3',
    '纳甘': 'na4gan1',
    '科谢尼娅': 'ke1xie4ni2ya4',
    '奇塔': 'qi2ta3',
    '寇尔芙': 'kou4er3fu2',
    '克罗丽科': 'ke4luo2li4ke1',
    '佩里缇亚': 'pei4li3ti2ya4',
    '阿尼亚': 'a1ni4ya4',
    '洛茜': 'luo4qian4',
    '祢豆子': 'ni2dou4zi5',
    '希儿': 'xi1er3',
    '杏': 'xing4',
    '伊瑟琳': 'yi1se4lin2',
    '芙兰': 'fu2lan2',
    '菲米莉丝': 'fei1mi3li4si1',
    '罗可可': 'luo4ke3ke3',
    '蜜豆子': 'mi2dou4zi',
    '神乐': 'shen2le4',
    '克拉拉': 'ke4la1la1',
}

def get_pinyin(key_word: str) -> str:
    """获取角色名的统一拼音

    优先使用预定义的拼音映射表，确保同一角色名始终生成相同的拼音
    """
    if key_word in PINYIN_MAPPING:
        return PINYIN_MAPPING[key_word]
    from pypinyin import lazy_pinyin, Style
    return ''.join(lazy_pinyin(key_word, style=Style.TONE3))

build_date = "2026-03-05 18:00"
publish_date = "2026-03-05 18:30"
