#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 文本工具

提供文本解析和处理功能
"""

import os
from re import compile, Pattern, Match
from typing import List, Dict, Callable, Union

from ..jm_exception import ExceptionTool
from ..jm_entity import JmPhotoDetail, JmAlbumDetail
from ..jm_config import JmModuleConfig
from ..common import mkdir_if_not_exists, jm_log


class JmcomicText:
    """禁漫文本解析工具"""

    pattern_jm_domain = compile(r'https://([\w.-]+)')
    pattern_jm_pa_id = [
        (compile(r'(photos?|album)/(\d+)'), 2),
        (compile(r'id=(\d+)'), 1),
    ]
    pattern_html_jm_pub_domain = compile(r'[\w-]+\.\w+/?\w+')

    pattern_html_photo_photo_id = compile(r'<meta property="og:url" content=".*?/photo/(\d+)/?.*?">')
    pattern_html_photo_scramble_id = compile(r'var scramble_id = (\d+);')
    pattern_html_photo_name = compile(r'<title>([\s\S]*?)\|.*</title>')
    pattern_html_photo_data_original_domain = compile(r'src="https://(.*?)/media/albums/blank')
    pattern_html_photo_data_original_0 = compile(r'data-original="(.*?)"[^>]*?id="album_photo[^>]*?data-page="0"')
    pattern_html_photo_tags = compile(r'<meta name="keywords"[\s\S]*?content="(.*?)"')
    pattern_html_photo_series_id = compile(r'var series_id = (\d+);')
    pattern_html_photo_sort = compile(r'var sort = (\d+);')
    pattern_html_photo_page_arr = compile(r'var page_arr = (.*?);')

    pattern_html_album_album_id = compile(r'<span class="number">.*?：JM(\d+)</span>')
    pattern_html_album_scramble_id = compile(r'var scramble_id = (\d+);')
    pattern_html_album_name = compile(r'<h1 class="book-name" id="book-name">([\s\S]*?)</h1>')
    pattern_html_album_episode_list = compile(r'data-album="(\d+)">\n *?<li.*?>\n *'
                                              r'第(\d+)話\n([\s\S]*?)\n *'
                                              r'<[\s\S]*?>(\d+-\d+-\d+).*?')
    pattern_html_album_page_count = compile(r'<span class="pagecount">.*?(\d+)</span>')
    pattern_html_album_pub_date = compile(r'>上架日期 : (.*?)</span>')
    pattern_html_album_update_date = compile(r'>更新日期 : (.*?)</span>')

    pattern_html_album_works = [
        compile(r'<span itemprop="author" data-type="works">([\s\S]*?)</span>'),
        compile(r'<a[^>]*?>(.*?)</a>')
    ]
    pattern_html_album_actors = [
        compile(r'<span itemprop="author" data-type="actor">([\s\S]*?)</span>'),
        compile(r'<a[^>]*?>(.*?)</a>')
    ]
    pattern_html_album_tags = [
        compile(r'<span itemprop="genre" data-type="tags">([\s\S]*?)</span>'),
        compile(r'<a[^>]*?>(.*?)</a>')
    ]
    pattern_html_album_authors = [
        compile(r'作者： *<span itemprop="author" data-type="author">([\s\S]*?)</span>'),
        compile(r"<a[^>]*?>(.*?)</a>"),
    ]
    pattern_html_album_likes = compile(r'<span id="albim_likes_\d+">(.*?)</span>')
    pattern_html_album_views = compile(r'<span>(.*?)</span>\n *<span>(次觀看|观看次数)</span>')
    pattern_html_album_comment_count = compile(r'<div class="badge"[^>]*?id="total_video_comments">(\d+)</div>'), 0

    pattern_ajax_favorite_msg = compile(r'</button>(.*?)</div>')

    @classmethod
    def parse_to_jm_domain(cls, text: str):
        if text.startswith(JmModuleConfig.PROT):
            return cls.pattern_jm_domain.search(text)[1]
        return text

    @classmethod
    def parse_to_jm_id(cls, text) -> str:
        if isinstance(text, int):
            return str(text)

        ExceptionTool.require_true(isinstance(text, str), f"无法解析jm车号, 参数类型为: {type(text)}")

        if text.isdigit():
            return text

        ExceptionTool.require_true(len(text) >= 2, f"无法解析jm车号, 文本太短: {text}")

        c0 = text[0]
        c1 = text[1]
        if (c0 == 'J' or c0 == 'j') and (c1 == 'M' or c1 == 'm'):
            return text[2:]
        else:
            for p, i in cls.pattern_jm_pa_id:
                match = p.search(text)
                if match is not None:
                    return match[i]
            ExceptionTool.raises(f"无法解析jm车号, 文本为: {text}")

    @classmethod
    def analyse_jm_pub_html(cls, html: str, domain_keyword=('jm', 'comic')) -> List[str]:
        domain_ls = cls.pattern_html_jm_pub_domain.findall(html)
        return list(filter(
            lambda domain: any(kw in domain for kw in domain_keyword),
            domain_ls
        ))

    @classmethod
    def analyse_jm_photo_html(cls, html: str) -> JmPhotoDetail:
        return cls.reflect_new_instance(
            html,
            "pattern_html_photo_",
            JmModuleConfig.photo_class()
        )

    @classmethod
    def analyse_jm_album_html(cls, html: str) -> JmAlbumDetail:
        return cls.reflect_new_instance(
            html,
            "pattern_html_album_",
            JmModuleConfig.album_class()
        )

    @classmethod
    def reflect_new_instance(cls, html: str, cls_field_prefix: str, clazz: type):
        def match_field(field_name: str, pattern: Union[Pattern, List[Pattern]], text):
            if isinstance(pattern, list):
                last_pattern = pattern[len(pattern) - 1]
                for i in range(0, len(pattern) - 1):
                    match: Match = pattern[i].search(text)
                    if match is None:
                        return None
                    text = match[0]
                return last_pattern.findall(text)

            if field_name.endswith("_list"):
                return pattern.findall(text)
            else:
                match = pattern.search(text)
                if match is not None:
                    return match[1]
                return None

        field_dict = {}
        pattern_name: str
        for pattern_name, pattern in cls.__dict__.items():
            if not pattern_name.startswith(cls_field_prefix):
                continue

            if isinstance(pattern, tuple):
                pattern, default = pattern
            else:
                default = None

            field_name = pattern_name[pattern_name.index(cls_field_prefix) + len(cls_field_prefix):]
            field_value = match_field(field_name, pattern, html)

            if field_value is None:
                if default is None:
                    ExceptionTool.raises_regex(
                        f"文本没有匹配上字段：字段名为'{field_name}'，pattern: [{pattern}]"
                        + (f"\n响应文本=[{html}]" if len(html) < 200 else
                           f'响应文本过长(len={len(html)})，不打印'),
                        html=html,
                        pattern=pattern,
                    )
                else:
                    field_value = default

            field_dict[field_name] = field_value

        return clazz(**field_dict)

    @classmethod
    def format_url(cls, path, domain):
        ExceptionTool.require_true(isinstance(domain, str) and len(domain) != 0, '域名为空')
        if domain.startswith(JmModuleConfig.PROT):
            return f'{domain}{path}'
        return f'{JmModuleConfig.PROT}{domain}{path}'

    @classmethod
    def format_album_url(cls, album_id: str, domain: str = None):
        domain = domain or JmModuleConfig.domain
        return cls.format_url(f'/album/{album_id}', domain)

    @classmethod
    def format_photo_url(cls, photo_id: str, domain: str = None):
        domain = domain or JmModuleConfig.domain
        return cls.format_url(f'/photo/{photo_id}', domain)
    
    @classmethod
    def parse_to_abspath(cls, path):
        """解析为绝对路径
        
        Args:
            path: 路径字符串或None
            
        Returns:
            str: 绝对路径
        """
        if path is None:
            return os.getcwd()
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        mkdir_if_not_exists(path)
        return path