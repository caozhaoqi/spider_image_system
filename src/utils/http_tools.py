import re


def is_valid_url(url):
    """
    url valid
    :param url:
    :return: True or False
    """
    # 匹配URL的正则表达式
    pattern = r'^https?://.+$'
    # 判断输入是否匹配正则表达式
    if re.match(pattern, url):
        return True
    else:
        return False
