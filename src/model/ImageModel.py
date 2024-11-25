"""Image model class for storing image metadata and download information"""
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class ImageModel:
    """Class representing an image with its metadata"""
    image_index: int
    txt_name: str 
    image_url: str
    image_name: str
    download_date: datetime
    txt_index: int
    continue_flag: bool = False

    def __post_init__(self):
        """Validate data after initialization"""
        if not isinstance(self.image_index, int):
            raise TypeError("image_index must be an integer")
        if not isinstance(self.txt_index, int):
            raise TypeError("txt_index must be an integer")
        if not isinstance(self.continue_flag, bool):
            raise TypeError("continue_flag must be a boolean")
