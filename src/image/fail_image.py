import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from run import constants
from typing import List


@logger.catch
def process_error_image(error_image_list: List[str]) -> List[str]:
    """Process error image URLs by replacing domain names
    
    Args:
        error_image_list: List of image URLs to process
        
    Returns:
        List[str]: Processed image URLs with replaced domains
    """
    new_error_image = []
    
    for error_image in error_image_list:
        processed_url = error_image
        
        if constants.s1_url in error_image or constants.s2_url in error_image:
            # Replace source domains with target domain
            processed_url = processed_url.replace(constants.s1_url, constants.target_url)
            processed_url = processed_url.replace(constants.s2_url, constants.target_url)
            
        elif constants.target_url in error_image:
            # Replace target domain with source domains
            processed_url = processed_url.replace(constants.target_url, constants.s1_url)
            processed_url = processed_url.replace(constants.target_url, constants.s2_url)
            
        new_error_image.append(processed_url)
            
    return new_error_image
