import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
model class define
"""


class SpiderKeyWordModel:
    """

    """

    def __init__(self, cur_keyword_txt, final_key_word, cur_page, continue_flag):
        """


        """
        self.cur_keyword_txt = cur_keyword_txt
        self.final_key_word = final_key_word
        self.cur_page = cur_page
        self.continue_flag = continue_flag

    cur_keyword_txt = ''
    final_key_word = ''
    cur_page = 1
    continue_flag = False
