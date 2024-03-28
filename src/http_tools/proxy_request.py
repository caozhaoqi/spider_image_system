#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loguru import logger
import requests
from run import constants


@logger.catch
def get_proxy(url):
    """
    proxy
    :param url:
    :return:
    """
    try:
        response = requests.get(url)
    except Exception as e:
        response = None
        logger.error(f"unknown error: {e}")
    return response


@logger.catch
def get_proxy_item():
    """

    :return:
    """
    get_proxy_api = constants.proxy_website + '/get'
    while True:
        ret = get_proxy(get_proxy_api)
        if ret:
            logger.info(f"get proxy host and port: {ret}")
            ret = ret.text
            break
        else:
            logger.error("no proxy use, please modify config.ini file proxy_flag = False or check proxy server status!")
            ret = None
            break
    return ret
