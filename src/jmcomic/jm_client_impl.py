#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 客户端实现

提供禁漫漫画网站的客户端实现

注意：此模块已重构，所有实现已移至 clients 子模块
"""

# 为了保持向后兼容性，从新的子模块导入所有类
from .clients import (
    AbstractJmClient,
    JmHtmlClient,
    JmApiClient,
    PhotoConcurrentFetcherProxy,
)

__all__ = [
    'AbstractJmClient',
    'JmHtmlClient',
    'JmApiClient',
    'PhotoConcurrentFetcherProxy',
]
