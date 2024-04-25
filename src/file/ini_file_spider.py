import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import configparser
from model.SpiderConfigModel import SpiderConfigModel
from loguru import logger

ini_path = os.path.join(os.getcwd(), 'config')
ini_file_path = os.path.join(ini_path, 'config.ini')


@logger.catch
def spider_config():
    """
    ini 配置文件查询
    :return:
    """
    entity = SpiderConfigModel()
    entity.s2_url = read_ini_config(ini_file_path, "spider_config", "s2_url")
    entity.visit_url = read_ini_config(ini_file_path, "spider_config", "visit_url")
    entity.s1_url = read_ini_config(ini_file_path, "spider_config", 's1_url')
    entity.target_url = read_ini_config(ini_file_path, "spider_config", 'target_url')
    entity.r18_mode = read_ini_config(ini_file_path, "spider_config", 'r18_mode')
    entity.all_show = read_ini_config(ini_file_path, "spider_config", 'all_show')
    entity.proxy_flag = read_ini_config(ini_file_path, "spider_config", 'proxy_flag')
    entity.search_delta_time = read_ini_config(ini_file_path, "spider_config", 'search_delta_time')
    entity.detail_delta_time = read_ini_config(ini_file_path, "spider_config", 'detail_delta_time')
    entity.sis_log_level = read_ini_config(ini_file_path, "spider_config", 'sis_log_level')
    entity.spider_images_max_count = read_ini_config(ini_file_path, "spider_config", "spider_images_max_count")
    entity.output_video_fps = read_ini_config(ini_file_path, "spider_config", "output_video_fps")
    entity.output_video_width = read_ini_config(ini_file_path, "spider_config", "output_video_width")
    entity.output_video_height = read_ini_config(ini_file_path, "spider_config", "output_video_height")
    entity.proxy_server_ip = read_ini_config(ini_file_path, "spider_config", "proxy_server_ip")
    entity.proxy_server_port = read_ini_config(ini_file_path, "spider_config", "proxy_server_port")

    entity.minio_config_id = read_ini_config(ini_file_path, "minio_config_selected", 'minio_config_id')
    entity.minio_server_ip = read_ini_config(ini_file_path, "minio_config_selected", 'minio_server_ip')
    entity.minio_server_port = read_ini_config(ini_file_path, "minio_config_selected", 'minio_server_port')
    entity.minio_account = read_ini_config(ini_file_path, "minio_config_selected", 'minio_account')
    entity.minio_password = read_ini_config(ini_file_path, "minio_config_selected", 'minio_password')
    entity.enable = read_ini_config(ini_file_path, "minio_config_selected", 'enable')
    return entity


@logger.catch
def write_minio_config_to_file(minio_config):
    """
    ini config write
    :param minio_config: [] notice
    :return:
    """
    iniPath = os.path.realpath(ini_file_path)
    logger.info("generate file path: " + iniPath)
    conf = configparser.ConfigParser()
    if os.path.exists(iniPath):
        try:
            os.remove(iniPath)
        except PermissionError as pe:
            logger.error("permission error, ini file only read mode, please update ini file chmod! detail: " + str(pe))
            return False
        except Exception as e:
            logger.error("unknown error, detail: " + str(e))
            return False
    logger.warning("Not Found config ini file , creating ini file ....")
    if not os.path.exists(ini_path):
        os.makedirs(ini_path)
        logger.debug("dir not exists, create dir")
    conf.read(iniPath, 'utf-8')
    logger.info("start generate config ini file.")

    conf.add_section("spider_config")
    conf.set("spider_config", "s2_url", minio_config.s2_url)
    conf.set("spider_config", "visit_url", minio_config.visit_url)
    conf.set("spider_config", "s1_url", minio_config.s1_url)
    conf.set("spider_config", "target_url", minio_config.target_url)  # 写入配置参数
    conf.set("spider_config", "r18_mode", str(minio_config.r18_mode))
    conf.set("spider_config", "all_show", str(minio_config.all_show))
    conf.set("spider_config", "proxy_flag", str(minio_config.proxy_flag))
    conf.set("spider_config", "proxy_website", 'http://demo.spiderpy.cn')
    conf.set("spider_config", "proxy_mode", 'auto')
    conf.set("spider_config", "search_delta_time", str(minio_config.search_delta_time))
    conf.set("spider_config", "detail_delta_time", str(minio_config.detail_delta_time))
    conf.set("spider_config", "sis_log_level", minio_config.sis_log_level)
    conf.set("spider_config", "spider_images_max_count", str(minio_config.spider_images_max_count))
    conf.set("spider_config", "output_video_fps", str(minio_config.output_video_fps))
    conf.set("spider_config", "output_video_width", str(minio_config.output_video_width))
    conf.set("spider_config", "output_video_height", str(minio_config.output_video_height))
    conf.set("spider_config", "proxy_server_ip", minio_config.proxy_server_ip)
    conf.set("spider_config", "proxy_server_port", str(minio_config.proxy_server_port))

    conf.add_section("automatic_config")
    conf.set("automatic_config", "filter_http_url", "js,emoji,svq,_50.png,_50.jpg,no_profile_s.png,block.vv50.de,"
                                                    "square,custom,_50.gif,data:image/png,no_profile.png,common")
    conf.set("automatic_config", "filter_image_url", "s_mode=s_tag,block.vv50.de,tags,square,custom,square,custom,"
                                                     "50.gif,data:image/png,no_profile.png,common")
    conf.set("automatic_config", "zoom_out_scale", "0.9")
    conf.set("automatic_config", "zoom_in_scale", "1.1")
    conf.set("automatic_config", "fire_wall_delay_time", "60")
    conf.set("automatic_config", "download_img_retry_times", "2")
    conf.set("automatic_config", "download_img_time_out", "10")
    conf.set("automatic_config", "detect_timeout_auto", "300")
    conf.set("automatic_config", "chrome_path", "None")
    conf.set("automatic_config", "chrome_version", "1")
    conf.set("automatic_config", "upload_minio_image_Flag", "False")
    conf.set("automatic_config", "allow_replace_domain_flag", 'True')

    conf.add_section("minio_config_selected")
    conf.set("minio_config_selected", "minio_config_id", "1")
    conf.set("minio_config_selected", "minio_server_ip", "121.36.66.145")  # 写入配置参数
    conf.set("minio_config_selected", "minio_server_port", "9000")
    conf.set("minio_config_selected", "minio_account", "minioadmin")
    conf.set("minio_config_selected", "minio_password", "minioadmin")
    conf.set("minio_config_selected", "mark_msg", "minio_config['mark_msg']")
    conf.set("minio_config_selected", "enable", '1')

    conf.add_section("unzip_config")
    conf.set("unzip_config", "SEVEN_ZIP_PATH", "C:/Program Files/7-Zip/7z.exe")
    conf.set("unzip_config", "PASSWORD", "1204")

    conf.write(open(iniPath, 'a+', encoding="utf-8"))
    conf.read(iniPath, 'utf-8')
    logger.info("config write finished, read test, current use visit url: " + conf.get("spider_config", "visit_url"))
    return True


@logger.catch
def read_ini_config(file_name, section, value_key):
    """
    读取指定配置文件
    :param file_name: ini file name
    :param section: ini file section name
    :param value_key: ini file content name
    :return: select value
    """
    config = configparser.ConfigParser()

    config.read(file_name, encoding="utf-8")

    try:
        value = config.get(section, value_key)
        return value
    except configparser.NoSectionError as e:
        logger.error("Error! section: " + section + ", value_key: " + value_key + ", value error content: " + str(e))
        return "log_dir"
    except configparser.NoOptionError:
        logger.error(f"No option '{section}' in section, please retry input config key!''" + value_key)
        return ""


@logger.catch
def check_ini_config():
    """
    系统启动引入默认配置
    :return:
    """
    iniPath = os.path.realpath(os.path.join("config", "config.ini"))
    # logger.info("detect config file, path: " + iniPath)
    conf = configparser.ConfigParser()
    if os.path.exists(iniPath):
        return True
    else:
        # logger.warning("Not Found config ini file, creating ini file....")
        if not os.path.exists(".\\config"):
            os.makedirs(".\\config")
            logger.debug("dir not exists, creating dir")
        conf.read(iniPath, 'utf-8')
        # logger.info("start generate config ini file: ")
        conf.add_section("spider_config")
        conf.set("spider_config", "visit_url", "sd.vv50.de")
        conf.set("spider_config", "s1_url", "pixiv.srpr.cc")
        conf.set("spider_config", "s2_url", "pixiv.888718.xyz")
        conf.set("spider_config", "target_url", "pximg.lolicon.run")  # 写入配置参数
        conf.set("spider_config", "r18_mode", 'True')
        conf.set("spider_config", "all_show", 'False')
        conf.set("spider_config", "proxy_flag", 'False')
        conf.set("spider_config", "proxy_website", 'http://demo.spiderpy.cn')
        conf.set("spider_config", "proxy_mode", 'auto')
        conf.set("spider_config", "search_delta_time", '3')
        conf.set("spider_config", "detail_delta_time", '2')
        conf.set("spider_config", "sis_log_level", 'DEBUG')
        conf.set("spider_config", "spider_images_max_count", '1000')
        conf.set("spider_config", "output_video_fps", "24")
        conf.set("spider_config", "output_video_width", "2560")
        conf.set("spider_config", "output_video_height", "1440")
        conf.set("spider_config", "proxy_server_ip", "192.168.199.26")
        conf.set("spider_config", "proxy_server_port", "8080")

        conf.add_section("automatic_config")
        conf.set("automatic_config", "filter_http_url", "js,emoji,svq,_50.png,_50.jpg,no_profile_s.png,block.vv50.de,"
                                                        "square,custom,_50.gif,data:image/png,no_profile.png,common")
        conf.set("automatic_config", "filter_image_url", "s_mode=s_tag,block.vv50.de,tags,square,custom,square,custom,"
                                                         "50.gif,data:image/png,no_profile.png,common")
        conf.set("automatic_config", "zoom_out_scale", "0.9")
        conf.set("automatic_config", "zoom_in_scale", "1.1")
        conf.set("automatic_config", "fire_wall_delay_time", "60")
        conf.set("automatic_config", "download_img_retry_times", "2")
        conf.set("automatic_config", "download_img_time_out", "10")
        conf.set("automatic_config", "detect_timeout_auto", "300")
        conf.set("automatic_config", "chrome_path", "None")
        conf.set("automatic_config", "chrome_version", "1")
        conf.set("automatic_config", "upload_minio_image_Flag", "False")
        conf.set("automatic_config", "allow_replace_domain_flag", 'True')

        conf.add_section("minio_config_selected")
        conf.set("minio_config_selected", "minio_config_id", "1")
        conf.set("minio_config_selected", "minio_server_ip", "121.36.66.145")  # 写入配置参数
        conf.set("minio_config_selected", "minio_server_port", "9000")
        conf.set("minio_config_selected", "minio_account", "minioadmin")
        conf.set("minio_config_selected", "minio_password", "minioadmin")
        conf.set("minio_config_selected", "mark_msg", "minio_config['mark_msg']")
        conf.set("minio_config_selected", "enable", '1')

        conf.add_section("unzip_config")
        conf.set("unzip_config", "SEVEN_ZIP_PATH", "C:/Program Files/7-Zip/7z.exe")
        conf.set("unzip_config", "PASSWORD", "1204")

        conf.write(open(iniPath, 'a+', encoding="utf-8"))
        conf.read(iniPath, 'utf-8')
        # logger.info("config write finished, read test: " + conf.get("spider_config", "visit_url"))
        return True
