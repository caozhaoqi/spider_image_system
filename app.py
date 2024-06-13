# aliyun function compute start web code
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.run.sis_main_process import api_main

if __name__ == '__main__':
    api_main()
