import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from run.constants import download_img_retry_times, download_img_time_out
from loguru import logger
import urllib3

urllib3.disable_warnings()

# 配置重试策略
retry_strategy = Retry(
    total=download_img_retry_times,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504, 408, 429]
)

# 创建会话并配置重试
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)


@logger.catch
def send_request(url: str, timeout: int = download_img_time_out) -> requests.Response | None:
    """
    发送HTTP请求并处理重试和错误

    Args:
        url: 请求的URL
        timeout: 超时时间（秒）

    Returns:
        Response对象，如果请求失败则返回None
    """
    for attempt in range(retry_strategy.total):
        try:
            start_time = time.time()
            
            response = session.get(url, stream=True, timeout=timeout, verify=False)
            
            # 检查是否超时
            if time.time() - start_time >= timeout:
                logger.warning(f"Request timed out after {timeout}s")
                continue
                
            response.raise_for_status()
            return response
            
        except RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{retry_strategy.total}): {str(e)}")
            if attempt < retry_strategy.total - 1:
                sleep_time = retry_strategy.backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
            
        except Exception as e:
            logger.warning(f"Unexpected error (attempt {attempt + 1}/{retry_strategy.total}): {str(e)}")
            if attempt < retry_strategy.total - 1:
                sleep_time = retry_strategy.backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)
                
    return None
