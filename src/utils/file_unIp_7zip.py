import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loguru import logger
import subprocess
from run import constants


@logger.catch
def extract_xz_to_7z(seven_zip_path, xz_file_path, temp_7z_file_path):
    """

    :param seven_zip_path:
    :param xz_file_path:
    :param temp_7z_file_path:
    :return:
    """
    # 使用7z命令将.xz文件解压为.7z文件
    cmd = [seven_zip_path, 'x', xz_file_path, '-o' + os.path.dirname(temp_7z_file_path)]
    subprocess.run(cmd, check=True)

    # # 检查是否成功生成了.7z文件
    # if os.path.exists(temp_7z_file_path):
    #     return True
    # else:
    #     return False


@logger.catch
def extract_7z(seven_zip_path, password, archive_path, output_path):
    """

    :param seven_zip_path:
    :param password:
    :param archive_path:
    :param output_path:
    :return:
    """

    # 使用7z命令并提供密码来解压.7z文件
    if password:
        # 如果密码非空，使用-p参数提供密码
        cmd = [seven_zip_path, 'x', '-p' + password, archive_path, '-o' + output_path]
    else:
        # 如果密码为空，则不使用-p参数
        cmd = [seven_zip_path, 'x', archive_path, '-o' + output_path]
    subprocess.run(cmd, check=True)


@logger.catch
def unzip_file(dir_path):
    """

    :param dir_path: 目录
    :return:
    """
    # 7-Zip的安装路径，确保这是您电脑上7-Zip的实际安装路径
    SEVEN_ZIP_PATH = constants.SEVEN_ZIP_PATH
    # 解压密码（如果有的话）
    PASSWORD = constants.PASSWORD  # 替换为实际的密码

    # 遍历当前目录下的所有.7z.xz文件
    logger.debug("start unzip .xz to 7zp: ")
    for file in os.listdir(dir_path):
        if file.endswith('.7z.xz'):
            # 提取文件名和目录
            filename = os.path.splitext(file)[0]
            xz_file_path = os.path.join(dir_path, file)
            temp_7z_file_path = os.path.join(dir_path, filename + '.7z')

            # 解压.xz文件为.7z文件
            if not os.path.exists(temp_7z_file_path):
                extract_xz_to_7z(SEVEN_ZIP_PATH, xz_file_path, temp_7z_file_path)
            else:
                logger.warning(f".7z 存在：{file} skip!")
                continue

    logger.debug("start unzip .7z to mp4: ")
    for file_7z in os.listdir(dir_path):
        if file_7z.endswith('.7z'):
            # 提取文件名和目录
            filename = os.path.splitext(file_7z)[0]
            temp_7z_file_path = os.path.join(dir_path, filename + '.7z')
            mp4_file_path = os.path.join(dir_path, filename + '.mp4')
            # 解压.xz文件为.7z文件
            if not os.path.exists(mp4_file_path):
                # 解压.7z文件（如果需要密码的话）
                extract_7z(SEVEN_ZIP_PATH, PASSWORD, temp_7z_file_path, dir_path)
            else:
                logger.warning(f".mp4 存在：{file_7z} skip!")
                continue

    return True


if __name__ == '__main__':
    unzip_file(r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\utils\data')
