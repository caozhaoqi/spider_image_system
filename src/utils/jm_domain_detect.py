import os
import sys

from run import constants

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jmcomic import *
from loguru import logger

option = JmOption.default()

meta_data = {
    # 'proxies': ProxyBuilder.clash_proxy()
}

disable_jm_log()


@logger.catch
def get_domain_ls():
    """

    :return:
    """
    template = 'https://jmcmomic.github.io/go/{}.html'
    url_ls = [
        template.format(i)
        for i in range(300, 309)
    ]
    domain_set: Set[str] = set()

    @logger.catch
    def fetch_domain(url):
        """

        :param url:
        :return:
        """
        try:
            from curl_cffi import requests as postman
            text = postman.get(url, allow_redirects=False, **meta_data).text
            for domain in JmcomicText.analyse_jm_pub_html(text):
                if domain.startswith('jm365.work'):
                    continue
                domain_set.add(domain)
        except Exception as e:
            logger.warning(f"Unknown error, detail: {e}")

    multi_thread_launcher(
        iter_objs=url_ls,
        apply_each_obj_func=fetch_domain,
    )
    return domain_set


domain_status_dict = {}


@logger.catch
def test_domain(domain: str):
    """

    :param domain:
    :return:
    """
    client = option.new_jm_client(impl='html', domain_list=[domain], **meta_data)
    status = 'ok'

    try:
        client.get_album_detail('583946')
    except Exception as e:
        status = str(e.args)
        pass

    domain_status_dict[domain] = status


@logger.catch
def jm_domain_test():
    """

    :return:
    """
    domain_set = get_domain_ls()
    logger.info(f'获取到{len(domain_set)}个域名，开始测试')

    multi_thread_launcher(
        iter_objs=domain_set,
        apply_each_obj_func=test_domain,
    )

    for domain, status in domain_status_dict.items():
        logger.debug(f'{domain}: {status}')
    constants.jm_domain_detect_flag = False
    logger.success("detect jm domain finish.")

