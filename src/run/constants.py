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
    app_port: int = 33333
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
basic_path = Path('.').resolve()

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
build_date = "2026-03-05 18:00"
publish_date = "2026-03-05 18:30"
