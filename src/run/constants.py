import os
import sys

from file.ini_file_spider import check_ini_config, read_ini_config, ini_file_path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查默认配置项
check_ini_config()
# 当前图片名
filter_http_url = read_ini_config(ini_file_path, "spider_config", "filter_http_url")
filter_image_url = read_ini_config(ini_file_path, "spider_config", "filter_image_url")
# spider image url 图片抓取进程是否停止工作
stop_spider_url_flag = True
# download_image_flag
stop_download_image_flag = True
# firewall_flag
firewall_flag = False
# fire_wall_delay_time
fire_wall_delay_time = int(read_ini_config(ini_file_path, "spider_config", "fire_wall_delay_time"))
# spider mode
spider_mode = 'manual'
# process -image
process_image_flag = False
# zip download flag
download_finish_flag = True
# download link
download_video_link_flag = False
# download_gif_zip_flag
download_gif_zip_flag = False
# unzip_generate_video_flag
unzip_generate_video_flag = False
# 输出 video 帧率
output_video_fps = int(read_ini_config(ini_file_path, "spider_config", "output_video_fps"))
# 输出 video 宽度
output_video_width = int(read_ini_config(ini_file_path, "spider_config", "output_video_width"))
# 输出 video 高度
output_video_height = int(read_ini_config(ini_file_path, "spider_config", "output_video_height"))
# 抓取图片最大值
spider_images_max_count = int(read_ini_config(ini_file_path, "spider_config", "spider_images_max_count"))
# 抓取总图片数目 实时统计
spider_images_current_count = 0
# image zoom in
zoom_in_scale = float(read_ini_config(ini_file_path, "spider_config", "zoom_in_scale"))
# zoom_out_scale
zoom_out_scale = float(read_ini_config(ini_file_path, "spider_config", "zoom_out_scale"))
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
# mirror url
target_url = read_ini_config(ini_file_path, "spider_config", "target_url")
# search keyword and mode
r18_mode = read_ini_config(ini_file_path, "spider_config", "r18_mode")
# all show
all_show = read_ini_config(ini_file_path, "spider_config", "all_show")
# proxy config
proxy_flag = read_ini_config(ini_file_path, "spider_config", "proxy_flag")
# 代理服务器地址
proxy_server_ip = read_ini_config(ini_file_path, "spider_config", "proxy_server_ip")
# 代理服务器端口
proxy_server_port = int(read_ini_config(ini_file_path, "spider_config", "proxy_server_port"))
# 搜索延迟时间
search_delta_time = int(read_ini_config(ini_file_path, "spider_config", "search_delta_time"))
# 详情页等待时间
detail_delta_time = int(read_ini_config(ini_file_path, "spider_config", "detail_delta_time"))
sis_server_version = "v1.0.5_beta"
build_date = "2024-02-03 12:00"
publish_date = "2024-02-03 12:00"
