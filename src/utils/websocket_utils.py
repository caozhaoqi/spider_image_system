#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket工具函数 - 用于实时推送爬虫进度
"""

import json
from loguru import logger
from run import constants


async def send_progress_update(progress_data):
    """
    向所有连接的WebSocket客户端发送进度更新
    
    :param progress_data: 进度数据字典，包含以下字段：
        - type: 消息类型 (spider_progress, download_progress, etc.)
        - keyword: 当前爬取的关键词
        - current_count: 当前已采集数量
        - total_count: 总数量（可选）
        - status: 状态 (running, completed, error, stopped)
        - message: 消息内容
        - page: 当前页码
    """
    if not constants.websocket_connections:
        return
    
    message = json.dumps(progress_data, ensure_ascii=False)
    
    # 发送给所有连接的客户端
    disconnected = []
    for conn in constants.websocket_connections:
        try:
            await conn.send_text(message)
        except Exception as e:
            logger.warning(f"WebSocket发送失败: {e}")
            disconnected.append(conn)
    
    # 移除断开的连接
    for conn in disconnected:
        constants.websocket_connections.remove(conn)


def add_websocket_connection(conn):
    """添加WebSocket连接"""
    constants.websocket_connections.append(conn)
    logger.info(f"WebSocket连接已添加，当前连接数: {len(constants.websocket_connections)}")


def remove_websocket_connection(conn):
    """移除WebSocket连接"""
    if conn in constants.websocket_connections:
        constants.websocket_connections.remove(conn)
        logger.info(f"WebSocket连接已移除，当前连接数: {len(constants.websocket_connections)}")
