"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

from setuptools import setup, find_packages

setup(
    name="sis",  # 你的python项目包名
    version='1.1.8',
    description='spider image system',
    author="zhaoqi.cao",
    author_email='1150118968@qq.com',
    url='https://caozhaoqi.github.io',
    packages=find_packages(),  # find_packages()方法会自动寻找当前目录下名为packageName的包
)
