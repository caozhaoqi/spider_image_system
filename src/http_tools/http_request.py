"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import urllib.request
import cv2
import zipfile
import time
from loguru import logger
from requests import HTTPError, Timeout, TooManyRedirects

from file.file_process import scan_directory_zip
from utils.file_utils import remove_duplicates_from_txt
from run import constants
from run.constants import output_video_fps


@logger.catch
def download_all_zip(url: str, save_dir: str) -> bool:
    """Download zip file from URL to specified directory
    
    Args:
        url: Download URL
        save_dir: Save directory path
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        file_name = url.split("/")[-1]
        save_path = os.path.join(save_dir, "gif_zip")
        Path(save_path).mkdir(parents=True, exist_ok=True)
        
        download_thread = threading.Thread(
            target=download_file_fun,
            args=(url, os.path.join(save_path, file_name))
        )
        download_thread.start()
        
        return constants.SpiderConfig.download_finish_flag
        
    except FileNotFoundError as e:
        logger.warning(f"Target file not exists: {e}")
    except HTTPError as e:
        logger.error(f"HTTP error: {e}")
    except Timeout:
        logger.error("Connection timeout")
    except TooManyRedirects:
        logger.error("Too many redirects")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        
    return False


@logger.catch 
def extract_file(save_path: str, file_name: str) -> Optional[str]:
    """Extract zip file and verify extracted file size
    
    Args:
        save_path: Directory to save extracted files
        file_name: Zip file name
        
    Returns:
        str: Path to extracted files if successful, None otherwise
    """
    result_path = Path(save_path) / "gif_unzip" / Path(file_name).stem
    result_path.mkdir(parents=True, exist_ok=True)

    zip_size = os.path.getsize(file_name)

    if zip_size > 0:
        try:
            with zipfile.ZipFile(file_name) as zip_ref:
                zip_ref.extractall(str(result_path))
            logger.debug(f"Files extracted to {result_path}")
            return str(result_path)
        except Exception as e:
            logger.warning(f"Extraction error: {e}")
    else:
        logger.debug(f"Invalid zip file size: {zip_size} bytes")
        
    return None


@logger.catch
def generate_gif_video(zip_file_list: List[str]) -> bool:
    """Extract zips and generate videos from images
    
    Args:
        zip_file_list: List of zip file paths
        
    Returns:
        bool: True if successful, False otherwise
    """
    result_paths = []
    output_video_path = Path(constants.data_path) / zip_file_list[0].replace("zip", "video")
    output_video_path.mkdir(parents=True, exist_ok=True)

    for zip_file in zip_file_list:
        folder_path = Path(zip_file).parent.parent
        unzip_path = extract_file(str(folder_path), zip_file)
        
        if unzip_path:
            result_paths.append(unzip_path)
            logger.success(f"Extracted to {unzip_path}")
        else:
            logger.error(f"Failed to extract {zip_file}")

    logger.info("Scanning unzipped image files")
    
    for result_path in result_paths:
        img_files = [
            str(f) for f in Path(result_path).glob("*")
            if f.suffix.lower() in (".jpg", ".png")
        ]
        
        if img_files:
            video_name = Path(result_path).name
            logger.info(f"Generating video for {video_name}")
            if img_video_convert(img_files, str(output_video_path), video_name):
                logger.success(f"Video generated: {video_name}")

    constants.SpiderConfig.unzip_generate_video_flag = False
    logger.success(f"Generated videos from {len(result_paths)} zip files")
    return True


@logger.catch
def img_video_convert(image_paths: List[str], video_out_path: str, video_name: str) -> bool:
    """Convert image sequence to video
    
    Args:
        image_paths: List of image file paths
        video_out_path: Output directory for video
        video_name: Name for output video file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get dimensions from first valid image
    width = height = 0
    for img_path in image_paths:
        try:
            img = cv2.imread(img_path)
            if img is not None:
                height, width = img.shape[:2]
                break
        except Exception as e:
            logger.error(f"Error reading {img_path}: {e}")
            continue
            
    if not width or not height:
        logger.error("No valid images found")
        return False

    video_path = os.path.join(video_out_path, f"{video_name}_test.mp4")
    if os.path.exists(video_path):
        logger.warning(f"Video already exists: {video_path}")
        return False

    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    video = cv2.VideoWriter(video_path, fourcc, int(output_video_fps), (width, height))

    if not video.isOpened():
        logger.error("Failed to open video writer")
        return False

    try:
        for i, img_path in enumerate(image_paths, 1):
            img = cv2.imread(img_path)
            if img is None:
                logger.error(f"Failed to load image: {img_path}")
                continue
                
            resized = cv2.resize(img, (width, height))
            video.write(resized)
            
    finally:
        video.release()
        
    return True


@logger.catch
def download_file_fun(url: str, filename: str) -> bool:
    """Download file from URL
    
    Args:
        url: Download URL
        filename: Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    url = url.strip()
    filename = filename.strip()
    
    if os.path.exists(filename):
        logger.warning(f"File already exists: {filename}")
        constants.SpiderConfig.process_image_flag = True
        return True

    start_time = time.time()
    constants.SpiderConfig.process_image_flag = False

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            with open(filename, 'wb') as out_file:
                while chunk := response.read(1024):
                    out_file.write(chunk)
                    out_file.flush()

        download_time = time.time() - start_time
        file_size = os.path.getsize(filename)
        logger.info(f"Downloaded {filename} ({file_size} bytes) in {download_time:.2f}s")
        
        constants.SpiderConfig.process_image_flag = True
        return True
        
    except Exception as e:
        logger.warning(f"Download failed: {e}")
        return False


@logger.catch
def url_zip_all_process(zip_url_txt_list: List[str]) -> bool:
    """Process zip URLs from text files
    
    Args:
        zip_url_txt_list: List of text files containing zip URLs
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not zip_url_txt_list:
        logger.warning("No zip URL text files found")
        return False

    for txt_file in zip_url_txt_list:
        txt_path = Path(txt_file)
        new_file = txt_path.parent / f"{txt_path.stem}_result{txt_path.suffix}"
        
        if "_result" not in txt_path.stem:
            logger.warning(f"Creating result file: {new_file}")
            remove_duplicates_from_txt(str(txt_path), str(new_file))
            logger.success(f"Removed duplicates from {txt_path}")
            
        try:
            urls = new_file.read_text(encoding='utf-8').splitlines()
        except Exception as e:
            logger.error(f"Failed to read {new_file}: {e}")
            continue
            
        if not urls:
            logger.warning(f"No URLs found in {txt_file}")
            continue
            
        logger.info(f"Downloading zips from {txt_file}")
        for url in urls:
            download_all_zip(url, str(txt_path.parent))

    constants.SpiderConfig.download_gif_zip_flag = False
    logger.success(f"Processed {len(zip_url_txt_list)} URL files")
    return True


@logger.catch
def unzip_generate_gif() -> bool:
    """Unzip files and generate GIF videos
    
    Returns:
        bool: True if successful, False otherwise
    """
    zip_files = scan_directory_zip(constants.data_path)
    if not zip_files:
        logger.warning("No zip files found")
        return False
        
    return generate_gif_video(zip_files)
