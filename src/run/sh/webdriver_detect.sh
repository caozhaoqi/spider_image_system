filename="selenium-manager"

# 在当前目录及其子目录中搜索文件
found_path=$(find . -name "$filename" -type f -print -quit)

# 检查是否找到文件
if [ -n "$found_path" ]; then
    echo "find file path: $found_path"
    ./"$found_path" --browser chrome --debug
else
    echo "Error! not found file path: $filename"
fi
printf 'program already exited!'

# remove unuse /r command
# sed -i 's/\r//' your_script.sh