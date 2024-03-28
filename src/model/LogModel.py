import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LogModel:
    error_count = ''
    error_name = ''
    error_index = 0


class LogListModel:
    log_index = 0
    log_name = ''
    log_model_list = []
