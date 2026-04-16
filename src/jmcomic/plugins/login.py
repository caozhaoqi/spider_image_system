#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 登录插件

功能：登录禁漫，并保存登录后的cookies，让所有client都带上此cookies
"""

from .base import JmOptionPlugin
from ..jm_config import JmModuleConfig


class JmLoginPlugin(JmOptionPlugin):
    """登录插件"""
    plugin_key = 'login'

    def invoke(self, username: str, password: str, impl=None) -> None:
        self.require_param(username, '用户名不能为空')
        self.require_param(password, '密码不能为空')

        client = self.option.build_jm_client(impl=impl)
        client.login(username, password)

        cookies = dict(client['cookies'])
        self.option.update_cookies(cookies)
        JmModuleConfig.APP_COOKIES = cookies

        self.log('登录成功')
