"""
sis running status code
wait complete ...
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sis_run_normal = 0
sis_process_ing = 0x01
sis_process_finish = 0x02

sis_run_error = -0x01
web_api_error = -0x02
app_error = -0x03
sis_process_error = -0x04
internet_connect_error = -0x05
system_res_warning = -0x06

web_api_success = 200

web_api_not_found = 400
web_api_author_fail = 401
web_api_server_error = 500

web_api_fail = -1
