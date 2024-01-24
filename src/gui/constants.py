# position url
import os

from utils.ini_file_spider import read_ini_config, ini_file_path, check_ini_config

# 检查默认配置项
check_ini_config()
# 当前图片名
# spider image flag
spider_image_flag = False
# download_image_flag
download_image_flag = False
# process -image
process_image_flag = False
#
output_video_fps = 5
#
output_video_width = 1920
#
output_video_height = 1080
# 抓取图片最大值
spider_images_max_count = read_ini_config(ini_file_path, "spider_config", "spider_images_max_count")
# log level
sis_log_level = read_ini_config(ini_file_path, "spider_config", "sis_log_level")
# 数据存储路径
data_path = os.path.realpath('.\\data')
# 访问网址
visit_url = read_ini_config(ini_file_path, "spider_config", "visit_url")
# 图片服务器地址
s1_url = read_ini_config(ini_file_path, "spider_config", "s1_url")
# 备份图片服务器地址
s2_url = read_ini_config(ini_file_path, "spider_config", "s2_url")
# s3_url = 'sd.2021.host'
# https://i.pixivcat.com/c/360x360_70/custom-thumb/img/2024/01/20/19/45/39/115330738_p0_custom1200.jpg
# https://pximg.lolicon.run/img-master/img/2024/01/20/19/45/39/115330738_p0_master1200.jpg
# mirror url
target_url = read_ini_config(ini_file_path, "spider_config", "target_url")
# search keyword and mode
# keyword_search = ''
r18_mode = read_ini_config(ini_file_path, "spider_config", "r18_mode")
all_show = read_ini_config(ini_file_path, "spider_config", "all_show")
# proxy config
proxy_flag = read_ini_config(ini_file_path, "spider_config", "proxy_flag")
search_delta_time = int(read_ini_config(ini_file_path, "spider_config", "search_delta_time"))
detail_delta_time = int(read_ini_config(ini_file_path, "spider_config", "detail_delta_time"))
need_time = (7 + 3) * 61 / 60  # second control spider speed 20 + 5 -> 7 + 3 (min)
