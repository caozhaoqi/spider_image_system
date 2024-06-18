import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
from loguru import logger
import re
import stat, zipfile, os, psutil
import requests
from lxml import etree
import time


class AutoDownloadChromeDrive(object):
    """

    """

    def __init__(self):
        self.chrome_drive_url = "https://chromedriver.chromium.org/downloads"
        self.local_chrome_paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]

        self.headers = {'content-type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

    @logger.catch
    def get_chromedriver_urls(self, _=None):
        """

        :return:
        """
        try:
            r = requests.Session()
            response = r.get(self.chrome_drive_url, headers=self.headers, verify=False)
            logger.debug(response.status_code, response.encoding)
            html = etree.HTML(response.text, etree.HTMLParser())  # 解析HTML文本内容
            version_href = html.xpath(".//strong//..//@href")
            logger.debug("All chrome browser versions can be choosed:")
            for href in version_href:
                logger.debug(href)

            return version_href
        except Exception:
            return None

    @logger.catch
    def download_chrome_drive(self, url, _=None):
        """

        :param url:
        :return:
        """
        try:
            r = requests.Session()
            response = r.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                with open("chromedriver_win32.zip", "wb") as f:
                    f.write(response.content)
                    logger.debug("下载完成")
                    return 1
            else:
                logger.warning('Url请求返回错误，错误码为： %d' % response.status_code)
                return None
        except Exception:
            logger.warning("Request download chromedriver_win32.zip failed!")
            return None

    @logger.catch
    def find_local_version(self, loc_ver, all_ver, _=None):
        """
        :param _:
        :param loc_ver: 本地浏览器的版本
        :param all_ver: 下载的所有版本浏览器版本
        :return: 找到匹配的，return url,否则return None
        """
        for href in all_ver:
            try:
                res = re.search(r"path=(.*?)/", href)
                find_ver = res.group(1).split(".")[0]  # 截取大版本
                if loc_ver == find_ver:
                    return href
            except Exception:
                continue

        logger.debug("Not find match chrome browser{} version!".format(loc_ver))
        return None

    @logger.catch
    def kill_process(self, process_name, _=None):
        """

        :param _:
        :param process_name:
        :return:
        """
        logger.debug("检测{}进程是否存在，存在则杀掉。".format(process_name))
        pl = psutil.pids()
        for pid in pl:
            if psutil.Process(pid).name() == process_name:
                logger.debug('{} 存在进程中,杀掉'.format(process_name))
                os.popen('taskkill /f /im %s' % process_name)
                return pid
        logger.debug('{} 不存在进程中。'.format(process_name))
        return None

    @logger.catch
    def unzip(self, _=None):
        """

        :return:
        """
        self.kill_process("chromedriver.exe")
        logger.debug("去除旧版本chromedriver_win32文件夹内文件的只读属性(如果是只读)")
        old_driver_path = os.path.join(os.getcwd(), "chromedriver_win32")
        if os.path.exists(old_driver_path):
            for sub_file in os.listdir(old_driver_path):
                os.chmod(os.path.join(old_driver_path, sub_file), stat.S_IRWXU)
        time.sleep(1)  # 这个delay必须要有，os操作还是需要时间的
        logger.debug('''解压 chromedriver_win32.zip, 覆盖旧版本''')
        zFile = zipfile.ZipFile(os.path.join(os.getcwd(), "chromedriver_win32.zip"), "r")
        for fileM in zFile.namelist():
            zFile.extract(fileM, old_driver_path)
        zFile.close()
        logger.success(f"Download webdriver success, path: {zFile.filename}")

    @logger.catch
    def start(self, _=None):
        """
                读取本地chrome version

        :return:
        """
        version = get_chrome_version_from_executable()
        if not version:
            logger.debug("Check chrome browser version failed!")
            return None
        logger.debug("Chrome browser version:", version)
        '''下载网页端与本地匹配的chromedriver.exe'''
        version_href = self.get_chromedriver_urls()
        if not version_href:
            logger.debug("Request %s failed!" % self.chrome_drive_url)
            return None

        find_url = self.find_local_version(version.split(".")[0], version_href)
        logger.debug("找到匹配的版本:\n%s" % find_url)
        if not find_url:
            return None
        version_num = re.search(r"path=(.*?)/", find_url).group(1)
        find_url_2 = find_url.rsplit('/', 2)[0]
        new_url = "{}/{}/chromedriver_win32.zip".format(find_url_2, version_num)
        logger.debug("Downloading......\n%s" % new_url)
        ret = self.download_chrome_drive(new_url)
        if not ret:
            return None
        self.unzip()


@logger.catch
def get_chrome_version_from_executable():
    """

    :return:
    """
    try:
        file_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

        # WMI命令字符串
        command = f'wmic datafile where name="{file_path}" get Version'
        # 执行命令并捕获输出
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 从输出中提取版本信息
        if result.returncode == 0:
            version_line = [line for line in result.stdout.split('\n\n')]
            if version_line:
                return version_line[1].strip()
        else:
            logger.warning(f"Command failed with return code {result.returncode}: {result.stderr}")
    except Exception as e:
        logger.warning(f"Error reading file version: {e}")
    return None
