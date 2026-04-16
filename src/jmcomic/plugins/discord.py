#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic Discord插件

功能：发送Discord通知
"""

from .base import JmOptionPlugin


class DiscordPlugin(JmOptionPlugin):
    """Discord通知插件"""
    plugin_key = 'discord'

    def invoke(self, webhook_url: str, content: str = '', **kwargs) -> None:
        """
        发送Discord通知
        
        :param webhook_url: Discord webhook URL
        :param content: 通知内容
        """
        self.require_param(webhook_url, 'webhook_url不能为空')

        try:
            import requests
        except ImportError:
            self.warning_lib_not_install('requests')
            return

        data = {
            'content': content,
            'username': kwargs.get('username', 'JM Comic Bot'),
        }

        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                self.log('Discord通知发送成功')
            else:
                self.log(f'Discord通知发送失败: {response.status_code}', 'error')
        except Exception as e:
            self.log(f'Discord通知发送失败: {e}', 'error')
