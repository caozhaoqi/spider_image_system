import minio
from loguru import logger
from minio import Minio
import os

from image.img_switch import folder_path, show_filter_image


# from minio.error import ResponseError

@logger.catch
def find_upload_file(directory):
    """
    find image from current dir data and log
    :param directory:
    :return:
    """
    image_files_lists = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("dir not exists, create dir: " + str(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "img_url" in root or "according_pid_download_image" in root:
                if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.log'):
                    image_files_lists.append(os.path.join(root, file))
    return image_files_lists


image_files_upload = show_filter_image(find_upload_file(folder_path))


@logger.catch
def upload_images_to_minio(endpoint_url, access_key, secret_key, bucket_name, local_folder_path):
    """

    :param endpoint_url:
    :param access_key:
    :param secret_key:
    :param bucket_name:
    :param local_folder_path:
    :return:
    """
    # 初始化MinIO客户端
    client = Minio(
        endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        secure=False  # 如果你使用的是HTTPS，请将其更改为True
    )

    # 确保bucket存在
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except Exception as err:
        logger.error(f"Error: {err}")
        return False

    for file in image_files_upload:

        relative_path = os.path.relpath(file, local_folder_path)
        remote_file_path = os.path.join(bucket_name, relative_path).replace('\\', '/')
        try:
            client.stat_object(bucket_name, remote_file_path)
            logger.warning(f"already exists, will skip: {remote_file_path}")
        except minio.error.S3Error as s3_e:
            # 对象不存在
            # print("对象不存在")
            if s3_e.code == 'NoSuchKey':
                client.fput_object(bucket_name, remote_file_path, file)
                logger.success(f"Uploaded: {remote_file_path}")
            else:
                # 处理其他可能的异常
                logger.error("unknown error! detail:", s3_e)
                return False
    return True


@logger.catch
def upload_image(path):
    """

    :param path:
    :return:
    """
    # 请替换以下值为你自己的MinIO配置和本地文件夹路径
    minio_server_ip = '121.36.66.145'
    minio_server_port = 9001
    ENDPOINT_URL = str(minio_server_ip) + ':' + str(minio_server_port)
    ACCESS_KEY = "minioadmin"
    SECRET_KEY = "minioadmin"
    BUCKET_NAME = "dataupload"
    LOCAL_FOLDER_PATH = path

    logger.info(f"current use minio server: {ENDPOINT_URL}")
    if upload_images_to_minio(ENDPOINT_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME, LOCAL_FOLDER_PATH):
        logger.success("image and log, upload success!")
    else:
        logger.warning("upload error!")
