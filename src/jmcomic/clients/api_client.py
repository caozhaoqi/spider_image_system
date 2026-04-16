#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic API 客户端

基于禁漫移动端（APP）实现的JmClient
"""

from threading import Lock
from typing import Optional

from .abstract_client import AbstractJmClient
from ..jm_client_interface import *
from ..jm_toolkit import JmcomicText, JmPageTool, JmApiAdaptTool, JmCryptoTool, PatternTool
from ..jm_exception import ExceptionTool
from ..jm_config import JmModuleConfig, JmMagicConstants, jm_log
from ..common import time_stamp, field_cache


class JmApiClient(AbstractJmClient):
    """基于禁漫移动端（APP）实现的JmClient"""
    
    client_key = 'api'
    func_to_cache = ['search', 'fetch_detail_entity']

    API_SEARCH = '/search'
    API_CATEGORIES_FILTER = '/categories/filter'
    API_ALBUM = '/album'
    API_CHAPTER = '/chapter'
    API_SCRAMBLE = '/chapter_view_template'
    API_FAVORITE = '/favorite'

    def search(self, search_query: str, page: int, main_tag: int,
               order_by: str, time: str, category: str, sub_category: Optional[str]) -> JmSearchPage:
        params = {
            'main_tag': main_tag,
            'search_query': search_query,
            'page': page,
            'o': order_by,
            't': time,
        }
        resp = self.req_api(self.append_params_to_url(self.API_SEARCH, params))
        data = resp.model_data
        if data.get('redirect_aid', None) is not None:
            aid = data.redirect_aid
            return JmSearchPage.wrap_single_album(self.get_album_detail(aid))
        return JmPageTool.parse_api_to_search_page(data)

    def categories_filter(self, page: int, time: str, category: str,
                          order_by: str, sub_category: Optional[str] = None):
        o = f'{order_by}_{time}' if time != JmMagicConstants.TIME_ALL else order_by
        params = {'page': page, 'order': '', 'c': category, 'o': o}
        resp = self.req_api(self.append_params_to_url(self.API_CATEGORIES_FILTER, params))
        return JmPageTool.parse_api_to_search_page(resp.model_data)

    def get_album_detail(self, album_id) -> JmAlbumDetail:
        return self.fetch_detail_entity(album_id, JmModuleConfig.album_class())

    def get_photo_detail(self, photo_id, fetch_album=True, fetch_scramble_id=True) -> JmPhotoDetail:
        photo: JmPhotoDetail = self.fetch_detail_entity(photo_id, JmModuleConfig.photo_class())
        if fetch_album or fetch_scramble_id:
            self.fetch_photo_additional_field(photo, fetch_album, fetch_scramble_id)
        return photo

    def get_scramble_id(self, photo_id, album_id=None):
        cache = JmModuleConfig.SCRAMBLE_CACHE
        if photo_id in cache:
            return cache[photo_id]
        if album_id is not None and album_id in cache:
            return cache[album_id]

        scramble_id = self.fetch_scramble_id(photo_id)
        cache[photo_id] = scramble_id
        if album_id is not None:
            cache[album_id] = scramble_id
        return scramble_id

    def fetch_detail_entity(self, jmid, clazz):
        jmid = JmcomicText.parse_to_jm_id(jmid)
        url = self.API_ALBUM if issubclass(clazz, JmAlbumDetail) else self.API_CHAPTER
        resp = self.req_api(self.append_params_to_url(url, {'id': jmid}))
        return JmApiAdaptTool.parse_entity(resp.res_data, clazz)

    def fetch_scramble_id(self, photo_id):
        photo_id: str = JmcomicText.parse_to_jm_id(photo_id)
        resp = self.req_api(
            self.API_SCRAMBLE,
            params={
                'id': photo_id,
                'mode': 'vertical',
                'page': '0',
                'app_img_shunt': '1',
                'express': 'off',
                'v': time_stamp(),
            },
            require_success=False,
        )
        scramble_id = PatternTool.match_or_default(resp.text, JmcomicText.pattern_html_album_scramble_id, None)
        if scramble_id is None:
            jm_log('api.scramble', f'未匹配到scramble_id，响应文本：{resp.text}')
            scramble_id = str(JmMagicConstants.SCRAMBLE_220980)
        return scramble_id

    def fetch_photo_additional_field(self, photo: JmPhotoDetail, fetch_album: bool, fetch_scramble_id: bool):
        if fetch_album:
            photo.from_album = self.get_album_detail(photo.album_id)
        if fetch_scramble_id:
            photo.scramble_id = self.get_scramble_id(photo.photo_id, photo.album_id)

    def setting(self) -> JmApiResp:
        resp = self.req_api('/setting')
        setting_ver = str(resp.model_data.version)
        if setting_ver > JmMagicConstants.APP_VERSION and JmModuleConfig.FLAG_USE_VERSION_NEWER_IF_BEHIND:
            jm_log('api.setting', f'change APP_VERSION from [{JmMagicConstants.APP_VERSION}] to [{setting_ver}]')
            JmMagicConstants.APP_VERSION = setting_ver
        return resp

    def login(self, username, password) -> JmApiResp:
        resp = self.req_api('/login', False, data={'username': username, 'password': password})
        cookies = dict(resp.resp.cookies)
        cookies.update({'AVS': resp.res_data['s']})
        self['cookies'] = cookies
        return resp

    def favorite_folder(self, page=1, order_by=JmMagicConstants.ORDER_BY_LATEST,
                        folder_id='0', username='') -> JmFavoritePage:
        resp = self.req_api(
            self.API_FAVORITE,
            params={'page': page, 'folder_id': folder_id, 'o': order_by}
        )
        return JmPageTool.parse_api_to_favorite_page(resp.model_data)

    def add_favorite_album(self, album_id, folder_id='0'):
        resp = self.req_api('/favorite', data={'aid': album_id})
        self.require_resp_status_ok(resp)
        return resp

    def require_resp_status_ok(self, resp: JmApiResp):
        data = resp.model_data
        if data.status == 'ok':
            ExceptionTool.raises_resp(data.msg, resp)

    def req_api(self, url, get=True, require_success=True, **kwargs) -> JmApiResp:
        ts = self.decide_headers_and_ts(kwargs, url)
        if get:
            resp = self.get(url, **kwargs)
        else:
            resp = self.post(url, **kwargs)
        resp = JmApiResp(resp, ts)
        if require_success:
            self.require_resp_success(resp, url)
        return resp

    def update_request_with_specify_domain(self, kwargs: dict, domain: Optional[str], is_image=False):
        if is_image:
            kwargs['headers'] = {**JmModuleConfig.APP_HEADERS_TEMPLATE, **JmModuleConfig.APP_HEADERS_IMAGE}

    def decide_headers_and_ts(self, kwargs, url):
        if url == self.API_SCRAMBLE:
            ts = time_stamp()
            token, tokenparam = JmCryptoTool.token_and_tokenparam(ts, secret=JmMagicConstants.APP_TOKEN_SECRET_2)
        elif JmModuleConfig.FLAG_USE_FIX_TIMESTAMP:
            ts, token, tokenparam = JmModuleConfig.get_fix_ts_token_tokenparam()
        else:
            ts = time_stamp()
            token, tokenparam = JmCryptoTool.token_and_tokenparam(ts)

        headers = kwargs.get('headers', None) or JmModuleConfig.APP_HEADERS_TEMPLATE.copy()
        headers.update({'token': token, 'tokenparam': tokenparam})
        kwargs['headers'] = headers
        return ts

    @classmethod
    def require_resp_success(cls, resp: JmApiResp, url: Optional[str] = None):
        resp.require_success()
        data = resp.model().data
        if isinstance(data, list) and len(data) == 0:
            ExceptionTool.raise_missing(resp, JmcomicText.parse_to_jm_id(url))

    def raise_if_resp_should_retry(self, resp):
        if isinstance(resp, JmResp):
            return resp

        code = resp.status_code
        if code >= 500:
            msg = JmModuleConfig.JM_ERROR_STATUS_CODE.get(code, f'HTTP状态码: {code}')
            ExceptionTool.raises_resp(f"禁漫API异常响应, {msg}", resp)

        url = resp.request.url
        if self.API_SCRAMBLE in url:
            return resp

        text = resp.text
        for char in text:
            if char not in (' ', '\n', '\t'):
                ExceptionTool.require_true(
                    char == '{',
                    f'请求不是json格式，强制重试！响应文本: [{resp.text}]'
                )
                return resp
        ExceptionTool.raises_resp(f'响应无数据！request_url=[{url}]', resp)

    def after_init(self):
        if JmModuleConfig.FLAG_API_CLIENT_REQUIRE_COOKIES:
            self.ensure_have_cookies()

    client_init_cookies_lock = Lock()

    def ensure_have_cookies(self):
        if self.get_meta_data('cookies'):
            return
        with self.client_init_cookies_lock:
            if self.get_meta_data('cookies'):
                return
            self['cookies'] = self.get_cookies()

    @field_cache("APP_COOKIES", obj=JmModuleConfig)
    def get_cookies(self):
        resp = self.setting()
        return dict(resp.resp.cookies)