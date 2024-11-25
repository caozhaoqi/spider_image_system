import os
import sys
from pathlib import Path
from typing import List, Optional

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from minio import Minio
from minio.error import S3Error
from run import constants


@logger.catch
def find_upload_file(directory: str) -> List[str]:
    """查找目录下需要上传的图片和日志文件
    
    Args:
        directory: 要搜索的目录路径
        
    Returns:
        包含所有找到的文件路径的列表
    """
    image_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        directory_path.mkdir(parents=True)
        logger.info(f"创建目录: {directory_path}")
        
    for path in directory_path.rglob("*"):
        if not path.is_file():
            continue
            
        parent = path.parent
        if any(x in str(parent) for x in ["img_url", "according_pid_download_image", "log_dir"]):
            if path.suffix.lower() in [".jpg", ".png", ".log"]:
                image_files.append(str(path))
                
    return image_files


@logger.catch
def show_filter_image_log(images_list: List[str]) -> List[str]:
    """过滤不需要显示在首页的图片
    
    Args:
        images_list: 图片路径列表
        
    Returns:
        过滤后的图片路径列表
    """
    excluded_keywords = ["square", "custom", "error_images", "small_images"]
    
    return [
        img for img in images_list 
        if not any(keyword in str(Path(img)) for keyword in excluded_keywords)
    ]


@logger.catch
def upload_images_to_minio(
    endpoint_url: str,
    access_key: str, 
    secret_key: str,
    bucket_name: str,
    local_folder_path: str
) -> bool:
    """上传文件到MinIO服务器
    
    Args:
        endpoint_url: MinIO服务器地址
        access_key: 访问密钥
        secret_key: 密钥
        bucket_name: 存储桶名称
        local_folder_path: 本地文件夹路径
        
    Returns:
        上传是否成功
    """
    client = Minio(
        endpoint_url,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )

    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except Exception as err:
        logger.error(f"创建存储桶失败: {err}")
        return False

    image_files = show_filter_image_log(find_upload_file(constants.basic_path))
    if not image_files:
        logger.warning(f"目录 {local_folder_path} 中没有文件")
        return False
        
    for file_path in image_files:
        relative_path = os.path.relpath(file_path, local_folder_path)
        remote_path = f"{bucket_name}/{relative_path}".replace('\\', '/')
        
        try:
            client.stat_object(bucket_name, remote_path)
        except S3Error as err:
            if err.code == 'NoSuchKey':
                try:
                    client.fput_object(bucket_name, remote_path, file_path)
                    logger.success(f"上传成功: {remote_path}")
                except Exception as e:
                    logger.error(f"上传失败: {e}")
            else:
                logger.error(f"MinIO错误: {err}")
                return False
                
    return True


@logger.catch
def upload_image(path: str) -> None:
    """上传指定路径的文件到MinIO
    
    Args:
        path: 要上传的文件路径
    """
    endpoint = f"{constants.minio_server_ip}:{constants.minio_server_port}"
    logger.info(f"使用MinIO服务器: {endpoint}")
    
    if upload_images_to_minio(
        endpoint,
        constants.minio_account,
        constants.minio_password,
        "dataupload",
        path
    ):
        logger.success("所有图片和日志上传成功!")
        constants.uploading_image_flag = False
    else:
        logger.warning("上传失败,无法连接MinIO服务器!")
