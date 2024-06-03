JAR_PATH="./hserver-nsfw.jar"

# 日志文件路径
LOG_FILE="./run.log"

# 启动JAR文件并将输出重定向到日志文件
nohup java -jar $JAR_PATH > $LOG_FILE 2>&1 &

echo "JAR文件已启动，日志已保存到 $LOG_FILE"