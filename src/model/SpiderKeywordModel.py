"""Spider keyword model class for storing search keyword information"""
import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class SpiderKeywordModel:
    """Class representing spider search keyword configuration
    
    Attributes:
        cur_keyword_txt: Current keyword text being searched
        final_key_word: Final processed keyword 
        cur_page: Current page number being processed
        continue_flag: Flag indicating if processing should continue
    """
    cur_keyword_txt: str = ''
    final_key_word: str = ''
    cur_page: int = 1
    continue_flag: bool = False


    def __post_init__(self):
        """Validate data after initialization"""
        if not isinstance(self.cur_page, int):
            raise TypeError("cur_page must be an integer")
        if not isinstance(self.continue_flag, bool):
            raise TypeError("continue_flag must be a boolean")
