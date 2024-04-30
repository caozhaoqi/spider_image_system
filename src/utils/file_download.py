import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from requests.exceptions import ReadTimeout, ChunkedEncodingError, ConnectTimeout, HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from run.constants import download_img_retry_times, download_img_time_out
from loguru import logger

retries = Retry(
    total=download_img_retry_times,  # 总重试次数
    backoff_factor=0.5,  # 重试间隔的倍数，逐渐增加
    status_forcelist=[500, 502, 503, 504, 408, 429],  # 遇到这些HTTP状态码时重试
    # method_whitelist=["HEAD", "GET", "OPTIONS"]  # 只对这些方法重试
)

# 使用重试策略的适配器
adapter = HTTPAdapter(max_retries=retries)

# 挂载适配器到会话
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)


@logger.catch
def send_request(url, timeout=download_img_time_out):
    """
    发送请求并处理重试和错误
    :param url: 请求的URL
    :param timeout: 超时时间（秒）
    :return: 响应对象或None
    """
    try:
        # urllib3.disable_warnings()
        retries_count = 0
        while retries_count < retries.total:
            try:
                start_time = time.time()

                response = session.get(url, stream=True, timeout=timeout)

                # 检查是否超时
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    continue  # 如果实际请求时间超过了设定的超时时间，则继续重试

                response.raise_for_status()  # 如果HTTP请求返回了不成功的状态码，将引发HTTPError异常
                return response
            except (ReadTimeout, ChunkedEncodingError, ConnectTimeout, HTTPError) as e:
                time.sleep(retries.backoff_factor * (2 ** retries_count))
                retries_count += 1
            except Exception as e:
                time.sleep(retries.backoff_factor * (2 ** retries_count))
                retries_count += 1
                # continue
    except Exception as e:
        # logger.warning(e)
        ...
    return None
