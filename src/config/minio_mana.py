import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from minio import Minio
from file.ini_file_spider import spider_config


class MinioMana:
    mc = None

    @logger.catch
    def __init__(self):
        minio_ip = spider_config().minio_server_ip
        minio_port = spider_config().minio_server_port
        minio_username = spider_config().minio_account
        minio_password = spider_config().minio_password
        minio_config = {
            'endpoint': minio_ip + ':' + minio_port,
            'access_key': minio_username,
            'secret_key': minio_password,
            'secure': False
        }
        self.mc = Minio(
            minio_config['endpoint'],
            access_key=minio_config['access_key'],
            secret_key=minio_config['secret_key'],
            secure=False
        )

    @logger.catch
    def get_file_object(self, bucket, src, dst):
        try:
            result = self.mc.fget_object(bucket, src, dst)
        # Read data from response.
        finally:
            logger.info("created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id,
            ))

    @logger.catch
    def get_dir_object(self, bucket, dir, local_path):
        objects = self.mc.list_objects(
            bucket, prefix=dir, recursive=True,
        )

        for obj in objects:
            logger.info("file_list:" + obj.object_name)
            self.get_file_object(bucket,
                                 obj.object_name,
                                 local_path + obj.object_name)

    @logger.catch
    def put_file_object(self, bucket, multi_level_name, local_path):
        try:
            result = self.mc.fput_object(bucket, multi_level_name, local_path)
        # Read data from response.
        finally:
            logger.info("created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id,
            ))

