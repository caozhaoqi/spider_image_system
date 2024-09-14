"""
sqlite utils 

struct 
--------------------------------------
table name pix name
id name role_name src page index other
1 1_.png malni http 1 1 .
--------------------------------------

"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

import sqlite3


@logger.catch
def create_database(database_name):
    """
    """
    con = sqlite3.connect(database_name)
    return con


@logger.catch
def create_table(con, table_name, columns):
    """
    """
    cur = con.cursor()

    # Create table
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({columns})''')

    # Save (commit) the changes
    # cur.executemany("insert into characters(c) values (?)", theIter)

    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    # con.close()


@logger.catch
def sql_execute(con, sql):
    """
    """
    cur = con.cursor()

    # Insert a row of data
    cur.execute(sql)

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    # con.close()


@logger.catch
def sql_select(con, sql):
    """
    """
    ret = []
    cur = con.cursor()

    cur.execute(sql)
    for row in cur:
        print(row)
        ret.append(row)
    con.close()
    return ret


@logger.catch
def image_data_insert(data_list, conn):
    """

    """
    # data_list_pix = []
    sql_insert_value_pix = "INSERT INTO pix_images (id, name, role_name, src, page, pix_index, mark) \
                        VALUES (1, 'John', '1121', 'John', '1121', 'John', '1121');"
    sql_execute(conn, sql_insert_value_pix)


@logger.catch
def pix_image_select(conn):
    """

    """
    select_sql_pix = "select * from pix_images"
    sql_select(conn, select_sql_pix)


@logger.catch
def table_create_init():
    """

    """
    conn = create_database("sis_db.db")
    # table_struct = []
    columns = 'id TEXT, name TEXT, role_name TEXT, src TEXT, page TEXT, pix_index TEXT, mark TEXT'
    create_table(conn, "pix_images", columns)
    data_list_pix = []
    # sql_insert_value_pix = "INSERT INTO pix_images (id, name, role_name, src, page, pix_index, mark) \
    #                    VALUES (1, 'John', '1121', 'John', '1121', 'John', '1121');"
    # sql_execute(conn, sql_insert_value_pix)


if __name__ == '__main__':
    conn = create_database("sis_db.db")
    select_sql_pix = "select * from pix_images"
    sql_select(conn, select_sql_pix)
