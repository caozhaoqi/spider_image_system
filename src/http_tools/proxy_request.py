#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
def get_proxy_item():
    """

    :return:
    """
    ret = get_proxy(constants.proxy_website)
    if ret:
        if ret['check_count'] > 1000:
            return ret['proxy']
        else:
            logger.warning(f"check count < 1000, skip: {ret}")
    else:
        logger.error("get proxy error, proxy result null!")
        return None
