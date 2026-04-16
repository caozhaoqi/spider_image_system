#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 页面解析工具

提供页面解析功能
"""

from re import compile

from .pattern_tool import PatternTool
from ..jm_entity import JmSearchPage, JmFavoritePage, AdvancedDict


class JmPageTool:
    """页面解析工具"""

    pattern_html_search_shorten_for = compile(r'<div class="well well-sm">([\s\S]*)<div class="row">')
    pattern_html_search_album_info_list = compile(
        r'<a href="/album/(\d+)/[\s\S]*?title="(.*?)"([\s\S]*?)<div class="title-truncate tags .*>([\s\S]*?)</div>'
    )
    pattern_html_category_album_info_list = compile(
        r'<a href="/album/(\d+)/[^>]*>[^>]*?'
        r'title="(.*?)"[^>]*>[ \n]*</a>[ \n]*'
        r'<div class="label-loveicon">([\s\S]*?)'
        r'<div class="clearfix">'
    )
    pattern_html_search_tags = compile(r'<a[^>]*?>(.*?)</a>')
    pattern_html_search_error = compile(r'<fieldset>\n<legend>(.*?)</legend>\n<div class=.*?>\n(.*?)\n</div>\n</fieldset>')
    pattern_html_search_total = compile(r'class="text-white">(\d+)</span> A漫.'), 0

    pattern_html_favorite_content = compile(
        r'<div id="favorites_album_[^>]*?>[\s\S]*?'
        r'<a href="/album/(\d+)/">[\s\S]*?'
        r'<div class="video-title title-truncate">([^<]*?)'
        r'</div>'
    )
    pattern_html_favorite_total = compile(r' : (\d+)[^/]*/\D*(\d+)')
    pattern_html_favorite_folder_list = [
        compile(r'<select class="user-select" name="movefolder-fid">([\s\S]*)</select>'),
        compile(r'<option value="(\d+)">([^<]*?)</option>')
    ]

    @classmethod
    def parse_html_to_search_page(cls, html: str) -> JmSearchPage:
        PatternTool.require_not_match(
            html,
            cls.pattern_html_search_error,
            msg_func=lambda match: '{}: {}'.format(match[1], match[2])
        )

        html = PatternTool.require_match(
            html,
            cls.pattern_html_search_shorten_for,
            msg='未匹配到搜索结果',
        )

        content = []
        total = int(PatternTool.match_or_default(html, *cls.pattern_html_search_total))

        album_info_list = cls.pattern_html_search_album_info_list.findall(html)

        for (album_id, title, _label_category_text, tag_text) in album_info_list:
            tags = cls.pattern_html_search_tags.findall(tag_text)
            content.append((
                album_id, {
                    'name': title,
                    'tags': tags
                }
            ))

        return JmSearchPage(content, total)

    @classmethod
    def parse_html_to_category_page(cls, html: str) -> JmSearchPage:
        content = []
        total = int(PatternTool.match_or_default(html, *cls.pattern_html_search_total))

        album_info_list = cls.pattern_html_category_album_info_list.findall(html)

        for (album_id, title, tag_text) in album_info_list:
            tags = cls.pattern_html_search_tags.findall(tag_text)
            content.append((
                album_id, {
                    'name': title,
                    'tags': tags
                }
            ))

        return JmSearchPage(content, total)

    @classmethod
    def parse_html_to_favorite_page(cls, html: str) -> JmFavoritePage:
        total = int(PatternTool.require_match(
            html,
            cls.pattern_html_favorite_total,
            '未匹配到收藏夹的本子总数',
        ))

        content = cls.pattern_html_favorite_content.findall(html)
        content = [
            (aid, {'name': atitle})
            for aid, atitle in content
        ]

        p1, p2 = cls.pattern_html_favorite_folder_list
        folder_list_text = PatternTool.require_match(html, p1, '未匹配到收藏夹列表')
        folder_list_raw = p2.findall(folder_list_text)
        folder_list = [{'name': fname, 'FID': fid} for fid, fname in folder_list_raw]

        return JmFavoritePage(content, folder_list, total)

    @classmethod
    def parse_api_to_search_page(cls, data: AdvancedDict) -> JmSearchPage:
        total: int = int(data.total or 0)
        content = cls.adapt_content(data.content)
        return JmSearchPage(content, total)

    @classmethod
    def parse_api_to_favorite_page(cls, data: AdvancedDict) -> JmFavoritePage:
        total: int = int(data.total)
        content = cls.adapt_content(data.list)
        folder_list = data.get('folder_list', [])
        return JmFavoritePage(content, folder_list, total)

    @classmethod
    def adapt_content(cls, content):
        def adapt_item(item: AdvancedDict):
            item: dict = item.src_dict
            item.setdefault('tags', [])
            return item

        content = [
            (item.id, adapt_item(item)) for item in content
        ]
        return content
