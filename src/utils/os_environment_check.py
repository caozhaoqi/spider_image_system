"""
exe execute os environment
"""
import os
import platform
import subprocess
import sys


# 定义下载和安装函数，这些函数将根据平台进行调整
def download_file(url, dest):
    if platform.system() == 'Windows':
        # Windows平台下使用wget或PowerShell下载文件
        subprocess.run(['wget', url, '-O', dest])
    elif platform.system() == 'Linux':
        # Ubuntu或其他Linux平台使用wget或curl下载文件
        subprocess.run(['wget', url, '-O', dest])
    else:
        raise Exception("Unsupported platform")


def install_selenium():
    # 这里假设你有一个适用于各平台的selenium安装包
    selenium_installer = 'selenium-installer.tar.gz'
    download_file('https://your-cloud-storage-url/' + selenium_installer, selenium_installer)

    # 解压并安装selenium
    if platform.system() == 'Windows':
        subprocess.run(['tar', '-xzf', selenium_installer])
        # Windows平台可能需要额外的步骤来配置环境变量或移动文件
    elif platform.system() == 'Linux':
        subprocess.run(['tar', '-xzf', selenium_installer])
        # 对于Linux，你可能需要将selenium移动到适当的Python库目录


def install_chromedriver():
    # 假设你有适用于各平台的chromedriver二进制文件
    chromedriver_file = 'chromedriver'
    if platform.system() == 'Windows':
        # 下载Windows版本的chromedriver
        chromedriver_exe = 'chromedriver.exe'
        download_file('https://your-cloud-storage-url/' + chromedriver_exe, chromedriver_exe)
        # 将chromedriver.exe移动到PATH中或指定的目录
        os.environ['PATH'] += os.pathsep + os.path.dirname(chromedriver_exe)
    elif platform.system() == 'Linux':
        # 下载Linux版本的chromedriver
        download_file('https://your-cloud-storage-url/' + chromedriver_file, chromedriver_file)
        # 为chromedriver设置执行权限并移动到适当的目录
        subprocess.run(['chmod', '+x', chromedriver_file])
        # 移动chromedriver到PATH中或指定的目录


# 主程序
def main():
    # 检查并安装selenium和chromedriver
    if not is_selenium_installed():
        install_selenium()
    if not is_chromedriver_installed():
        install_chromedriver()


# 检测selenium和chromedriver是否已安装的函数
def is_selenium_installed():
    try:
        import selenium  # 尝试导入selenium库
        return True
    except ImportError:
        return False


def is_chromedriver_installed():
    # 在Windows上，检查chromedriver.exe是否在PATH中
    if platform.system() == 'Windows':
        try:
            subprocess.run(['chromedriver', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False
    # 在Linux上，假设chromedriver在PATH中或指定的路径下
    elif platform.system() == 'Linux':
        return os.path.exists('/usr/bin/chromedriver')  # 或其他你放置chromedriver的路径


if __name__ == '__main__':
    main()