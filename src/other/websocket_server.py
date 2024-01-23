import asyncio
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger

import asyncio
import websockets

IP_ADDR = "0.0.0.0"
IP_PORT = "8888"


@logger.catch
# 握手，通过接收hello，发送"123"来进行双方的握手。
async def server_hands(websocket):
    """
    receive client send msg
    :param websocket:
    :return:
    """
    while True:
        recv_text = await websocket.recv()
        logger.debug("recv_text=" + recv_text)
        # logger.debug("connected success")
        return True


# 接收从客户端发来的消息并处理，再返给客户端ok
@logger.catch
async def server_recv(websocket):
    """

    :param websocket:
    :return:
    """
    while True:
        recv_text = await websocket.recv()
        await websocket.send("ok!!!")
        logger.debug("recv:", recv_text)


# 握手并且接收数据
@logger.catch
async def server_run(websocket, path):
    """
    
    :param websocket: 
    :param path: 
    :return: 
    """
    # logger.debug(path)
    await server_hands(websocket)

    # await server_recv(websocket)


# main function
if __name__ == '__main__':
    logger.debug("======server main begin======")
    server = websockets.serve(server_run, IP_ADDR, 9999)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
