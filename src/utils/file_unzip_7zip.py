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
    try:
        # 使用7z命令将.xz文件解压为.7z文件
        cmd = [seven_zip_path, 'x', '-y', xz_file_path, '-o' + os.path.dirname(temp_7z_file_path)]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logger.error(f"unknown error, please check config! detail: {e}")
        return False


@logger.catch
def extract_7z(seven_zip_path, password, archive_path, output_path):
    """

    :param seven_zip_path:
    :param password:
    :param archive_path:
    :param output_path:
    :return:
    """
    try:
        # 使用7z命令并提供密码来解压.7z文件
        if password:
            # 如果密码非空，使用-p参数提供密码
            cmd = [seven_zip_path, 'x', '-y', '-p' + password, archive_path, '-o' + output_path]
        else:
            # 如果密码为空，则不使用-p参数
            cmd = [seven_zip_path, 'x', '-y', archive_path, '-o' + output_path]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logger.error(f"unknown error, please check config! detail: {e}")
        return False


@logger.catch
def scan_file_zip(dir_path):
    """

    :param dir_path:
    :return:
    """
    file_zip_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.7z') or file.endswith('.7z.xz'):
                file_zip_list.append(os.path.join(root, file))
    return file_zip_list


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
    file_list = scan_file_zip(dir_path)
    if not file_list:
        logger.warning(f"{dir_path} no xz content!")
        constants.unzip_file_flag = False
        return False

    logger.debug(f"start unzip .xz to 7zp length: {len(file_list)}: ")
    for file in file_list:
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

    # f7zp_list = os.listdir(dir_path)
    logger.debug(f"start unzip .7z to mp4 length {len(file_list)}: ")
    if not file_list:
        logger.warning(f"{dir_path} no 7z content!")
        constants.unzip_file_flag = False
        return False

    for file_7z in file_list:
        if file_7z.endswith('.7z'):
            # 提取文件名和目录
            filename = os.path.splitext(file_7z)[0]
            temp_7z_file_path = os.path.join(dir_path, filename + '.7z')
            mp4_file_path = os.path.join(dir_path, filename + '.mp4')
            unzip_file_path = os.path.join(os.path.dirname(mp4_file_path), 'unzip_video')
            if not os.path.exists(unzip_file_path):
                logger.warning(f"unzip file path not exists, will create it: {unzip_file_path}")
                os.makedirs(unzip_file_path)
            # 解压.xz文件为.7z文件
            if not os.path.exists(mp4_file_path):
                # 解压.7z文件（如果需要密码的话）
                extract_7z(SEVEN_ZIP_PATH, PASSWORD, temp_7z_file_path, unzip_file_path)
            else:
                logger.warning(f".mp4 存在：{file_7z} skip!")
                continue

    logger.success("unzip all file success!")
    constants.unzip_file_flag = False
    return True
