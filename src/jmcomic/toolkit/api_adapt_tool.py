#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic API适配工具

负责把移动端的api返回值，适配为标准的实体类
"""

from ..jm_entity import JmAlbumDetail, JmPhotoDetail, AdvancedDict
from ..jm_exception import ExceptionTool
from ..jm_config import JmModuleConfig


class JmApiAdaptTool:
    """API适配工具"""

    field_adapter = {
        JmAlbumDetail: [
            'likes',
            'tags',
            'works',
            'actors',
            'related_list',
            'name',
            ('id', 'album_id'),
            ('author', 'authors'),
            ('total_views', 'views'),
            ('comment_total', 'comment_count'),
        ],
        JmPhotoDetail: [
            'name',
            'series_id',
            'tags',
            ('id', 'photo_id'),
            ('images', 'page_arr'),
        ]
    }

    @classmethod
    def parse_entity(cls, data: dict, clazz: type):
        adapter = cls.get_adapter(clazz)

        fields = {}
        for k in adapter:
            if isinstance(k, str):
                v = data[k]
                fields[k] = v
            elif isinstance(k, tuple):
                k, rename_k = k
                v = data[k]
                fields[rename_k] = v

        if issubclass(clazz, JmAlbumDetail):
            cls.post_adapt_album(data, clazz, fields)
        else:
            cls.post_adapt_photo(data, clazz, fields)

        return clazz(**fields)

    @classmethod
    def get_adapter(cls, clazz: type):
        for k, v in cls.field_adapter.items():
            if issubclass(clazz, k):
                return v
        ExceptionTool.raises(f'不支持的类型: {clazz}')

    @classmethod
    def post_adapt_album(cls, data: dict, _clazz: type, fields: dict):
        series = data['series']
        episode_list = []
        for chapter in series:
            chapter = AdvancedDict(chapter)
            episode_list.append(
                (chapter.id, chapter.sort, chapter.name, None)
            )
        fields['episode_list'] = episode_list
        for it in 'scramble_id', 'page_count', 'pub_date', 'update_date':
            fields[it] = '0'

    @classmethod
    def post_adapt_photo(cls, data: dict, _clazz: type, fields: dict):
        sort = 1
        series: list = data['series']
        for chapter in series:
            chapter = AdvancedDict(chapter)
            if int(chapter.id) == int(data['id']):
                sort = chapter.sort
                break

        fields['sort'] = sort
        import random
        fields['data_original_domain'] = random.choice(JmModuleConfig.DOMAIN_IMAGE_LIST)
