#!/bin/bash

# 检查参数数量
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <target_folder> <source_folder>"
    exit 1
fi

# 获取参数
folder_name="$1"
src_name="$2"

# 创建目标文件夹
mkdir -p "$folder_name"

# 检查文件夹是否创建成功
if [ $? -ne 0 ]; then
    echo "Failed to create the folder '$folder_name'."
    exit 1
fi

# 克隆Git仓库到目标文件夹
git clone https://gitee.com/caozhaoqi/spider_image_system "$folder_name/spider_image_system"

# 检查Git克隆是否成功
if [ $? -ne 0 ]; then
    echo "Failed to clone the Git repository."
    exit 1
fi

# 修改新克隆仓库的权限
chmod -R 777 "$folder_name/spider_image_system"

# 切换到新克隆仓库的指定目录
cd "$folder_name/spider_image_system/src/run" || exit

# 将源文件夹中的数据移动到当前目录
if [ -d "$src_name/spider_image_system/src/run/data" ]; then
    mv "./$src_name/spider_image_system/src/run/data" "./$folder_name/spider_image_system/src/run"
else
    echo "Data directory not found in source folder: $src_name/spider_image_system/src/run/data"
    exit 1
fi

# 检查移动操作是否成功
if [ $? -ne 0 ]; then
    echo "Failed to move data directory."
    exit 1
fi

# 执行run.sh脚本
./sh/run.sh

# 检查run.sh脚本执行是否成功
if [ $? -ne 0 ]; then
    echo "Failed to execute run.sh script."
    exit 1
fi

echo "All operations completed successfully!"