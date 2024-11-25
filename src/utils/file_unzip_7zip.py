import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
import subprocess
from run import constants


@logger.catch
def extract_xz_to_7z(seven_zip_path: str, xz_file_path: str, temp_7z_file_path: str) -> bool:
    """
    将.xz文件解压为.7z文件
    
    Args:
        seven_zip_path: 7zip程序路径
        xz_file_path: xz文件路径
        temp_7z_file_path: 输出的7z文件路径
        
    Returns:
        bool: 解压是否成功
    """
    try:
        cmd = [seven_zip_path, 'x', '-y', xz_file_path, '-o' + str(Path(temp_7z_file_path).parent)]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logger.error(f"解压xz文件失败: {e}")
        return False


@logger.catch
def extract_7z(seven_zip_path: str, password: str, archive_path: str, output_path: str) -> bool:
    """
    解压7z文件
    
    Args:
        seven_zip_path: 7zip程序路径
        password: 解压密码
        archive_path: 7z文件路径
        output_path: 输出目录
        
    Returns:
        bool: 解压是否成功
    """
    try:
        cmd = [seven_zip_path, 'x', '-y']
        if password:
            cmd.append('-p' + password)
        cmd.extend([archive_path, '-o' + output_path])
        
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logger.error(f"解压7z文件失败: {e}")
        return False


@logger.catch
def scan_file_zip(dir_path: str) -> list:
    """
    扫描目录下的压缩文件
    
    Args:
        dir_path: 要扫描的目录路径
        
    Returns:
        list: 压缩文件路径列表
    """
    file_zip_list = []
    for path in Path(dir_path).rglob('*'):
        if path.suffix in ['.7z', '.xz'] and path.name.endswith(('.7z', '.7z.xz')):
            file_zip_list.append(str(path))
    return file_zip_list


@logger.catch
def unzip_file(dir_path: str) -> bool:
    """
    解压目录下的所有压缩文件
    
    Args:
        dir_path: 目录路径
        
    Returns:
        bool: 解压是否成功
    """
    try:
        file_list = scan_file_zip(dir_path)
        if not file_list:
            logger.warning(f"{dir_path} 目录下没有找到压缩文件")
            constants.unzip_file_flag = False
            return False

        # 处理.7z.xz文件
        logger.debug(f"开始解压 .xz 文件, 共 {len(file_list)} 个文件")
        for file in file_list:
            if not file.endswith('.7z.xz'):
                continue
                
            file_path = Path(file)
            temp_7z_path = file_path.parent / (file_path.stem + '.7z')
            
            if not temp_7z_path.exists():
                extract_xz_to_7z(constants.SEVEN_ZIP_PATH, str(file_path), str(temp_7z_path))
            else:
                logger.warning(f"7z文件已存在，跳过: {file_path.name}")

        # 处理.7z文件
        logger.debug(f"开始解压 .7z 文件, 共 {len(file_list)} 个文件")
        for file_7z in file_list:
            if not file_7z.endswith('.7z'):
                continue
                
            file_path = Path(file_7z)
            mp4_path = file_path.parent / (file_path.stem + '.mp4')
            unzip_path = file_path.parent / 'unzip_video'
            
            unzip_path.mkdir(parents=True, exist_ok=True)
            
            if not mp4_path.exists():
                extract_7z(constants.SEVEN_ZIP_PATH, constants.PASSWORD, str(file_path), str(unzip_path))
            else:
                logger.warning(f"MP4文件已存在，跳过: {file_path.name}")

        logger.success("所有文件解压完成!")
        constants.unzip_file_flag = False
        return True
        
    except Exception as e:
        logger.error(f"解压过程出错: {e}")
        constants.unzip_file_flag = False
        return False
