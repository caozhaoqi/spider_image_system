import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
from loguru import logger
from urllib3.exceptions import ProtocolError

from image.fail_image import process_error_image
from image.img_switch import find_images, image_exists, img_category_images, check_images
from utils.file_download import send_request
from utils.file_utils import remove_duplicates_from_txt
from utils.http_utils import image_url_re, match_img_result
from utils.minio_file import upload_image
from run import constants
from run.constants import data_path
from file.file_process import (
    read_end_download_image, save_download_end,
    update_download_continue_flag, record_download_finish_txt,
    exists_txt_from_finish, write_error_image
)


@logger.catch
def download_image(url: str, filename: str, total_count: int, current_index: int) -> None:
    """Download image from URL and save to file
    
    Args:
        url: Image URL to download
        filename: Local path to save image
        total_count: Total number of images to download
        current_index: Current image index
    """
    image_name = image_url_re(url)
    image_list = find_images(constants.data_path)
    
    if image_list and image_exists(image_name, image_list):
        return
        
    try:
        response = send_request(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            logger.debug(
                f"Image saved as {filename}, "
                f"Progress: {current_index}/{total_count}"
            )
        else:
            write_error_image(constants.data_path, url, filename)
            logger.error(
                f"Failed to download image from {url}, "
                f"Progress: {current_index}/{total_count}, "
                f"Error: {response.content}"
            )
            
    except (ConnectionError, ProtocolError) as e:
        write_error_image(constants.data_path, url, filename)
        logger.error(
            f"Connection error downloading {url}, "
            f"Progress: {current_index}/{total_count}, "
            f"Error: {str(e)}"
        )
    except Exception as e:
        write_error_image(constants.data_path, url, filename)
        logger.error(
            f"Unknown error downloading {url}, "
            f"Progress: {current_index}/{total_count}, "
            f"Error: {str(e)}"
        )


@logger.catch
def download_images_from_file(
    ui, file_path: str, txt_index: int, 
    final_url: str, continue_flag: bool
) -> None:
    """Download images from URLs listed in file
    
    Args:
        ui: UI instance for progress updates
        file_path: Path to file containing image URLs
        txt_index: Index of current text file
        final_url: URL to resume from if continuing
        continue_flag: Whether to continue from previous download
    """
    save_dir = os.path.splitext(file_path)[0] + "/images"
    os.makedirs(save_dir, exist_ok=True)

    with open(file_path, 'r', encoding='utf-8') as f:
        urls = f.readlines()
        
    total_count = len(urls)
    start_index = 0
    
    if continue_flag:
        for i, url in enumerate(urls):
            if url.strip() == final_url:
                start_index = i
                logger.warning(f"Resuming download from {final_url}")
                break
                
    for i, url in enumerate(urls[start_index:], start_index):
        if constants.SpiderConfig.stop_download_image_flag:
            save_download_end(i, file_path, url.strip(), txt_index)
            break
            
        url = url.strip()
        if not url:
            continue
            
        filename = os.path.join(save_dir, os.path.basename(url))
        
        if ui:
            keyword = match_img_result(os.path.dirname(file_path))
            ui.download_show_label.setText(
                f"Keyword: {keyword}, "
                f"Progress: {i+1}/{total_count}, "
                f"File: {image_url_re(url)}"
            )
            
        download_image(url, filename, total_count, i)


@logger.catch
def download_img_txt(ui) -> bool:
    """Process and download images from all text files
    
    Args:
        ui: UI instance for progress updates
        
    Returns:
        bool: True if successful, False otherwise
    """
    txt_files = [
        os.path.join(root, f) 
        for root, _, files in os.walk(data_path)
        for f in files if f.endswith("_img.txt")
    ]
    
    if not txt_files:
        logger.warning("No image text files found")
        constants.SpiderConfig.stop_download_image_flag = True
        return False
        
    for i, txt_path in enumerate(txt_files):
        if constants.SpiderConfig.stop_download_image_flag:
            if ui:
                ui.download_show_label.setText("0/0")
                ui.sys_tips("Download stopped")
            break
            
        try:
            if not exists_txt_from_finish(txt_path):
                logger.info(f"Processing {txt_path} ({i+1}/{len(txt_files)})")
                
                download_info = read_end_download_image()
                final_txt, final_url = download_info[1:3]
                continue_flag = download_info[4]
                
                if final_txt and continue_flag:
                    update_download_continue_flag()
                    logger.warning(f"Resuming from {txt_path}, URL: {final_url}")

                processed_path = remove_duplicates_from_txt(txt_path)
                download_images_from_file(ui, processed_path, i, final_url, continue_flag)
                
        except Exception as e:
            logger.warning(f"Error processing {txt_path}: {e}")
            
        process_image(ui, txt_path)
        
        if not constants.SpiderConfig.stop_download_image_flag:
            record_download_finish_txt(txt_path)
            
        if (constants.upload_minio_image_flag == 'True' and
            not constants.ProcessingConfig.category_image_flag and
            not constants.ProcessingConfig.check_images_flag):
            logger.debug("Uploading images to MinIO")
            upload_image(constants.basic_path)
        else:
            logger.warning(
                f"Skipping MinIO upload: "
                f"Flag={constants.upload_minio_image_flag}, "
                f"Category={constants.ProcessingConfig.category_image_flag}, "
                f"Check={constants.ProcessingConfig.check_images_flag}"
            )
            
    if ui:
        ui.success_tips("Download complete")
    else:
        logger.success("Download complete")
        
    constants.SpiderConfig.stop_download_image_flag = True
    return True


@logger.catch
def download_re_error_image() -> bool:
    """Retry downloading failed images
    
    Returns:
        bool: True if successful, False otherwise
    """
    error_file = os.path.join(constants.data_path, "download_fail_image.txt")
    
    try:
        with open(error_file, 'r', encoding='utf-8', errors='replace') as f:
            error_urls = f.readlines()
            
        if not error_urls:
            logger.warning("No failed downloads to retry")
            return False
            
        error_urls = process_error_image(error_urls)
        logger.success("Updated URLs with new domains")
        
        for i, line in enumerate(error_urls):
            url, keyword = line.strip().split(',')
            keyword = keyword or 'unknown_keyword'
            
            save_dir = os.path.join(
                constants.data_path,
                "img_url/re_download/img_url",
                f"{keyword}_img_result/images"
            )
            os.makedirs(save_dir, exist_ok=True)
            
            filename = os.path.join(save_dir, image_url_re(url))
            download_image(url.strip(), filename, len(error_urls), i)
            
        constants.SpiderConfig.download_image_re_flag = False
        logger.success("Retry downloads complete")
        return True
        
    except Exception as e:
        logger.error(f"Error retrying downloads: {e}")
        return False


@logger.catch
def process_image(ui, txt_path: str) -> None:
    """Process downloaded images - check for errors and categorize
    
    Args:
        ui: UI instance
        txt_path: Path to image text file
    """
    logger.debug("Checking for errors")
    constants.ProcessingConfig.check_images_flag = True
    threading.Thread(
        target=check_images,
        args=(ui, constants.data_path)
    ).start()

    logger.debug("Categorizing images") 
    constants.ProcessingConfig.category_image_flag = True
    threading.Thread(
        target=img_category_images,
        args=(ui, constants.data_path)
    ).start()


@logger.catch
def remove_error_image(ui) -> None:
    """Scan and remove error images
    
    Args:
        ui: UI instance for status updates
    """
    logger.info("Starting image scan...")
    threading.Thread(
        target=check_images,
        args=(ui, constants.data_path)
    ).start()


@logger.catch
def img_category_button(ui) -> None:
    """Start image categorization thread
    
    Args:
        ui: UI instance for status updates
    """
    logger.info("Starting image categorization...")
    threading.Thread(
        target=img_category_images,
        args=(ui, constants.data_path)
    ).start()