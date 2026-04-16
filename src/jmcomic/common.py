#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 公共工具模块
"""

import os
import logging
import traceback
from loguru import logger
import time
from typing import Optional

def mkdir_if_not_exists(path):
    """创建目录如果不存在
    
    Args:
        path: 目录路径
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"创建目录: {path}")

def jm_log(message, level='info'):
    """JM Comic 日志函数
    
    Args:
        message: 日志消息
        level: 日志级别
    """
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'debug':
        logger.debug(message)
    else:
        logger.info(message)

def field_cache(cache_key: Optional[str] = None, obj=None):
    """字段缓存装饰器
    
    Args:
        cache_key: 缓存键名，如果为None则使用函数名
        obj: 缓存对象，如果为None则使用实例对象
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取实例对象
            self = args[0]
            # 确定缓存对象
            cache_obj = obj or self
            # 生成缓存键
            key = cache_key or func.__name__
            # 检查缓存是否存在
            if not hasattr(cache_obj, '_cache'):
                cache_obj._cache = {}
            if key in cache_obj._cache:
                return cache_obj._cache[key]
            # 调用原函数并缓存结果
            result = func(*args, **kwargs)
            cache_obj._cache[key] = result
            return result
        return wrapper
    return decorator

def time_stamp():
    """获取时间戳
    
    Returns:
        str: 时间戳字符串
    """
    return str(int(time.time()))

def str_to_list(s: str) -> list:
    """字符串转列表
    
    Args:
        s: 字符串
    
    Returns:
        list: 列表
    """
    if not s:
        return []
    return [line.strip() for line in s.split('\n') if line.strip()]

class ProxyBuilder:
    """代理构建器"""
    
    @staticmethod
    def system_proxy():
        """获取系统代理
        
        Returns:
            dict: 代理配置
        """
        return None

class AdvancedDict:
    """高级字典类，允许通过属性访问字典的键"""
    
    def __init__(self, data: dict):
        """初始化
        
        Args:
            data: 字典数据
        """
        self.src_dict = data or {}
        for key, value in self.src_dict.items():
            if isinstance(value, dict):
                setattr(self, key, AdvancedDict(value))
            else:
                setattr(self, key, value)
    
    def __getattr__(self, name):
        """获取属性
        
        Args:
            name: 属性名
        
        Returns:
            Any: 属性值
        """
        return self.src_dict.get(name)
    
    def get(self, key, default=None):
        """获取字典值
        
        Args:
            key: 键
            default: 默认值
        
        Returns:
            Any: 值
        """
        return self.src_dict.get(key, default)

class PackerUtil:
    """打包工具类"""
    
    @staticmethod
    def pack(data, filepath):
        """打包数据到文件
        
        Args:
            data: 数据
            filepath: 文件路径
        """
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    @staticmethod
    def unpack(filepath):
        """从文件解包数据
        
        Args:
            filepath: 文件路径
        
        Returns:
            Any: 数据
        """
        import pickle
        with open(filepath, 'rb') as f:
            return pickle.load(f), filepath

class Postman:
    """HTTP请求客户端"""
    
    def get(self, url, **kwargs):
        """发送GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他参数
        
        Returns:
            Response: 响应对象
        """
        raise NotImplementedError
    
    def post(self, url, data=None, json=None, **kwargs):
        """发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            **kwargs: 其他参数
        
        Returns:
            Response: 响应对象
        """
        raise NotImplementedError

class PostmanProxy:
    """Postman代理类"""
    
    def __init__(self, postman):
        """初始化
        
        Args:
            postman: Postman实例
        """
        self.postman = postman
    
    def get(self, url, **kwargs):
        """发送GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他参数
        
        Returns:
            Response: 响应对象
        """
        return self.postman.get(url, **kwargs)
    
    def post(self, url, data=None, json=None, **kwargs):
        """发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            **kwargs: 其他参数
        
        Returns:
            Response: 响应对象
        """
        return self.postman.post(url, data=data, json=json, **kwargs)

class Postmans:
    """Postman工厂类"""
    
    @classmethod
    def create(cls, data):
        """创建Postman实例
        
        Args:
            data: 配置数据
        
        Returns:
            Postman: Postman实例
        """
        return cls.new_postman(**data.get('meta_data', {}))
    
    @classmethod
    def new_session(cls, **kwargs):
        """创建会话Postman
        
        Args:
            **kwargs: 配置参数
        
        Returns:
            Postman: Postman实例
        """
        import requests
        session = requests.Session()
        if 'headers' in kwargs:
            session.headers.update(kwargs['headers'])
        if 'proxies' in kwargs:
            session.proxies.update(kwargs['proxies'])
        return session
    
    @classmethod
    def new_postman(cls, **kwargs):
        """创建普通Postman
        
        Args:
            **kwargs: 配置参数
        
        Returns:
            Postman: Postman实例
        """
        import requests
        return requests


def fix_filepath(filepath, is_dir=False):
    """修复文件路径
    
    Args:
        filepath: 文件路径
        is_dir: 是否为目录
    
    Returns:
        str: 修复后的文件路径
    """
    # 替换路径中的非法字符
    import re
    filepath = re.sub(r'[<>"|?*]', '', filepath)
    # 处理路径分隔符
    filepath = os.path.normpath(filepath)
    # 如果是目录，确保路径以分隔符结尾
    if is_dir and not filepath.endswith(os.path.sep):
        filepath += os.path.sep
    return filepath


def fix_windir_name(name):
    """修复Windows目录名
    
    Args:
        name: 目录名
    
    Returns:
        str: 修复后的目录名
    """
    # 替换Windows目录名中的非法字符
    import re
    return re.sub(r'[<>"|?*]', '', name)


def traceback_print_exec():
    """打印异常堆栈信息"""
    traceback.print_exc()


def multi_thread_launcher(iter_objs, apply_each_obj_func, wait_finish=True):
    """多线程启动器
    
    Args:
        iter_objs: 迭代对象
        apply_each_obj_func: 应用于每个对象的函数
        wait_finish: 是否等待所有线程完成
    """
    import threading
    threads = []
    for obj in iter_objs:
        t = threading.Thread(target=apply_each_obj_func, args=(obj,))
        t.start()
        threads.append(t)
    
    if wait_finish:
        for t in threads:
            t.join()


def thread_pool_executor(iter_objs, apply_each_obj_func, max_workers):
    """线程池执行器
    
    Args:
        iter_objs: 迭代对象
        apply_each_obj_func: 应用于每个对象的函数
        max_workers: 最大工作线程数
    """
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(apply_each_obj_func, iter_objs)


def file_exists(filepath):
    """检查文件是否存在
    
    Args:
        filepath: 文件路径
    
    Returns:
        bool: 文件是否存在
    """
    return os.path.exists(filepath)
