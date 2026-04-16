#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 资源使用日志插件

功能：监控资源使用情况
"""

import threading
from typing import Optional

from .base import JmOptionPlugin


class UsageLogPlugin(JmOptionPlugin):
    """资源使用日志插件"""
    plugin_key = 'usage_log'

    def invoke(self, **kwargs) -> None:
        t = threading.Thread(
            target=self.monitor_resource_usage,
            kwargs=kwargs,
            daemon=True,
        )
        t.start()
        self.set_thread_as_option_attr(t)

    def set_thread_as_option_attr(self, t):
        """线程留痕"""
        name = f'thread_{self.plugin_key}'
        thread_ls: Optional[list] = getattr(self.option, name, None)
        if thread_ls is None:
            setattr(self.option, name, [t])
        else:
            thread_ls.append(t)

    def monitor_resource_usage(
            self,
            interval=1,
            enable_warning=True,
            warning_cpu_percent=70,
            warning_mem_percent=70,
            warning_thread_count=100,
    ):
        try:
            import psutil
        except ImportError:
            self.warning_lib_not_install('psutil')
            return

        from time import sleep
        from threading import active_count
        process = psutil.Process()

        cpu_percent = None
        thread_count = None
        mem_usage = None

        def warning():
            warning_msg_list = []
            if cpu_percent >= warning_cpu_percent:
                warning_msg_list.append(f'进程占用cpu过高 ({cpu_percent}% >= {warning_cpu_percent}%)')

            mem_percent = psutil.virtual_memory().percent
            if mem_percent >= warning_mem_percent:
                warning_msg_list.append(f'系统内存占用过高 ({mem_percent}% >= {warning_mem_percent}%)')

            if thread_count >= warning_thread_count:
                warning_msg_list.append(f'线程数过多 ({thread_count} >= {warning_thread_count})')

            if warning_msg_list:
                self.log('\n'.join(warning_msg_list), 'warning')

        while True:
            sleep(interval)
            cpu_percent = process.cpu_percent()
            thread_count = active_count()
            mem_usage = process.memory_info().rss / 1024 / 1024

            if enable_warning:
                warning()

            self.log(f'cpu: {cpu_percent}%, mem: {mem_usage}MB, thread: {thread_count}')
