#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Danbooru2024 采集模块
"""

from .danbooru_client import DanbooruClient, load_character_list as load_character_list_local
from .danbooru_api_spider import DanbooruApiSpider, load_character_list
from .danbooru_mirror_spider import DanbooruMirrorSpider, load_character_list as load_character_list_mirror

__all__ = [
    'DanbooruClient',
    'DanbooruApiSpider',
    'DanbooruMirrorSpider',
    'load_character_list',
]
