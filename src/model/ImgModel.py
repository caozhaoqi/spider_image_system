"""
test py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class KeyWordModel:
    def __init__(self):
        ...

    def __json__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def __repr__(self):
        ...

    index = 0
    name = ''
    cur_page = 0
    # reduce duplicates
    link_count = 0
    # reduce duplicates
    image_count = 0
    skip_flag = False
    all_finish = False
    download_image_count = 0
    download_image_finished = False
    error_image = 0
    small_image = 0
    master_image = 0
    other_image = 0
    video_gif = 0

