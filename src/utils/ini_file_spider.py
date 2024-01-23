import configparser
import os
import sys

from src.utils.SpiderConfigModel import SpiderConfigModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

ini_path = os.path.join(os.getcwd(), f'./config/')
ini_file_path = os.path.join(os.getcwd(), f'./config/config.ini')


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
    return entity


@logger.catch
def write_minio_config_to_file(minio_config):
    """
    ini 配置文件写入
    :param minio_config: 元组 notice
    :return:
    """
    iniPath = os.path.realpath(ini_file_path)  # 读取生成后运行时的临时文件目录
    logger.info("generate file path：" + iniPath)
    conf = configparser.ConfigParser()
    if os.path.exists(iniPath):
        os.remove(iniPath)
    logger.warning("Not Found config ini file , creating ini file ....")
    if not os.path.exists(ini_path):
        os.makedirs(ini_path)
        logger.debug("dir not exists ,create dir")
    # tes = open(iniPath, 'a+')
    # tes.close()
    conf.read(iniPath, 'utf-8')
    logger.info("start generate config ini file :")

    conf.add_section("spider_config")
    conf.set("spider_config", "s2_url", minio_config.s2_url)
    conf.set("spider_config", "visit_url", minio_config.visit_url)
    conf.set("spider_config", "s1_url", minio_config.s1_url)
    conf.set("spider_config", "target_url", minio_config.target_url)  # 写入配置参数
    conf.set("spider_config", "r18_mode", minio_config.r18_mode)
    conf.set("spider_config", "all_show", minio_config.all_show)
    conf.set("spider_config", "proxy_flag", minio_config.proxy_flag)
    conf.set("spider_config", "search_delta_time", str(minio_config.search_delta_time))
    conf.set("spider_config", "detail_delta_time", str(minio_config.detail_delta_time))
    # conf.set(minio_config.minio_config_id, "minio_server_ip", minio_config.minio_server_ip)
    # tes.write(conf.values())
    conf.write(open(iniPath, 'a+', encoding="utf-8"))
    conf.read(iniPath, 'utf-8')
    logger.info("config write finished , read test , current use minio server ip : " + conf.get("spider_config",
                                                                                                "visit_url"))
    # logger.info("minio use "+" port:" + conf.get(
    #     "spider_config", "minio_server_port"))


@logger.catch
def read_ini_config(file_name, section, value_key):
    """
    读取指定配置文件
    :param file_name: ini file name
    :param section: ini file section name
    :param value_key: ini file content name
    :return: select value
    """
    # file_name = "../config/config.ini"

    # Writing Data
    config = configparser.ConfigParser()

    config.read(file_name, encoding="utf-8")
    keys = [
        "host",
        "user",
        "port",
        "password",
        "port"
    ]
    # for key in keys:
    try:
        value = config.get(section, value_key)
        # logger.info("read ini file :" + file_name + ", ini file config content : " + config.get(section, value_key))
        return value
    except configparser.NoSectionError as e:
        # logger.info("normal")
        logger.error("Error! section: " + section + ", value_key :" + value_key + ", value error content: " + str(e))
        return "log_dir"
    except configparser.NoOptionError:
        logger.error(f"No option '{section}' in section , please re input config key''" + value_key)
        return ""


@logger.catch
def check_ini_config():
    """
    系统启动引入默认配置
    :return:
    """
    # iniPath = str(os.path.dirname(sys.path[0]) + '\\config\\config.ini')  # 读取生成后运行时的临时文件目录
    # iniPath = iniPath.replace("\\", "\\\\")  # 此步不要省
    # cur_path = os.path.abspath(__file__)
    # parent_path = os.path.abspath(os.path.dirname(cur_path) + os.path.sep + "..")
    # file_path = os.path.join(parent_path, 'config\\config.ini')
    # logger.info("generate file path：" + file_path)
    iniPath = os.path.realpath('.\\config\\config.ini')  # 读取生成后运行时的临时文件目录
    logger.info("generate file path：" + iniPath)
    conf = configparser.ConfigParser()
    if os.path.exists(iniPath):  # 此步判断环境测试未生成临时文件时调用配置文件
        conf.read(iniPath, 'utf-8')
        # return "complete"
    else:
        logger.warning("Not Found config ini file , creating ini file ....")
        if not os.path.exists(".\\config"):
            os.makedirs(".\\config")
            logger.debug("dir not exists ,create dir")
        # tes = open(iniPath, 'a+')
        # tes.close()
        conf.read(iniPath, 'utf-8')
        logger.info("start generate config ini file :")

        conf.add_section("spider_config")
        conf.set("spider_config", "visit_url", "pixiv.net")
        conf.set("spider_config", "s2_url", "s.pximg.net")
        conf.set("spider_config", "s1_url", "i.pximg.net")
        conf.set("spider_config", "target_url", " pixiv.322333.xyz")  # 写入配置参数
        conf.set("spider_config", "r18_mode", 'False')
        conf.set("spider_config", "all_show", 'True')
        conf.set("spider_config", "proxy_flag", 'True')
        conf.set("spider_config", "search_delta_time", '7')
        conf.set("spider_config", "detail_delta_time", '3')

        # tes.write(conf.values())
        conf.write(open(iniPath, 'a+', encoding="utf-8"))
        conf.read(iniPath, 'utf-8')
        logger.info("config write finished , read test : " + conf.get("spider_config", "source_url"))
        # return "wait"
    #
    # if __name__ == '__main__':
    #     read_ini_config("../config/config.ini", "spider_config", "host")
    # write_config_ini()
