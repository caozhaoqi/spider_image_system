"""
GoFile文件上传工具

用于将文件上传到GoFile服务器的工具函数集合。

Author: zq.c
Modified: 2024/8/1
Created: 2024/7/24
Describe: Github link: https://github.com/caozhaoqi
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional

import requests
from loguru import logger
from run import constants

# GoFile API配置
GO_FILE_CONFIG = {
    "token": "sz6exDf8GuR0yuB38GOerYDspmY5qB7F",
    "id": "e6b6dd7f-a89a-4165-af70-9674aab82c18", 
    "folder_id": "f5822db9-1046-4a41-b6f1-3ad3aee6e8fe"
}


@logger.catch
def http_upload(file_path: str) -> bool:
    """
    上传文件到GoFile服务器
    
    Args:
        file_path: 要上传的文件路径
        
    Returns:
        bool: 上传是否成功
    """
    server_list = detect_go_server()
    if not server_list:
        logger.error("无法获取GoFile服务器列表")
        return False
        
    server_name = server_list[0]['name']
    upload_url = f'https://{server_name}.gofile.io/contents/uploadfile'
    
    headers = {
        "Authorization": f"Bearer {GO_FILE_CONFIG['token']}"
    }
    data = {
        "folderId": GO_FILE_CONFIG['folder_id']
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(upload_url, files=files, data=data, headers=headers)
            response.raise_for_status()
            
        result = response.json()
        if result['status'] == 'ok':
            logger.success(f"文件上传成功: {result['data']}")
            return True
        else:
            logger.warning(f"文件上传失败: {result}")
            return False
            
    except Exception as e:
        logger.error(f"上传过程出错: {e}")
        return False


@logger.catch
def detect_go_server() -> List[Dict]:
    """
    获取可用的GoFile服务器列表
    
    Returns:
        List[Dict]: 服务器信息列表
    """
    api_url = 'https://api.gofile.io/servers'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        result = response.json()
        
        if result['status'] == 'ok':
            return result['data']['servers']
        return []
        
    except Exception as e:
        logger.error(f"获取服务器列表失败: {e}")
        return []


@logger.catch
def scan_files_go(directory: str) -> List[str]:
    """
    扫描目录下的所有非空文件
    
    Args:
        directory: 要扫描的目录路径
        
    Returns:
        List[str]: 文件路径列表
    """
    file_list = []
    for path in Path(directory).rglob('*'):
        if path.is_file() and path.stat().st_size > 0:
            file_list.append(str(path))
    return file_list


@logger.catch
def save_upload_already(txt_data_path: str, file_path: str) -> bool:
    """
    记录已上传的文件
    
    Args:
        txt_data_path: 记录文件所在目录
        file_path: 已上传的文件路径
        
    Returns:
        bool: 记录是否成功
    """
    record_file = Path(txt_data_path) / "go_file_img_upload.txt"
    try:
        with open(record_file, 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"{file_path}\n")
        logger.success(f"记录已上传文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"记录文件失败: {e}")
        return False


@logger.catch
def exists_upload_gofile(txt_path: str) -> List[str]:
    """
    获取已上传文件记录
    
    Args:
        txt_path: 记录文件所在目录
        
    Returns:
        List[str]: 已上传文件列表
    """
    record_file = Path(txt_path) / "go_file_img_upload.txt"
    
    try:
        if not record_file.exists():
            record_file.touch()
            logger.warning(f"创建记录文件: {record_file}")
            return []
            
        with open(record_file, 'r', encoding='utf-8', errors='replace') as f:
            return f.readlines()
            
    except Exception as e:
        logger.error(f"读取记录文件失败: {e}")
        return []


@logger.catch
def exists_gofile_img(file_path: str, uploaded_files: List[str]) -> bool:
    """
    检查文件是否已上传
    
    Args:
        file_path: 要检查的文件路径
        uploaded_files: 已上传文件列表
        
    Returns:
        bool: 文件是否已上传
    """
    file_name = Path(file_path).name
    return any(file_name in uploaded for uploaded in uploaded_files)


@logger.catch
def upload_all_gofile(data_path: str) -> bool:
    """
    上传目录下的所有文件
    
    Args:
        data_path: 要上传的目录路径
        
    Returns:
        bool: 上传是否全部成功
    """
    logger.info(f"开始上传文件到GoFile服务器，配置信息:\n{json.dumps(GO_FILE_CONFIG, indent=2)}")
    
    try:
        uploaded_files = exists_upload_gofile(data_path)
        files_to_upload = scan_files_go(data_path)
        
        if not files_to_upload:
            logger.warning(f"目录 {data_path} 中没有找到文件")
            return False
            
        for file_path in files_to_upload:
            if exists_gofile_img(file_path, uploaded_files):
                logger.warning(f"文件已上传，跳过: {file_path}")
                continue
                
            if http_upload(file_path):
                save_upload_already(data_path, file_path)
                
        constants.ProcessingConfig.go_file_upload_flag = False
        logger.success("所有文件上传完成")
        return True
        
    except Exception as e:
        logger.error(f"上传过程出错: {e}")
        return False


if __name__ == '__main__':
    path = './'
    upload_all_gofile(path)
