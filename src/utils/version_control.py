# 导入OS模块
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import requests
from loguru import logger
import run.constants


@logger.catch
def compare_versions(version1, version2):
    """
    Compare two version strings, potentially with a 'v' prefix.

    :param version1: First version string
    :param version2: Second version string
    :return:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """

    # Remove the 'v' prefix if it exists
    version1 = version1.lstrip('v')
    version2 = version2.lstrip('v')

    # Split the version strings into lists of integers
    v1 = [int(part) for part in version1.split('.')]
    v2 = [int(part) for part in version2.split('.')]

    # Pad the shorter list with zeros
    max_length = max(len(v1), len(v2))
    v1.extend([0] * (max_length - len(v1)))
    v2.extend([0] * (max_length - len(v2)))

    # Compare the version numbers
    for i in range(max_length):
        if v1[i] < v2[i]:
            return -1
        elif v1[i] > v2[i]:
            return 1

    # If we reach here, the versions are equal
    return 0


@logger.catch
def compare_versions_with_pre_release(version1, version2):
    """
    Compare two version strings with pre-release tags.

    :param version1: First version string
    :param version2: Second version string
    :return:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """

    pattern = r'^v?(\d+(\.\d+)*)(.*?)$'

    match1 = re.match(pattern, version1)
    match2 = re.match(pattern, version2)

    if match1 is None:
        logger.warning(f"版本号 {version1} 匹配失败")
        return None

    if match2 is None:
        logger.warning(f"版本号 {version2} 匹配失败")
        return None

    main_version1 = match1.group(1)
    pre_release1 = match1.group(3)
    main_version2 = match2.group(1)
    pre_release2 = match2.group(3)

    if not pre_release1 and not pre_release2:
        return compare_versions(main_version1, main_version2)

    if not pre_release1:
        return 1
    if not pre_release2:
        return -1

    if main_version1 == main_version2:
        return pre_release1 < pre_release2 - 1

    # 比较主要版本号
    return compare_versions(main_version1, main_version2)


@logger.catch
def download_new_version(version):
    """

    @:param version
    :return:
    """
    url = 'https://gitee.com/caozhaoqi/spider_image_system/releases/download/' + version + '/sis_' + version \
          + '.exe'
    save_path = run.constants.basic_path

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(save_path, 'wb') as file:

            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        logger.success(f"New version download finished: {save_path}")
        return True
    else:
        logger.error(f"请求失败，状态码：{response.status_code}")
        return False
