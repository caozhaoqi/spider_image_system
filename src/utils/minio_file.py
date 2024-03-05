from loguru import logger
from minio import Minio
# from minio.error import
import os


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
        return

    # 遍历文件夹中的图片文件
    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.log')):
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(bucket_name, file)

                # 上传文件到MinIO
                try:
                    client.fput_object(bucket_name, remote_file_path, local_file_path)
                    logger.success(f"Uploaded: {local_file_path} to {remote_file_path}")
                except Exception as err:
                    logger.error(f"Error uploading {local_file_path}: {err}")


@logger.catch
def upload_image(path):
    """

    :param path:
    :return:
    """
    # 请替换以下值为你自己的MinIO配置和本地文件夹路径
    minio_server_ip = '121.36.66.145'
    minio_server_port = 9000
    ENDPOINT_URL = minio_server_ip + ':' + minio_server_port
    ACCESS_KEY = "minioadmin"
    SECRET_KEY = "minioadmin"
    BUCKET_NAME = "data_upload"
    LOCAL_FOLDER_PATH = path

    logger.info(f"current use minio server: {ENDPOINT_URL}")
    upload_images_to_minio(ENDPOINT_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME, LOCAL_FOLDER_PATH)
    logger.success("image and log, upload success!")
