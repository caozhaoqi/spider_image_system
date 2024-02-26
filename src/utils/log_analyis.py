import os
import re
from collections import Counter

# 日志文件路径
from loguru import logger

from model.LogModel import LogModel
from run import constants

# log_file_path = r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\run\log_dir\sis_2024-02-21.log'

# 错误信息正则表达式
connection_broken_error_pattern = r'ERROR.*unknown error.*Connection broken: IncompleteRead'
remote_disconnected_error_pattern = r'ERROR.*unknown error.*Connection aborted\. RemoteDisconnected'
not_found_error_pattern = r'ERROR.*Failed to download image from'
nginx_502_error_pattern = r'ERROR.*Failed to download image from'
connection_error_pattern = r'ERROR.*error, connect point url error, cur images index'
success_download_pattern = r'DEBUG.*Image saved as'
cannot_open_image_pattern = r'ERROR.*无法打开图片'
unknown_image_category_pattern = r'WARNING.*未知种类图片，待定:'
establish_error_pattern = 'ERROR.*unknown error'

# 解析错误详情的正则表达式
connection_broken_detail_pattern = r'detail: \((.*? bytes read, .*? more expected)\)'
remote_disconnected_detail_pattern = r'detail: \(Remote end closed connection without response\)'
not_found_detail_pattern = r'detail: <!DOCTYPE html>\n<html>\n\s*<h1>404 Not Found</h1>\n</html>\n'
nginx_502_detail_pattern = r'detail: <html>\r\n<head><title>502 Bad ' \
                           r'Gateway</title></head>\r\n<body>\r\n<center><h1>502 Bad ' \
                           r'Gateway</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n '
connection_detail_pattern = r'detail:(.+)'
success_detail_pattern = r'cur txt images download count: (\d+)'
cannot_open_image_detail_pattern = r'错误信息:*(\d+)'
unknown_image_category_detail_pattern = r'(\d{4}\.jpg|png|gif)$'
establish_error_detail_pattern = r'detail:(.+)'


# 读取日志文件并统计错误次数及解析原因
@logger.catch
def analyze_log_errors(file_path, error_pattern, detail_pattern):
    """

    :param file_path:
    :param error_pattern:
    :param detail_pattern:
    :return:
    """
    error_counts = Counter()
    detail_causes = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if re.search(error_pattern, line):
                # 匹配到错误行，增加错误计数
                error_counts['error'] += 1

                # 提取错误详情
                detail_match = re.search(detail_pattern, line)
                if detail_match:
                    detail = detail_match.group(1)
                    # 分析错误原因并增加对应原因的计数
                    parse_error_cause(detail, detail_causes)

    return error_counts, error_pattern


# 解析错误原因并添加到detail_causes字典中
@logger.catch
def parse_error_cause(detail, detail_causes):
    """

    :param detail:
    :param detail_causes:
    :return:
    """
    # 根据具体情况解析错误原因，这里只是简单地将detail作为原因
    cause = detail.strip()
    detail_causes[cause] = detail_causes.get(cause, 0) + 1


# 运行分析
@logger.catch
def log_analyze(log_file_path):
    """

    :param log_file_path:
    :return:
    """
    error_list = []
    error_detail_list = []
    connection_broken_error_counts, connection_broken_error_detail = analyze_log_errors(
        log_file_path,
        connection_broken_error_pattern,
        connection_broken_detail_pattern)
    connection_disconnection_error_counts, connection_disconnection_error_detail = analyze_log_errors(
        log_file_path,
        remote_disconnected_error_pattern,
        remote_disconnected_detail_pattern)
    not_found_error_counts, not_found_error_detail = analyze_log_errors(log_file_path, not_found_error_pattern,
                                                                        not_found_detail_pattern)
    nginx_502_error_counts, nginx_502_error_detail = analyze_log_errors(log_file_path, nginx_502_error_pattern,
                                                                        nginx_502_detail_pattern)
    connection_error_counts, connection_error_detail = analyze_log_errors(log_file_path, connection_error_pattern,
                                                                          connection_detail_pattern)
    success_download_counts, success_download_detail = analyze_log_errors(log_file_path, success_download_pattern,
                                                                          success_detail_pattern)
    cannot_open_image_counts, cannot_open_image_detail = analyze_log_errors(log_file_path, cannot_open_image_pattern,
                                                                            cannot_open_image_detail_pattern)
    unknown_image_category_counts, unknown_image_category_detail = analyze_log_errors(
        log_file_path,
        unknown_image_category_pattern,
        unknown_image_category_detail_pattern)
    establish_error_counts, establish_error_detail = analyze_log_errors(log_file_path, establish_error_pattern,
                                                                        establish_error_detail_pattern)
    error_list.append(connection_broken_error_counts)
    error_list.append(connection_disconnection_error_counts)
    error_list.append(not_found_error_counts)
    error_list.append(nginx_502_error_counts)
    error_list.append(connection_error_counts)
    error_list.append(success_download_counts)
    error_list.append(cannot_open_image_counts)
    error_list.append(unknown_image_category_counts)
    error_list.append(establish_error_counts)
    error_detail_list.append(connection_broken_error_detail)
    error_detail_list.append(connection_disconnection_error_detail)
    error_detail_list.append(not_found_error_detail)
    error_detail_list.append(nginx_502_error_detail)
    error_detail_list.append(connection_error_detail)
    error_detail_list.append(success_download_detail)
    error_detail_list.append(cannot_open_image_detail)
    error_detail_list.append(unknown_image_category_detail)
    error_detail_list.append(establish_error_detail)
    return error_list, error_detail_list


@logger.catch
def find_log(directory):
    """
    find image from current dir data
    :param directory:
    :return:
    """
    log_files_lists = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info("dir not exists, create dir: " + str(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.log'):
                log_files_lists.append(os.path.join(root, file))
    return log_files_lists


@logger.catch
def log_data_analyze():
    """

    :return:
    """
    log_analyze_data = []
    log_dir = os.path.realpath('./log_dir')
    log_list = find_log(log_dir)
    for log_index, log_content in enumerate(log_list):
        log_list_content = []
        result_count_list, result_detail_list = log_analyze(log_content)
        log_list_content.append(result_count_list)
        log_list_content.append(result_detail_list)
        log_list_content.append(log_content)
        log_analyze_data.append(log_list_content)
    logger.info(f"scan log end finish, scan result log length: {len(log_list)}")
    return log_analyze_data


@logger.catch
def log_analyze_data_output():
    """
    log andlyze data analyze
    :return:
    """
    data = log_data_analyze()
    data_list = []
    data_list_set = []
    for line in data:
        #     log_list_content.append(result_count_list)
        #         log_list_content.append(result_detail_list)
        #         log_list_content.append(log_content)
        #         log_analyze_data.append(log_list_content)
        file_name = line[2]
        error_count = line[0]
        error_name_list = []
        error_count_list = []
        error_count_zero_list = []
        for index, error_detail_count in enumerate(error_count):
            if error_detail_count['error']:
                error_count_list.append(error_detail_count['error'])
            else:
                # error_count_list.append(0)
                error_count_zero_list.append(index)

        error_details = line[1]
        for index, error_details_d in enumerate(error_details):
            if index in error_count_zero_list:
                continue
            else:
                error_name_list.append(error_details_d[7:])
        error_count_list, error_name_list = mege_same_value(error_name_list, error_count_list)
        if error_count_list != [] and error_count_list != []:
            data_list_set.append(error_name_list)
            data_list_set.append(error_count_list)
        if file_name != '' and file_name:
            data_list_set.append(file_name)
        data_list.append(data_list_set)
        error_count_zero_list.clear()
    return data_list


@logger.catch
def log_analyze_data_output_new():
    """
    log andlyze data analyze
    :return:
    """
    data = log_data_analyze()
    error_name_list = []
    error_count_list = []
    error_count_zero_list = []
    for line in data:
        file_name = line[2]
        error_count = line[0]

        for index, error_detail_count in enumerate(error_count):
            if error_detail_count['error']:
                error_count_list.append(error_detail_count['error'])
            else:
                error_count_zero_list.append(index)

        error_details = line[1]
        for index, error_details_d in enumerate(error_details):
            if index in error_count_zero_list:
                continue
            else:
                if error_details_d and error_details_d != '':
                    error_name_list.append(error_details_d)
        error_count_zero_list.clear()
    error_count_new_list, error_name_list_new = mege_same_value(error_name_list, error_count_list)
    return error_count_new_list, error_name_list_new


@logger.catch
def find_duplicates_indices(list_data):
    """

    :param list_data:
    :return:
    """

    indices_dict = {}
    duplicates_indices = []

    for i, val in enumerate(list_data):
        if val in indices_dict:
            duplicates_indices.append((indices_dict[val], i))
            indices_dict[val].append(i)
        else:
            indices_dict[val] = [i]

    return duplicates_indices


@logger.catch
def mege_same_value(labels, values):
    """

    :param labels:
    :param values:
    :return:
    """
    # 确保两个列表长度相同
    assert len(labels) == len(values), "Labels and values lists must have the same length"

    # 使用字典来合并相同标签的值
    merged_dict = {}
    for label, value in zip(labels, values):
        if label in merged_dict:
            merged_dict[label] += value
        else:
            merged_dict[label] = value

    # 从字典中提取标签和合并后的值，创建新的列表
    new_labels = list(merged_dict.keys())
    new_values = list(merged_dict.values())
    return new_labels, new_values


if __name__ == '__main__':
    data_list = log_analyze_data_output()
    for data in data_list:
        log_name = data[2]
        error_count = data[1]
        error_name = data[0]
    logger.info(f"{data_list[0]}, {data_list[1]}")
