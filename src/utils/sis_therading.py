import os
import sys
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Dict

sys.path.append(str(Path(__file__).parent.parent))

import threading
import time

from loguru import logger
from run import constants


class SISThreading(threading.Thread):
    def __init__(
        self,
        target: Callable,
        args: Tuple = (),
        kwargs: Optional[Dict] = None,
        *args_thread: Any,
        **kwargs_thread: Any
    ) -> None:
        """初始化线程类
        
        Args:
            target: 目标函数
            args: 位置参数
            kwargs: 关键字参数
            args_thread: 线程位置参数
            kwargs_thread: 线程关键字参数
        """
        super().__init__(*args_thread, **kwargs_thread)
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    @logger.catch
    def run(self, _: Any = None) -> None:
        """运行线程"""
        while self.__running.is_set():
            if constants.SpiderConfig.stop_spider_url_flag:
                logger.warning("停止爬虫线程")
                break
                
            logger.info("线程运行中")
            self.__flag.wait()
            
            self.target(*self.args, **self.kwargs)
            time.sleep(constants.search_delta_time)

    @logger.catch
    def pause(self, _: Any = None) -> None:
        """暂停线程"""
        logger.error("线程已暂停")
        self.__flag.clear()

    @logger.catch
    def resume(self, _: Any = None) -> None:
        """恢复线程"""
        logger.warning("线程已恢复")
        self.__flag.set()
        self.__running.set()

    @logger.catch
    def stop(self, _: Any = None) -> None:
        """停止线程"""
        logger.error("线程已停止")
        self.__flag.set()
        self.__running.clear()

    @logger.catch
    def is_running(self, _: Any = None) -> bool:
        """检查线程是否正在运行
        
        Returns:
            线程是否在运行
        """
        return self.__running.is_set()
