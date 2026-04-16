#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 插件基类

提供插件的基础功能
"""

import os
import os.path
from typing import List, Any

from ..jm_option import JmOption
from ..common import jm_log, file_exists


class PluginValidationException(Exception):
    """插件验证异常"""
    
    def __init__(self, plugin: 'JmOptionPlugin', msg: str):
        self.plugin = plugin
        self.msg = msg


class JmOptionPlugin:
    """JM Option 插件基类"""
    
    plugin_key: str

    def __init__(self, option: JmOption):
        self.option = option
        self.log_enable = True
        self.delete_original_file = False

    def invoke(self, **kwargs) -> None:
        """
        执行插件的功能
        :param kwargs: 给插件的参数
        """
        raise NotImplementedError

    @classmethod
    def build(cls, option: JmOption) -> 'JmOptionPlugin':
        """
        创建插件实例
        :param option: JmOption对象
        """
        return cls(option)

    def log(self, msg, topic=None):
        if self.log_enable is not True:
            return

        jm_log(
            topic=f'plugin.{self.plugin_key}' + (f'.{topic}' if topic is not None else ''),
            msg=msg
        )

    def require_param(self, case: Any, msg: str):
        """
        专门用于校验参数的方法，会抛出特定异常，由option拦截根据策略进行处理

        :param case: 条件
        :param msg: 报错信息
        """
        if case:
            return
        raise PluginValidationException(self, msg)

    def warning_lib_not_install(self, lib: str):
        msg = (f'插件`{self.plugin_key}`依赖库: {lib}，请先安装{lib}再使用。'
               f'安装命令: [pip install {lib}]')
        import warnings
        warnings.warn(msg)

    def execute_deletion(self, paths: List[str]):
        """
        删除文件和文件夹
        :param paths: 路径列表
        """
        if self.delete_original_file is not True:
            return

        for p in paths:
            if not file_exists(p):
                continue

            if os.path.isdir(p):
                os.rmdir(p)
                self.log(f'删除文件夹: {p}', 'remove')
            else:
                os.remove(p)
                self.log(f'删除原文件: {p}', 'remove')

    def execute_cmd(self, cmd):
        """
        执行shell命令
        :param cmd: shell命令
        """
        return os.system(cmd)

    def execute_multi_line_cmd(self, cmd: str):
        import subprocess
        subprocess.run(cmd, shell=True, check=True)

    def enter_wait_list(self):
        self.option.need_wait_plugins.append(self)

    def leave_wait_list(self):
        self.option.need_wait_plugins.remove(self)

    def wait_until_finish(self):
        pass
