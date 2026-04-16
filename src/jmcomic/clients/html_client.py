#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic HTML 客户端

基于网页实现的JmClient
"""

from typing import Optional

from .abstract_client import AbstractJmClient
from ..jm_client_interface import *
from ..jm_toolkit import JmcomicText, JmPageTool, PatternTool
from ..jm_exception import ExceptionTool
from ..jm_config import JmModuleConfig, JmMagicConstants, jm_log


def parse_unicode_escape_text(text: str) -> str:
    """
    解析Unicode转义文本
    """
    import codecs
    return codecs.decode(text, 'unicode_escape')


class JmHtmlClient(AbstractJmClient):
    """基于网页实现的JmClient"""
    
    client_key = 'html'
    func_to_cache = ['search', 'fetch_detail_entity']

    API_SEARCH = '/search/photos'
    API_CATEGORY = '/albums'

    def add_favorite_album(self, album_id, folder_id='0'):
        data = {'album_id': album_id, 'fid': folder_id}
        resp = self.get_jm_html('/ajax/favorite_album', data=data)
        res = resp.json()

        if res['status'] != 1:
            msg = parse_unicode_escape_text(res['msg'])
            error_msg = PatternTool.match_or_default(msg, JmcomicText.pattern_ajax_favorite_msg, msg)
            self.raise_request_error(resp, error_msg)

        return resp

    def get_album_detail(self, album_id) -> JmAlbumDetail:
        return self.fetch_detail_entity(album_id, 'album')

    def get_photo_detail(self, photo_id, fetch_album=True, fetch_scramble_id=True) -> JmPhotoDetail:
        photo = self.fetch_detail_entity(photo_id, 'photo')
        if fetch_album:
            photo.from_album = self.get_album_detail(photo.album_id)
        return photo

    def fetch_detail_entity(self, jmid, prefix):
        jmid = JmcomicText.parse_to_jm_id(jmid)
        resp = self.get_jm_html(f"/{prefix}/{jmid}")
        
        if prefix == 'album':
            return JmcomicText.analyse_jm_album_html(resp.text)
        if prefix == 'photo':
            return JmcomicText.analyse_jm_photo_html(resp.text)

    def search(self, search_query: str, page: int, main_tag: int,
               order_by: str, time: str, category: str, sub_category: Optional[str]) -> JmSearchPage:
        params = {
            'main_tag': main_tag,
            'search_query': search_query,
            'page': page,
            'o': order_by,
            't': time,
        }
        url = self.build_search_url(self.API_SEARCH, category, sub_category)
        resp = self.get_jm_html(self.append_params_to_url(url, params), allow_redirects=True)

        if resp.redirect_count != 0 and '/album/' in resp.url:
            album = JmcomicText.analyse_jm_album_html(resp.text)
            return JmSearchPage.wrap_single_album(album)
        else:
            return JmPageTool.parse_html_to_search_page(resp.text)

    @classmethod
    def build_search_url(cls, base: str, category: str, sub_category: Optional[str]):
        if category == JmMagicConstants.CATEGORY_ALL:
            return base
        if sub_category is None:
            return f'{base}/{category}'
        return f'{base}/{category}/sub/{sub_category}'

    def categories_filter(self, page: int, time: str, category: str,
                          order_by: str, sub_category: Optional[str] = None) -> JmCategoryPage:
        params = {'page': page, 'o': order_by, 't': time}
        url = self.build_search_url(self.API_CATEGORY, category, sub_category)
        resp = self.get_jm_html(self.append_params_to_url(url, params), allow_redirects=True)
        return JmPageTool.parse_html_to_category_page(resp.text)

    def login(self, username, password, id_remember='on', login_remember='on'):
        data = {
            'username': username,
            'password': password,
            'id_remember': id_remember,
            'login_remember': login_remember,
            'submit_login': '',
        }
        resp = self.post('/login', data=data, allow_redirects=False)

        if resp.status_code != 200:
            ExceptionTool.raises_resp(f'登录失败，状态码为{resp.status_code}', resp)

        orig_cookies = self.get_meta_data('cookies') or {}
        new_cookies = dict(resp.cookies)
        if 'AVS' in orig_cookies and 'AVS' not in new_cookies:
            return resp

        self['cookies'] = new_cookies
        self._username = username
        return resp

    def favorite_folder(self, page=1, order_by=JmMagicConstants.ORDER_BY_LATEST,
                        folder_id='0', username='') -> JmFavoritePage:
        if username == '':
            ExceptionTool.require_true(self._username is not None, 'favorite_folder方法需要传username参数')
            username = self._username

        resp = self.get_jm_html(
            f'/user/{username}/favorite/albums',
            params={'page': page, 'o': order_by, 'folder_id': folder_id}
        )
        return JmPageTool.parse_html_to_favorite_page(resp.text)

    def get_jm_html(self, url, require_200=True, **kwargs):
        resp = self.get(url, **kwargs)
        if require_200 and resp.status_code != 200:
            self.check_special_http_code(resp)
            self.raise_request_error(resp)
        self.require_resp_success_else_raise(resp, url)
        return resp

    def update_request_with_specify_domain(self, kwargs: dict, domain: Optional[str], is_image=False):
        if is_image:
            return
        latest_headers = kwargs.get('headers', None)
        base_headers = self.get_meta_data('headers', None) or JmModuleConfig.new_html_headers(domain)
        base_headers.update(latest_headers or {})
        kwargs['headers'] = base_headers

    @classmethod
    def raise_request_error(cls, resp, msg: Optional[str] = None):
        if msg is None:
            msg = f"请求失败，响应状态码为{resp.status_code}，URL=[{resp.url}]"
            if len(resp.text) < 200:
                msg += f"响应文本=[{resp.text}]"
            else:
                msg += f'响应文本过长(len={len(resp.text)})，不打印'
        ExceptionTool.raises_resp(msg, resp)

    def album_comment(self, video_id, comment, originator='', status='true',
                      comment_id=None, **kwargs) -> JmAlbumCommentResp:
        data = {
            'video_id': video_id,
            'comment': comment,
            'originator': originator,
            'status': status,
        }
        if comment_id is not None:
            data.pop('status')
            data['comment_id'] = comment_id
            data['is_reply'] = 1
            data['forum_subject'] = 1

        jm_log('album.comment', f'{video_id}: [{comment}]' + (f' to ({comment_id})' if comment_id else ''))
        resp = self.post('/ajax/album_comment', data=data)
        ret = JmAlbumCommentResp(resp)
        jm_log('album.comment', f'{video_id}: [{comment}] ← ({ret.model().cid})')
        return ret

    @classmethod
    def require_resp_success_else_raise(cls, resp, url: str):
        resp_url: str = resp.url
        cls.check_special_text(resp)

        if resp.redirect_count == 0 or '/error/' not in resp_url:
            return

        if resp_url.endswith('/error/album_missing') and not url.endswith('/error/album_missing'):
            ExceptionTool.raise_missing(resp, JmcomicText.parse_to_jm_id(url))
        if resp_url.endswith('/error/user_missing') and not url.endswith('/error/user_missing'):
            ExceptionTool.raises_resp('此用戶名稱不存在，或者你没有登录，請再次確認使用名稱', resp)
        if resp_url.endswith('/error/invalid_module') and not url.endswith('/error/invalid_module'):
            ExceptionTool.raises_resp('發生了無法預期的錯誤。若問題持續發生，請聯繫客服支援', resp)

    @classmethod
    def check_special_text(cls, resp):
        html = resp.text
        url = resp.url

        if len(html) > 500:
            return

        for content, reason in JmModuleConfig.JM_ERROR_RESPONSE_TEXT.items():
            if content not in html:
                continue
            cls.raise_request_error(resp, f'{reason}' + (f': {url}' if url else ''))

    @classmethod
    def check_special_http_code(cls, resp):
        code = resp.status_code
        url = resp.url
        error_msg = JmModuleConfig.JM_ERROR_STATUS_CODE.get(int(code), None)
        if error_msg is None:
            return

        cls.raise_request_error(
            resp,
            f"请求失败，响应状态码为{code}，原因为: [{error_msg}]" + (f'URL=[{url}]' if url else '')
        )