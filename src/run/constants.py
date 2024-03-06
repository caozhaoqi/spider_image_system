import os
import sys

from file.file_process import scan_img_txt
from file.ini_file_spider import check_ini_config, read_ini_config, ini_file_path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查默认配置项
check_ini_config()

# spider image url 图片抓取进程是否停止工作
stop_spider_url_flag = True
# download_image_flag
stop_download_image_flag = True
# dialog show
edit_config_msg_visible = False
about_message_lookup_visible = False
online_look_image_visible = False
auto_play_image_visible = False
start_auto_play_flag = False
performance_monitor_visible = False
genshin_impact_view_visible = False
log_analyze_visible = False
face_detect_flag = False
convert_folder_name_flag = False
online_show_image = False
# firewall_flag
firewall_flag = False

# spider mode
spider_mode = 'manual'
# process image
process_image_flag = False
# zip download flag
download_finish_flag = True
# download link
download_video_link_flag = False
# download_gif_zip_flag
download_gif_zip_flag = False
# unzip_generate_video_flag
unzip_generate_video_flag = False
# 数据存储路径
data_path = os.path.realpath('./data')
# 基础路径
basic_path = os.path.realpath('./')
# online img list
online_img_list = scan_img_txt(data_path)
# online cur show img index
cur_show_img_index = 0
# 抓取总图片数目 实时统计
spider_images_current_count = 0
check_images_flag = False
category_image_flag = False

# 输出 video 帧率
output_video_fps = int(read_ini_config(ini_file_path, "spider_config", "output_video_fps"))
# 输出 video 宽度
output_video_width = int(read_ini_config(ini_file_path, "spider_config", "output_video_width"))
# 输出 video 高度
output_video_height = int(read_ini_config(ini_file_path, "spider_config", "output_video_height"))
# 抓取图片最大值
spider_images_max_count = int(read_ini_config(ini_file_path, "spider_config", "spider_images_max_count"))


# log level
sis_log_level = read_ini_config(ini_file_path, "spider_config", "sis_log_level")

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
# 当前图片名
filter_http_url = read_ini_config(ini_file_path, "automatic_config", "filter_http_url")
# filter image url
filter_image_url = read_ini_config(ini_file_path, "automatic_config", "filter_image_url")
# image zoom in
zoom_in_scale = float(read_ini_config(ini_file_path, "automatic_config", "zoom_in_scale"))
# zoom_out_scale
zoom_out_scale = float(read_ini_config(ini_file_path, "automatic_config", "zoom_out_scale"))
# chrome path
chrome_path = read_ini_config(ini_file_path, "automatic_config", "chrome_path")
# upload_minio_image_Flag
upload_minio_image_Flag = read_ini_config(ini_file_path, "automatic_config", "upload_minio_image_Flag")
# allow re place image domain
allow_replace_domain_flag = read_ini_config(ini_file_path, "automatic_config", "allow_replace_domain_flag")
# fire_wall_delay_time
fire_wall_delay_time = int(read_ini_config(ini_file_path, "automatic_config", "fire_wall_delay_time"))
# download image fail retry times
download_img_retry_times = int(read_ini_config(ini_file_path, "automatic_config", "download_img_retry_times"))
# retry time out
download_img_time_out = int(read_ini_config(ini_file_path, "automatic_config", "download_img_time_out"))
sis_server_version = "v1.0.9-beta.1.240306"
build_date = "2024-03-06 18:00"
publish_date = "2024-03-06 18:30"
