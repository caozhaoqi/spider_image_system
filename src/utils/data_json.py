import json

from loguru import logger

from run import constants
from utils.log_analyis import log_analyze_data_output


@logger.catch
def data_json(data):
    # 将数据转换为 JSON 字符串
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # 输出 JSON 字符串
    # print(json_data)

    # 如果您想将 JSON 字符串保存到文件中
    with open(constants.data_path + '/log_analyze_result.json', 'w', encoding='utf-8') as file:
        file.write(json_data)

    return json_data


if __name__ == '__main__':
    data_json(log_analyze_data_output())
