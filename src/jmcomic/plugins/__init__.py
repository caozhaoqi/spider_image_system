#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 插件模块

提供各种功能插件
"""

from .base import JmOptionPlugin, PluginValidationException
from .login import JmLoginPlugin
from .usage_log import UsageLogPlugin
from .client_proxy import ClientProxyPlugin
from .favorite_folder import FavoriteFolderPlugin
from .zip_plugin import ZipPlugin
from .send_email import SendEmailPlugin
from .discord import DiscordPlugin
from .telegram import TelegramPlugin

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
