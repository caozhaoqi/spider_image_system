#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loguru import logger
import requests
from requests.exceptions import RequestException
from run import constants


@logger.catch
def get_proxy(url: str) -> Optional[requests.Response]:
    """
    Send GET request to proxy URL and return response
    
    Args:
        url: Proxy API URL
        
    Returns:
        Optional[requests.Response]: Response object if successful, None otherwise
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


@logger.catch
def get_proxy_item() -> Optional[str]:
    """
    Get proxy details from proxy API
    
    Returns:
        Optional[str]: Proxy details if successful, None otherwise
    """
    proxy_api = f"{constants.proxy_website}/get"
    
    response = get_proxy(proxy_api)
    if response:
        proxy_details = response.text
        logger.info(f"Retrieved proxy: {proxy_details}")
        return proxy_details
    
    logger.error("Failed to get proxy. Please check proxy server status or disable proxy in config.ini")
    return None
