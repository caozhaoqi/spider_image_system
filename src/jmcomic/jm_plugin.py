#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 插件模块

提供各种功能插件

注意：此模块已重构，所有实现已移至 plugins 子模块
"""

# 为了保持向后兼容性，从新的子模块导入所有类
from .plugins import (
    JmOptionPlugin,
    PluginValidationException,
    JmLoginPlugin,
    UsageLogPlugin,
    ClientProxyPlugin,
    FavoriteFolderPlugin,
    ZipPlugin,
    SendEmailPlugin,
    DiscordPlugin,
    TelegramPlugin,
)

__all__ = [
    'JmOptionPlugin',
    'PluginValidationException',
    'JmLoginPlugin',
    'UsageLogPlugin',
    'ClientProxyPlugin',
    'FavoriteFolderPlugin',
    'ZipPlugin',
    'SendEmailPlugin',
    'DiscordPlugin',
    'TelegramPlugin',
]
