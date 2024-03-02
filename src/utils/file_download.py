import requests
from loguru import logger
from requests.exceptions import ReadTimeout, ChunkedEncodingError, ConnectTimeout, HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# 设置重试策略
retries = Retry(
    total=5,  # 总重试次数
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


def send_request(url, timeout=20):
    """
    发送请求并处理重试和错误
    :param url: 请求的URL
    :param timeout: 超时时间（秒）
    :return: 响应对象或None
    """
    retries_count = 0
    while retries_count < retries.total:
        try:
            # 增加日志记录重试次数和开始时间
            logger.info(f"Attempting request to {url} (retry {retries_count + 1}/{retries.total})")
            start_time = time.time()

            response = session.get(url, stream=True, timeout=timeout)

            # 检查是否超时
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                logger.warning(
                    f"Request to {url} took too long ({elapsed_time} seconds >= {timeout} seconds) and was cancelled.")
                continue  # 如果实际请求时间超过了设定的超时时间，则继续重试

            response.raise_for_status()  # 如果HTTP请求返回了不成功的状态码，将引发HTTPError异常
            return response
        except (ReadTimeout, ChunkedEncodingError, ConnectTimeout, HTTPError) as e:
            # 如果是超时、分块编码错误或其他HTTP错误，记录错误并决定是否重试
            logger.error(f"Request to {url} failed with an error: {e}")

            # 增加重试延迟
            time.sleep(retries.backoff_factor * (2 ** retries_count))
            retries_count += 1

    # 如果所有重试都失败了，返回None
    logger.error(f"Failed to retrieve data from {url} after multiple retries.")
    return None

# # 使用函数发送请求，处理重试和错误
# url = 'https://example.com/api/data'
# data = send_request(url)
#
# # 处理获取到的数据
# if data is not None:
#     logger.info("Data received successfully.")
#     # 这里可以处理或输出数据，例如：
#     # print(data.text)
# else:
#     logger.error("Failed to receive data after multiple retries.")
