#!/bin/bash
echo 'before start, uninstall opencv-python-headless, install opencv-python.'
sudo pip uninstall opencv-python-headless
sudo pip install opencv-python -r https://pypi.tuna.tsinghua.edu.cn/simple
echo 'success, start operate:'
# 指定待搜索的文件名
filename="face_detect.py"

# 在当前目录及其子目录中搜索文件
found_path=$(find ../../ -name "$filename" -type f -print -quit)

# 检查是否找到文件
if [ -n "$found_path" ]; then
    echo "find file path: $found_path"
    python3 "$found_path"
    echo 'execute finished! start uninstall opencv-python, start install opencv-python-headless.'
    sudo pip uninstall opencv-python
    sudo pip install opencv-python-headless -r https://pypi.tuna.tsinghua.edu.cn/simple
    echo 'operate finished!'
else
    echo "Error! not found file path: $filename"
fi
printf 'program already exited!'