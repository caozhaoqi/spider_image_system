"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

"""Router configuration for the SIS API"""
import os
import sys
from fastapi import APIRouter
from view import log_process

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create main router
api_router = APIRouter()

# Include SIS API routes
api_router.include_router(
    log_process.router,
    prefix="/sis",
    tags=["SIS API Operations"]
)
