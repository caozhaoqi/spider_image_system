#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 客户端代理插件

功能：使用代理客户端替换原有的客户端
"""

from .base import JmOptionPlugin


class ClientProxyPlugin(JmOptionPlugin):
    """客户端代理插件"""
    plugin_key = 'client_proxy'

    def invoke(self, proxy_client_key: str, **kwargs) -> None:
        """
        使用代理客户端替换原有的客户端
        
        :param proxy_client_key: 代理客户端的key
        :param kwargs: 代理客户端的其他参数
        """
        from ..clients import PhotoConcurrentFetcherProxy
        
        # 获取原有的客户端
        original_client = self.option.build_jm_client()
        
        # 根据代理客户端key创建代理客户端
        if proxy_client_key == 'photo_concurrent_fetcher_proxy':
            proxy_client = PhotoConcurrentFetcherProxy(
                client=original_client,
                **kwargs
            )
        else:
            raise ValueError(f"未知的代理客户端key: {proxy_client_key}")
        
        # 替换原有的客户端
        self.option.jm_client = proxy_client
        
        self.log(f'已使用代理客户端: {proxy_client_key}')
