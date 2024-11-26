"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from loguru import logger
import requests
from run import constants

# WxPusher配置
WXPUSHER_CONFIG = {
    "APP_TOKEN": "AT_83TZKCOVuq7OJ2WSVCRZuFyZwuxnphYP",
    "USER_UID": "UID_uQwquKqBNPWTloEbEbPL6gq1wbRj",
    "API_URL": "https://wxpusher.zjiecode.com/api/send/message",
    "WEBSITE_URL": "https://caozhaoqi.github.io"
}


@logger.catch
def wx_push_content(content: str) -> bool:
    """推送消息到微信
    
    Args:
        content: 消息内容
        
    Returns:
        bool: 推送是否成功
    """
    if not constants.wechat_push_flag:
        logger.warning("微信消息推送功能未开启,跳过推送")
        return False

    try:
        logger.debug(f"准备推送微信消息: {content}")

        payload = {
            "appToken": WXPUSHER_CONFIG["APP_TOKEN"],
            "content": content,
            "summary": "消息摘要",
            "contentType": 1,
            "uids": [WXPUSHER_CONFIG["USER_UID"]],
            "url": WXPUSHER_CONFIG["WEBSITE_URL"],
            "verifyPay": False,
            "verifyPayType": 0
        }

        response = requests.post(
            WXPUSHER_CONFIG["API_URL"],
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 1000:
            logger.debug(f"微信消息推送成功: {result}")
            return True
            
        logger.error(f"微信消息推送失败: {result}")
        return False
        
    except Exception as e:
        logger.error(f"微信消息推送出错: {e}")
        return False
