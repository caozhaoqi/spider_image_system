"""SQLite数据库工具模块

数据表结构
--------------------------------------
表名: pix_images
列名    说明
id      唯一标识
name    图片名称
role_name 角色名称  
src     图片来源URL
page    页码
index   序号
mark    备注
--------------------------------------
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Any

sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
from loguru import logger


@logger.catch
def create_database(database_name: str) -> sqlite3.Connection:
    """创建并连接SQLite数据库
    
    Args:
        database_name: 数据库文件名
        
    Returns:
        数据库连接对象
    """
    return sqlite3.connect(database_name)


@logger.catch
def create_table(conn: sqlite3.Connection, table_name: str, columns: str) -> None:
    """创建数据表
    
    Args:
        conn: 数据库连接
        table_name: 表名
        columns: 列定义字符串
    """
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({columns})''')
    conn.commit()


@logger.catch
def sql_execute(conn: sqlite3.Connection, sql: str) -> None:
    """执行SQL语句
    
    Args:
        conn: 数据库连接
        sql: SQL语句
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


@logger.catch
def sql_select(conn: sqlite3.Connection, sql: str) -> List[Tuple]:
    """执行查询SQL语句
    
    Args:
        conn: 数据库连接
        sql: SQL查询语句
        
    Returns:
        查询结果列表
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        logger.debug(row)
    conn.close()
    return results


@logger.catch
def image_data_insert(data_list: List[Any], conn: sqlite3.Connection) -> None:
    """插入图片数据
    
    Args:
        data_list: 图片数据列表
        conn: 数据库连接
    """
    sql = """INSERT INTO pix_images 
             (id, name, role_name, src, page, pix_index, mark)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    cursor = conn.cursor()
    cursor.executemany(sql, data_list)
    conn.commit()


@logger.catch
def pix_image_select(conn: sqlite3.Connection) -> List[Tuple]:
    """查询所有图片数据
    
    Args:
        conn: 数据库连接
        
    Returns:
        图片数据列表
    """
    return sql_select(conn, "SELECT * FROM pix_images")


@logger.catch
def table_create_init() -> None:
    """初始化数据表"""
    conn = create_database("sis_db.db")
    columns = '''
        id TEXT,
        name TEXT, 
        role_name TEXT,
        src TEXT,
        page TEXT,
        pix_index TEXT,
        mark TEXT
    '''
    create_table(conn, "pix_images", columns)
    conn.close()


if __name__ == '__main__':
    conn = create_database("sis_db.db")
    pix_image_select(conn)
