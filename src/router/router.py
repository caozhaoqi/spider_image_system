# 导入OS模块
import os
import sys

# 把当前文件所在文件夹的父文件夹路径加入到PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter
from view import log_process

api_router = APIRouter()
# 模块路由配置
api_router.include_router(log_process.router, prefix="/sis", tags=['sis api 操作'])
