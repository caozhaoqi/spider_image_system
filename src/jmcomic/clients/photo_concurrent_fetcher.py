#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 照片并发获取代理

为了解决 JmApiClient.get_photo_detail 方法的排队调用问题，
实现并发请求photo、album和scramble_id接口
"""

from typing import Dict
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock

from ..jm_client_interface import JmcomicClient, JmPhotoDetail, JmAlbumDetail
from ..jm_toolkit import JmcomicText


class PhotoConcurrentFetcherProxy(JmcomicClient):
    """
    并发获取照片详情的代理客户端
    
    可通过插件 ClientProxyPlugin 启用本类
    """
    client_key = 'photo_concurrent_fetcher_proxy'

    class FutureWrapper:
        def __init__(self, future: Future, after_done_callback):
            self.future = future
            self.done = False
            self._result = None
            self.after_done_callback = after_done_callback

        def result(self):
            if not self.done:
                self._result = self.future.result()
                self.done = True
                self.future = None
                self.after_done_callback()
            return self._result

    def __init__(self, client: JmcomicClient, max_workers=None, executors=None):
        self.client = client
        self.route_notimpl_method_to_internal_client(client)

        if executors is None:
            executors = ThreadPoolExecutor(max_workers)
        self.executors = executors
        self.future_dict: Dict[str, PhotoConcurrentFetcherProxy.FutureWrapper] = {}
        self.lock = Lock()

    def route_notimpl_method_to_internal_client(self, client):
        proxy_methods = {'get_album_detail', 'get_photo_detail'}
        attributes_and_methods = dir(client)
        
        for method in attributes_and_methods:
            if (not method.startswith('_')
                    and callable(getattr(client, method))
                    and method not in proxy_methods):
                setattr(self, method, getattr(client, method))

    def get_album_detail(self, album_id) -> JmAlbumDetail:
        album_id = JmcomicText.parse_to_jm_id(album_id)
        cache_key = f'album_{album_id}'
        future = self.get_future(cache_key, task=lambda: self.client.get_album_detail(album_id))
        return future.result()

    def get_future(self, cache_key, task):
        if cache_key in self.future_dict:
            return self.future_dict[cache_key]

        with self.lock:
            if cache_key in self.future_dict:
                return self.future_dict[cache_key]

            future = self.FutureWrapper(
                self.executors.submit(task),
                after_done_callback=lambda: self.future_dict.pop(cache_key, None)
            )
            self.future_dict[cache_key] = future
            return future

    def get_photo_detail(self, photo_id, fetch_album=True, fetch_scramble_id=True) -> JmPhotoDetail:
        photo_id = JmcomicText.parse_to_jm_id(photo_id)
        client = self.client
        futures = [None, None, None]
        results = [None, None, None]

        # photo_detail
        futures[0] = self.get_future(f'photo_{photo_id}',
                                     lambda: client.get_photo_detail(photo_id, False, False))

        # fetch_album
        if fetch_album:
            futures[1] = self.get_future(f'album_{photo_id}',
                                         lambda: client.get_album_detail(photo_id))

        # fetch_scramble_id
        if fetch_scramble_id and hasattr(client, 'get_scramble_id'):
            futures[2] = self.get_future(f'scramble_id_{photo_id}',
                                         lambda: client.get_scramble_id(photo_id))

        # wait finish
        for i, f in enumerate(futures):
            if f is not None:
                results[i] = f.result()

        # compose
        photo: JmPhotoDetail = results[0]
        album = results[1]
        scramble_id = results[2]

        if album is not None:
            photo.from_album = album
        if scramble_id:
            photo.scramble_id = scramble_id

        return photo
