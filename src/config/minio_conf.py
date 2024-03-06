import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from run.constant import minio_password, minio_username, minio_ip, minio_port

# minio_config = {
#     # 'endpoint': '172.22.10.34:9000',
#     'endpoint': minio_ip + ':' + minio_port,
#     'access_key': minio_username,
#     'secret_key': minio_password,
#     'secure': False
# }
rehil_bucket = 'rehil-system-data'
