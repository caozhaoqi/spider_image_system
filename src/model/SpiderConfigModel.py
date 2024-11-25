"""Spider configuration model class for storing spider settings"""
import os
import sys
from dataclasses import dataclass
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class SpiderConfigModel:
    """Class representing spider configuration settings"""
    visit_url: str = ''
    s1_url: str = ''  
    s2_url: str = ''
    target_url: str = ''
    r18_mode: bool = False
    all_show: bool = True
    proxy_flag: bool = True
    search_delta_time: int = 7
    detail_delta_time: int = 3
    sis_log_level: str = ''
    spider_images_max_count: int = 0
    output_video_fps: int = 5
    output_video_width: int = 2560
    output_video_height: int = 1440
    proxy_server_ip: str = '192.168.199.26'
    proxy_server_port: int = 8080
