#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
    拥有代理功能的爬虫request

"""
from loguru import logger

import requests
from run import constants


@logger.catch
def get_proxy(url, ):
    """
    proxy
    :param url:
    :return:
    """
    response = requests.get(url).json()
    return response


@logger.catch
def valid_proxy_ip(ret):
    """

    :param ret:
    :return:
    """
    pass


@logger.catch
def get_proxy_item():
    """

    :return:
    """
    get_proxy_api = constants.proxy_website + '/get'
    while True:
        ret = get_proxy(get_proxy_api)
        if ret:
            if ret['check_count'] > 10:
                logger.success(f"cur proxy msg: {ret}")
                ret = ret['proxy']
                # valid_proxy_ip(ret)
                break
            else:
                logger.warning(f"check count < 1000, skip: {ret}")
                continue
        else:
            logger.error("no proxy use, please modify config.ini file proxy_flag = False or check proxy server status!")
            ret = None
            break
    return ret
