#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 抽象客户端基类

提供域名管理、发请求、重试机制、日志、缓存等功能
"""

from typing import List, Dict, Optional

from ..jm_client_interface import *
from ..jm_toolkit import JmcomicText
from ..jm_config import JmModuleConfig, jm_log


class AbstractJmClient(
    JmcomicClient,
    PostmanProxy,
):
    """抽象基类，实现了域名管理、发请求、重试机制、日志、缓存等功能"""
    
    client_key = '__just_for_placeholder_do_not_use_me__'
    func_to_cache = []

    def __init__(self,
                 postman: Postman,
                 domain_list: List[str],
                 retry_times: int = 0,
                 ):
        """
        创建JM客户端

        :param postman: 负责实现HTTP请求的对象，持有cookies、headers、proxies等信息
        :param domain_list: 禁漫域名
        :param retry_times: 重试次数
        """
        super().__init__(postman)
        self.retry_times = retry_times
        self.domain_list = domain_list
        self.CLIENT_CACHE = None
        self._username = None
        self.enable_cache()
        self.after_init()

    def after_init(self):
        pass

    def get(self, url, **kwargs):
        return self.request_with_retry(self.postman.get, url, **kwargs)

    def post(self, url, **kwargs):
        return self.request_with_retry(self.postman.post, url, **kwargs)

    def of_api_url(self, api_path, domain):
        return JmcomicText.format_url(api_path, domain)

    def get_jm_image(self, img_url) -> JmImageResp:
        def callback(resp):
            resp = JmImageResp(resp)
            resp.require_success()
            return resp
        return self.get(img_url, callback=callback, headers=JmModuleConfig.new_html_headers())

    def request_with_retry(self,
                           request,
                           url,
                           domain_index: int = 0,
                           retry_count: int = 0,
                           callback=None,
                           **kwargs,
                           ):
        """
        支持重试和切换域名的机制

        如果url包含了指定域名，则不会切换域名，例如图片URL。
        """
        if domain_index >= len(self.domain_list):
            return self.fallback(request, url, domain_index, retry_count, **kwargs)

        url_backup = url

        if url.startswith('/'):
            domain = self.domain_list[domain_index]
            url = self.of_api_url(url, domain)
            self.update_request_with_specify_domain(kwargs, domain)
            jm_log(self.log_topic(), self.decode(url))
        else:
            self.update_request_with_specify_domain(kwargs, None, True)

        if domain_index != 0 or retry_count != 0:
            jm_log('req.retry',
                   ', '.join([
                       f'次数: [{retry_count}/{self.retry_times}]',
                       f'域名: [{domain_index} of {self.domain_list}]',
                       f'路径: [{url}]',
                   ]))

        try:
            resp = request(url, **kwargs)
            if callback is not None:
                resp = callback(resp)
            resp = self.raise_if_resp_should_retry(resp)
            return resp
        except Exception as e:
            if self.retry_times == 0:
                raise e
            self.before_retry(e, kwargs, retry_count, url)

        if retry_count < self.retry_times:
            return self.request_with_retry(request, url_backup, domain_index, retry_count + 1, callback, **kwargs)
        else:
            return self.request_with_retry(request, url_backup, domain_index + 1, 0, callback, **kwargs)

    def raise_if_resp_should_retry(self, resp):
        """在最后返回之前，还可以判断resp是否重试"""
        return resp

    def update_request_with_specify_domain(self, kwargs: dict, domain: Optional[str], is_image: bool = False):
        """域名自动切换时，用于更新请求参数的回调"""
        pass

    def log_topic(self):
        return self.client_key

    def before_retry(self, e, kwargs, retry_count, url):
        jm_log('req.error', str(e))

    def enable_cache(self):
        def make_key(args, kwds, typed,
                     kwd_mark=(object(),),
                     fasttypes={int, str},
                     tuple=tuple, type=type, len=len):
            key = args
            if kwds:
                key += kwd_mark
                for item in kwds.items():
                    key += item
            if typed:
                key += tuple(type(v) for v in args)
                if kwds:
                    key += tuple(type(v) for v in kwds.values())
            elif len(key) == 1 and type(key[0]) in fasttypes:
                return key[0]
            return hash(key)

        def wrap_func_with_cache(func_name, cache_field_name):
            if hasattr(self, cache_field_name):
                return

            func = getattr(self, func_name)

            def cache_wrapper(*args, **kwargs):
                cache = self.CLIENT_CACHE
                if cache is None:
                    return func(*args, **kwargs)

                key = make_key(args, kwargs, False)
                sentinel = object()
                result = cache.get(key, sentinel)
                if result is not sentinel:
                    return result

                result = func(*args, **kwargs)
                cache[key] = result
                return result

            setattr(self, func_name, cache_wrapper)

        for func_name in self.func_to_cache:
            wrap_func_with_cache(func_name, f'__{func_name}.cache.dict__')

    def set_cache_dict(self, cache_dict: Optional[Dict]):
        self.CLIENT_CACHE = cache_dict

    def get_cache_dict(self):
        return self.CLIENT_CACHE

    def get_domain_list(self):
        return self.domain_list

    def set_domain_list(self, domain_list: List[str]):
        self.domain_list = domain_list

    def fallback(self, request, url, domain_index, retry_count, **kwargs):
        msg = f"请求重试全部失败: [{url}], {self.domain_list}"
        jm_log('req.fallback', msg)
        ExceptionTool.raises(msg, {}, RequestRetryAllFailException)

    def append_params_to_url(self, url, params):
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{url}?{query_string}"

    def decode(self, url: str):
        if not JmModuleConfig.FLAG_DECODE_URL_WHEN_LOGGING or '/search/' not in url:
            return url
        from urllib.parse import unquote
        return unquote(url.replace('+', ' '))
