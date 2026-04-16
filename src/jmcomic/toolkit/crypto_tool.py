#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 加密解密工具

提供禁漫加解密相关逻辑
"""

from ..jm_config import JmMagicConstants
from ..jm_exception import ExceptionTool


class JmCryptoTool:
    """加密解密工具"""

    @classmethod
    def token_and_tokenparam(cls, ts, ver=None, secret=None):
        """
        计算禁漫接口的请求headers的token和tokenparam
        
        :param ts: 时间戳
        :param ver: app版本
        :param secret: 密钥
        :return (token, tokenparam)
        """
        if ver is None:
            ver = JmMagicConstants.APP_VERSION

        if secret is None:
            secret = JmMagicConstants.APP_TOKEN_SECRET

        tokenparam = '{},{}'.format(ts, ver)
        token = cls.md5hex(f'{ts}{secret}')

        return token, tokenparam

    @classmethod
    def decode_resp_data(cls, data: str, ts, secret=None) -> str:
        """
        解密接口返回值
        
        :param data: resp.json()['data']
        :param ts: 时间戳
        :param secret: 密钥
        :return: json格式的字符串
        """
        if secret is None:
            secret = JmMagicConstants.APP_DATA_SECRET

        import base64
        data_b64 = base64.b64decode(data)

        key = cls.md5hex(f'{ts}{secret}').encode('utf-8')
        from Crypto.Cipher import AES
        data_aes = AES.new(key, AES.MODE_ECB).decrypt(data_b64)

        data = data_aes[:-data_aes[-1]]
        res = data.decode('utf-8')

        return res

    @classmethod
    def md5hex(cls, key: str):
        ExceptionTool.require_true(isinstance(key, str), 'key参数需为字符串')
        from hashlib import md5
        return md5(key.encode("utf-8")).hexdigest()
