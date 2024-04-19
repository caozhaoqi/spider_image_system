import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time

from loguru import logger
from run import constants


class SISThreading(threading.Thread):
    def __init__(self, target, args=(), kwargs=None, *args_thread, **kwargs_thread):
        """

        :param target:
        :param args:
        :param kwargs:
        :param args_thread:
        :param kwargs_thread:
        """
        super(SISThreading, self).__init__(*args_thread, **kwargs_thread)
        if kwargs is None:
            kwargs = {}
        self.target = target  # 存储目标函数
        self.args = args  # 存储位置参数
        self.kwargs = kwargs  # 存储关键字参数
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def run(self):
        """

        :return:
        """
        while self.__running.is_set():
            if constants.stop_spider_url_flag:
                logger.warning("stop spider url in threading run.")
                break
            logger.info("thread is running!")
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到self.__flag为True后返回
            # logger.debug("run = ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            # 调用目标函数并传递参数
            self.target(*self.args, **self.kwargs)
            time.sleep(1)

    def pause(self):
        """

        :return:
        """
        logger.error("thread is pause")
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        """

        :return:
        """
        logger.warning("thread is resume")
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        """

        :return:
        """
        logger.error("thread is stop")
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False

    def is_running(self):
        """检查线程是否正在运行"""
        return self.__running.is_set()


# a = Job()
# a.start()
# time.sleep(3)
# a.pause()
# time.sleep(5)
# a.resume()
# time.sleep(2)
# a.stop()
