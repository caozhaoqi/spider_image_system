#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic Telegram插件

功能：发送Telegram通知
"""

from .base import JmOptionPlugin


class TelegramPlugin(JmOptionPlugin):
    """Telegram通知插件"""
    plugin_key = 'telegram'

    def invoke(self, bot_token: str, chat_id: str, message: str = '', **kwargs) -> None:
        """
        发送Telegram通知
        
        :param bot_token: Telegram Bot Token
        :param chat_id: Telegram Chat ID
        :param message: 消息内容
        """
        self.require_param(bot_token, 'bot_token不能为空')
        self.require_param(chat_id, 'chat_id不能为空')

        try:
            import requests
        except ImportError:
            self.warning_lib_not_install('requests')
            return

        api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': kwargs.get('parse_mode', 'HTML'),
        }

        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                self.log('Telegram通知发送成功')
            else:
                self.log(f'Telegram通知发送失败: {response.status_code}', 'error')
        except Exception as e:
            self.log(f'Telegram通知发送失败: {e}', 'error')
