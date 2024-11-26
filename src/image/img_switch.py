import os
import sys
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from PyQt5.QtGui import QPixmap
from loguru import logger
from PIL import Image
from run import constants
from run.constants import data_path

# Data path for images
folder_path = os.path.realpath(os.path.join(os.getcwd(), data_path))


@logger.catch
def find_images(directory: str) -> List[str]:
    """Find image files in the given directory
    
    Args:
        directory: Directory path to search for images
        
    Returns:
        List[str]: List of image file paths found
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
        
    image_files = []
    for root, _, files in os.walk(directory):
        if any(x in root for x in ["img_url", "according_pid_download_image"]):
            for file in files:
                if file.endswith(('.jpg', '.png')):
                    image_files.append(os.path.join(root, file))
    return image_files


@logger.catch
def image_exists(image_path: str, image_list: List[str]) -> bool:
    """Check if image exists in the list
    
    Args:
        image_path: Path of image to check
        image_list: List of existing image paths
        
    Returns:
        bool: True if image exists, False otherwise
    """
    return any(image_path in img for img in image_list)


@logger.catch
def show_filter_image(images_list: List[str]) -> List[str]:
    """Filter out small images and special categories
    
    Args:
        images_list: List of image paths to filter
        
    Returns:
        List[str]: Filtered list of image paths
    """
    filtered_images = []
    excluded_terms = ["square", "custom", "error_images", "small_images"]
    
    for image in images_list:
        path, name = os.path.split(image)
        if not any(term in name or term in path for term in excluded_terms):
            filtered_images.append(image)
            
    return filtered_images


current_image_index = 0
image_files = show_filter_image(find_images(folder_path))


@logger.catch
def show_next_image(self) -> None:
    """Show next image in UI"""
    try:
        global current_image_index, image_files
        current_image_index = (current_image_index + 1) % len(image_files)
        show_image(self, image_files[current_image_index])
        self.show_page_label.setText(f"{current_image_index}/{len(image_files)}")

    except Exception as e:
        logger.warning(f"Failed to show next image: {e}")


@logger.catch
def show_image(self, image_file: str) -> None:
    """Display image in UI
    
    Args:
        image_file: Path of image to display
    """
    full_path = os.path.join(folder_path, image_file)
    self.file_name_label.setText(full_path)
    self.pixmap_image_tab1 = QPixmap(full_path)
    self.label.setPixmap(self.pixmap_image_tab1)
    self.label.resize(self.pixmap_image_tab1.width(), self.pixmap_image_tab1.height())
    logger.info(f"Showing image: {full_path}")


@logger.catch
def show_current_file_name(image_file: str) -> str:
    """Get filename from full path
    
    Args:
        image_file: Full image file path
        
    Returns:
        str: Image filename
    """
    return os.path.split(image_file)[1]


@logger.catch
def check_images(self, image_path: str) -> None:
    """Check images for errors and small sizes
    
    Args:
        image_path: Directory containing images to check
    """
    image_lists = find_images(image_path)
    small_images = []
    error_images = []

    for filepath in image_lists:
        if not filepath.endswith(('.jpg', '.png')):
            continue
            
        if any(x in filepath for x in ["error_images", "small_images"]):
            continue

        try:
            with Image.open(filepath) as img:
                width, height = img.size
                if width <= 250 and height <= 250:
                    small_images.append(filepath)
        except Exception as e:
            error_images.append(filepath)

    # Process error images
    error_dir = os.path.join(image_path, "error_images")
    os.makedirs(error_dir, exist_ok=True)
    
    error_txt = os.path.join(image_path, 'error_image_txt.txt')
    for img in error_images:
        try:
            if 'error_images' not in img:
                with open(error_txt, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"{img}\n")
                shutil.move(img, os.path.join(error_dir, os.path.basename(img)))
        except Exception:
            logger.warning(f"Failed to process error image: {img}")

    # Process small images            
    small_dir = os.path.join(image_path, "small_images")
    os.makedirs(small_dir, exist_ok=True)
    
    small_txt = os.path.join(image_path, 'small_image_txt.txt')
    for img in small_images:
        try:
            if 'small_images' not in img:
                with open(small_txt, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"{img}\n")
                shutil.move(img, os.path.join(small_dir, os.path.basename(img)))
        except Exception:
            logger.warning(f"Failed to process small image: {img}")

    if constants.ProcessingConfig.check_images_flag:
        constants.ProcessingConfig.check_images_flag = False
        logger.success("Image check completed")
        
    if constants.ProcessingConfig.single_flag:
        logger.success("Single image scan completed")
        constants.single_flag = False


@logger.catch
def img_category_images(self, image_path: str) -> None:
    """Categorize images into custom/square/master folders
    
    Args:
        image_path: Directory containing images to categorize
    """
    image_lists = find_images(image_path)
    categories = {
        'custom': [],
        'square': [], 
        'master': []
    }

    for filepath in image_lists:
        if not filepath.endswith(('.jpg', '.png')):
            continue
            
        path, name = os.path.split(filepath)
        if any(x in path for x in categories.keys()):
            continue
            
        for category in categories:
            if category in name:
                categories[category].append(filepath)
                break

    for category, images in categories.items():
        for img in images:
            try:
                dir_path, file_name = os.path.split(img)
                category_dir = os.path.join(dir_path, category)
                os.makedirs(category_dir, exist_ok=True)
                
                txt_path = os.path.join(dir_path, f'{category}_image_txt.txt')
                with open(txt_path, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"{img}\n")
                shutil.move(img, os.path.join(category_dir, file_name))
            except Exception:
                logger.warning(f"Failed to categorize image: {img}")

    if constants.ProcessingConfig.category_image_flag:
        constants.ProcessingConfig.category_image_flag = False
        logger.success("Image categorization completed")
        
    if constants.ProcessingConfig.single_flag:
        logger.success("Single image categorization completed")
        constants.single_flag = False


@logger.catch
def error_img_update(url: str) -> bool:
    """Update error image list by removing fixed URL
    
    Args:
        url: URL to remove from error list
        
    Returns:
        bool: True if URL was found and removed, False otherwise
    """
    error_txt = os.path.join(constants.data_path, "download_fail_image.txt")
    if not os.path.exists(error_txt):
        return False
        
    try:
        with open(error_txt, "r", encoding='utf-8', errors='replace') as f:
            error_urls = f.readlines()
            
        if url in error_urls:
            error_urls.remove(url)
            with open(error_txt, 'w', encoding='utf-8', errors='replace') as f:
                f.writelines(f"{u}\n" for u in error_urls)
            return True
            
    except Exception as e:
        logger.error(f"Failed to update error image list: {e}")
        
    return False
