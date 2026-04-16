#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 收藏夹插件

功能：管理收藏夹
"""

from .base import JmOptionPlugin


class FavoriteFolderPlugin(JmOptionPlugin):
    """收藏夹插件"""
    plugin_key = 'favorite_folder'

    def invoke(self, folder_id='0', **kwargs) -> None:
        """
        设置默认收藏夹
        
        :param folder_id: 收藏夹ID
        """
        self.option.favorite_folder_id = folder_id
        self.log(f'设置默认收藏夹: {folder_id}')
