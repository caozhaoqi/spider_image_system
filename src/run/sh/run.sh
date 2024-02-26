#!/bin/bash

# 指定待搜索的文件名
filename="ui_main.py"

# 在当前目录及其子目录中搜索文件
found_path=$(find . -name "$filename" -type f -print -quit)

# 检查是否找到文件
if [ -n "$found_path" ]; then
    echo "find file path: $found_path"
    python3 found_path
else
    echo "not found file path: $filename"
fi
printf 'programmer already exited!'