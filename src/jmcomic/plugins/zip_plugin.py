#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic ZIP插件

功能：将下载的文件打包成ZIP
"""

import os
import zipfile

from .base import JmOptionPlugin


class ZipPlugin(JmOptionPlugin):
    """ZIP打包插件"""
    plugin_key = 'zip'

    def invoke(self, level='photo', filename='{album_id}/{photo_id}.zip', **kwargs) -> None:
        """
        将下载的文件打包成ZIP
        
        :param level: 打包级别，'photo'或'album'
        :param filename: ZIP文件名模板
        """
        self.level = level
        self.filename_template = filename
        self.delete_original_file = kwargs.get('delete_original_file', False)

    def zip_photo(self, photo, image_paths):
        """打包单个章节"""
        if self.level != 'photo':
            return

        zip_path = self.filename_template.format(
            album_id=photo.album_id,
            photo_id=photo.photo_id,
            photo_title=photo.title,
        )

        self._create_zip(image_paths, zip_path)
        self.execute_deletion(image_paths)

    def zip_album(self, album, photo_paths):
        """打包整个本子"""
        if self.level != 'album':
            return

        zip_path = self.filename_template.format(
            album_id=album.album_id,
            album_title=album.title,
        )

        self._create_zip(photo_paths, zip_path)
        self.execute_deletion(photo_paths)

    def _create_zip(self, paths, zip_path):
        """创建ZIP文件"""
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in paths:
                if os.path.exists(path):
                    arcname = os.path.basename(path)
                    zf.write(path, arcname)

        self.log(f'创建ZIP: {zip_path}')
