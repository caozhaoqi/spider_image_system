"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import configparser
from loguru import logger
from model.SpiderConfigModel import SpiderConfigModel
from utils.sys_info import get_cur_os

INI_PATH = os.path.join(os.getcwd(), 'config')
INI_FILE_PATH = os.path.join(INI_PATH, 'config.ini')


@logger.catch
def read_config_all() -> Dict[str, Dict[str, str]]:
    """Read all sections from config file and return as dictionary"""
    config = configparser.ConfigParser()
    config.read(os.path.realpath(INI_FILE_PATH))
    return {section: dict(config.items(section)) for section in config.sections()}


@logger.catch
def spider_config() -> SpiderConfigModel:
    """Read spider configuration from ini file"""
    entity = SpiderConfigModel()
    
    # Spider config section
    spider_section = "spider_config"
    entity.s2_url = read_ini_config(INI_FILE_PATH, spider_section, "s2_url")
    entity.visit_url = read_ini_config(INI_FILE_PATH, spider_section, "visit_url") 
    entity.s1_url = read_ini_config(INI_FILE_PATH, spider_section, "s1_url")
    entity.target_url = read_ini_config(INI_FILE_PATH, spider_section, "target_url")
    entity.r18_mode = read_ini_config(INI_FILE_PATH, spider_section, "r18_mode")
    entity.all_show = read_ini_config(INI_FILE_PATH, spider_section, "all_show")
    entity.proxy_flag = read_ini_config(INI_FILE_PATH, spider_section, "proxy_flag")
    entity.search_delta_time = read_ini_config(INI_FILE_PATH, spider_section, "search_delta_time")
    entity.detail_delta_time = read_ini_config(INI_FILE_PATH, spider_section, "detail_delta_time")
    entity.sis_log_level = read_ini_config(INI_FILE_PATH, spider_section, "sis_log_level")
    entity.spider_images_max_count = read_ini_config(INI_FILE_PATH, spider_section, "spider_images_max_count")
    entity.output_video_fps = read_ini_config(INI_FILE_PATH, spider_section, "output_video_fps")
    entity.output_video_width = read_ini_config(INI_FILE_PATH, spider_section, "output_video_width")
    entity.output_video_height = read_ini_config(INI_FILE_PATH, spider_section, "output_video_height")
    entity.proxy_server_ip = read_ini_config(INI_FILE_PATH, spider_section, "proxy_server_ip")
    entity.proxy_server_port = read_ini_config(INI_FILE_PATH, spider_section, "proxy_server_port")

    # Minio config section
    minio_section = "minio_config_selected"
    entity.minio_config_id = read_ini_config(INI_FILE_PATH, minio_section, "minio_config_id")
    entity.minio_server_ip = read_ini_config(INI_FILE_PATH, minio_section, "minio_server_ip")
    entity.minio_server_port = read_ini_config(INI_FILE_PATH, minio_section, "minio_server_port")
    entity.minio_account = read_ini_config(INI_FILE_PATH, minio_section, "minio_account")
    entity.minio_password = read_ini_config(INI_FILE_PATH, minio_section, "minio_password")
    entity.enable = read_ini_config(INI_FILE_PATH, minio_section, "enable")

    return entity


@logger.catch
def write_minio_config_to_file(minio_config: SpiderConfigModel) -> bool:
    """Write minio configuration to ini file"""
    ini_path = os.path.realpath(INI_FILE_PATH)
    logger.info(f"Generate file path: {ini_path}")

    # Create config directory if not exists
    os.makedirs(os.path.dirname(ini_path), exist_ok=True)

    # Remove existing file
    try:
        if os.path.exists(ini_path):
            os.remove(ini_path)
    except PermissionError as pe:
        logger.error(f"Permission error: {pe}")
        return False
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return False

    conf = configparser.ConfigParser()

    # Spider config section
    conf.add_section("spider_config")
    spider_config = {
        "s2_url": minio_config.s2_url,
        "visit_url": minio_config.visit_url,
        "s1_url": minio_config.s1_url,
        "target_url": minio_config.target_url,
        "r18_mode": str(minio_config.r18_mode),
        "all_show": str(minio_config.all_show),
        "proxy_flag": str(minio_config.proxy_flag),
        "proxy_website": "http://demo.spiderpy.cn",
        "proxy_mode": "auto",
        "search_delta_time": str(minio_config.search_delta_time),
        "detail_delta_time": str(minio_config.detail_delta_time),
        "sis_log_level": minio_config.sis_log_level,
        "spider_images_max_count": str(minio_config.spider_images_max_count),
        "output_video_fps": str(minio_config.output_video_fps),
        "output_video_width": str(minio_config.output_video_width),
        "output_video_height": str(minio_config.output_video_height),
        "proxy_server_ip": minio_config.proxy_server_ip,
        "proxy_server_port": str(minio_config.proxy_server_port)
    }
    for key, value in spider_config.items():
        conf.set("spider_config", key, value)

    # Automatic config section
    conf.add_section("automatic_config")
    automatic_config = {
        "filter_http_url": "js,emoji,svq,_50.png,_50.jpg,no_profile_s.png,block.vv50.de,square,custom,_50.gif,data:image/png,no_profile.png,common",
        "filter_image_url": "s_mode=s_tag,block.vv50.de,tags,square,custom,square,custom,50.gif,data:image/png,no_profile.png,common",
        "zoom_out_scale": "0.9",
        "zoom_in_scale": "1.1",
        "fire_wall_delay_time": "60",
        "download_img_retry_times": "2", 
        "download_img_time_out": "10",
        "detect_timeout_auto": "300",
        "chrome_path": "None",
        "chrome_exe_path": "None",
        "chrome_version": "1",
        "upload_minio_image_Flag": "False",
        "allow_replace_domain_flag": "True",
        "scheduled_download_program_flag": "True",
        "dmi_api_server": "192.168.163.129:8888",
        "detect_img_model": "python",
        "WeChat_push_flag": "True",
        "search_content": "site"
    }
    for key, value in automatic_config.items():
        conf.set("automatic_config", key, value)

    # Minio config section
    conf.add_section("minio_config_selected")
    minio_config_selected = {
        "minio_config_id": "1",
        "minio_server_ip": "121.36.66.145",
        "minio_server_port": "9000", 
        "minio_account": "minioadmin",
        "minio_password": "minioadmin",
        "mark_msg": "minio_config['mark_msg']",
        "enable": "1"
    }
    for key, value in minio_config_selected.items():
        conf.set("minio_config_selected", key, value)

    # Unzip config section
    conf.add_section("unzip_config")
    conf.set("unzip_config", "SEVEN_ZIP_PATH", "C:/Program Files/7-Zip/7z.exe")
    conf.set("unzip_config", "PASSWORD", "1204")

    with open(ini_path, 'a+', encoding="utf-8") as f:
        conf.write(f)

    logger.info(f"Config write finished, using visit url: {conf.get('spider_config', 'visit_url')}")
    return True


@logger.catch
def read_ini_config(file_name: str, section: str, value_key: str) -> str:
    """Read value from ini config file"""
    config = configparser.ConfigParser()
    config.read(file_name, encoding="utf-8")

    try:
        return config.get(section, value_key)
    except configparser.NoSectionError as e:
        logger.error(f"Section error: {section}, key: {value_key}, error: {e}")
        return "log_dir"
    except configparser.NoOptionError:
        logger.error(f"No option '{value_key}' in section '{section}'")
        return ""


# Default configuration constants
DEFAULT_CONFIG = {
    "spider_config": {
        "visit_url": "sd.vv50.de",
        "s1_url": "pixiv.srpr.cc", 
        "s2_url": "pixiv.888718.xyz",
        "target_url": "pximg.lolicon.run",
        "r18_mode": "True",
        "all_show": "False",
        "proxy_flag": "False",
        "proxy_website": "http://demo.spiderpy.cn",
        "proxy_mode": "auto",
        "search_delta_time": "3",
        "detail_delta_time": "2",
        "sis_log_level": "DEBUG",
        "spider_images_max_count": "1000",
        "output_video_fps": "24",
        "output_video_width": "2560",
        "output_video_height": "1440",
        "proxy_server_ip": "192.168.199.26",
        "proxy_server_port": "8080"
    },
    "automatic_config": {
        "filter_http_url": "js,emoji,svq,_50.png,_50.jpg,no_profile_s.png,block.vv50.de,square,custom,_50.gif,data:image/png,no_profile.png,common",
        "filter_image_url": "s_mode=s_tag,block.vv50.de,tags,square,custom,square,custom,50.gif,data:image/png,no_profile.png,common",
        "zoom_out_scale": "0.9",
        "zoom_in_scale": "1.1",
        "fire_wall_delay_time": "60",
        "download_img_retry_times": "2",
        "download_img_time_out": "10",
        "detect_timeout_auto": "300",
        "chrome_path": "None",
        "chrome_exe_path": "None",
        "chrome_version": "1",
        "upload_minio_image_Flag": "False",
        "allow_replace_domain_flag": "True",
        "scheduled_download_program_flag": "True",
        "dmi_api_server": "192.168.163.129:8888",
        "detect_img_model": "python",
        "WeChat_push_flag": "True",
        "search_content": "site"
    },
    "minio_config_selected": {
        "minio_config_id": "1",
        "minio_server_ip": "121.36.66.145",
        "minio_server_port": "9000",
        "minio_account": "minioadmin",
        "minio_password": "minioadmin",
        "mark_msg": "minio_config['mark_msg']",
        "enable": "1"
    },
    "unzip_config": {
        "SEVEN_ZIP_PATH": "C:/Program Files/7-Zip/7z.exe",
        "PASSWORD": "1204"
    }
}

@logger.catch
def check_ini_config() -> bool:
    """
    Check and create default configuration file if not exists
    Returns:
        bool: True if config exists or was created successfully
    """
    ini_path = os.path.realpath(os.path.join("config", "config.ini"))
    logger.debug(f"Checking config file at: {ini_path}")

    if os.path.exists(ini_path):
        logger.info("Config file exists")
        return True

    # Create config directory
    config_folder = ".\\config" if get_cur_os() == "win32" else "./config"
    try:
        os.makedirs(config_folder, exist_ok=True)
        logger.info(f"Created config directory: {config_folder}")
    except OSError as e:
        logger.error(f"Failed to create config directory: {e}")
        return False

    # Create and write config file
    conf = configparser.ConfigParser()
    try:
        # Add all sections and their key-value pairs
        for section, values in DEFAULT_CONFIG.items():
            conf.add_section(section)
            for key, value in values.items():
                conf.set(section, key, value)

        # Write to file
        with open(ini_path, 'w', encoding="utf-8") as f:
            conf.write(f)
        
        logger.info(f"Created default config file at: {ini_path}")
        return True

    except (configparser.Error, IOError) as e:
        logger.error(f"Failed to write config file: {e}")
        return False
