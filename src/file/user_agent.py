import configparser
import os
import sys

from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ini_path = os.path.join(os.getcwd(), f'./config/')
agent_file_path = os.path.join(os.getcwd(), f'./config/user-agent.txt')

user_agents = [
    # 这里可以添加多个常见的User-Agent字符串
    # 这是Chrome浏览器的User-Agent字符串。
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 '
    'Safari/537.36',
    # 这是Mac上的Chrome浏览器的User-Agent字符串。
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 '
    'Safari/537.36',
    # 这是Firefox浏览器的User-Agent字符串
    'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
    # 这是iOS上的Safari浏览器的User-Agent字符串
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
    'Version/14.0.1 Mobile/15E148 Safari/604.1',
    # 这是Microsoft Edge浏览器的User - Agent字符串
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/18.18362',
    # chrome 2
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 '
    'Safari/537.36',
    # mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 '
    'Safari/537.36',
    # linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
]


@logger.catch
def create_agent_init(user_agent_file_path):
    """

    :param user_agent_file_path:
    :return:
    """
    with open(user_agent_file_path, 'w', encoding='utf-8') as f:
        if not os.path.exists(ini_path):
            os.makedirs(ini_path)
            logger.warning("base config not exists, will create.")
        for agent_detail in user_agents:
            f.write(agent_detail + "\n")
    logger.success("init user agent file write success!")


@logger.catch
def read_user_agent():
    """

    :return:
    """
    # user_agents_list = []
    with open(agent_file_path, 'r', encoding='utf-8') as f:
        if not os.path.exists(agent_file_path):
            create_agent_init(agent_file_path)
        user_agents_list = f.readlines()
    return user_agents_list
