import os.path
import re

import chardet
import codecs

from loguru import logger


@logger.catch
def convert_txt(input_file_path, output_file_path):
    """

    :param input_file_path:
    :param output_file_path:
    :return:
    """
    # 尝试的额外编码（例如：GBK, GB2312, GB18030等）
    alternative_encoding = 'gbk'

    # 用于记录乱码行数的列表
    corrupt_lines = []
    normal_lines = []
    read_lines = ''
    # 尝试使用UTF-8编码打开文件
    try:
        with codecs.open(input_file_path, 'r', encoding='gbk', errors='replace') as file:
            read_lines = file.readlines()
        with codecs.open(input_file_path, 'r', encoding='utf-8', errors='replace') as file:
            read_lines.extend(file.readlines())
    except Exception as e:
        logger.debug(f"无法以gbk编码打开文件: {e}")
        # exit(1)

    # 遍历文件的所有行，检查乱码
    with codecs.open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
        for line_num, line in enumerate(read_lines, start=1):
            try:
                # 尝试使用另一种编码解码行内容
                decoded_line = line.encode('utf-8').decode(alternative_encoding)
                # 如果解码成功，则写入输出文件
                output_file.write(decoded_line)
                normal_lines.append(line_num)
            except UnicodeDecodeError:
                # 如果解码失败，记录乱码行数
                corrupt_lines.append(line_num)
                logger.debug(f"检测到乱码行: {line_num}")

    # 打印乱码行信息
    set1 = set(normal_lines)
    set2 = set(corrupt_lines)

    # 使用集合的差集运算找出不同值
    # set1 - set2 会得到在set1中但不在set2中的元素
    # set2 - set1 会得到在set2中但不在set1中的元素
    different_values_in_set1 = set1 - set2
    different_values_in_set2 = set2 - set1

    # 如果你想找出两个列表中所有的不同值（即两个差集的并集）
    # corrupt_lines = different_values_in_set1 | different_values_in_set2
    # corrupt_lines = different_values_in_set1
    if corrupt_lines:
        logger.debug(f"以下行包含乱码，并已被跳过：{corrupt_lines}")
    else:
        logger.debug("未检测到乱码行。")

    # 如果你还想删除原文件中的乱码行，你可以创建一个新文件，只包含正常数据
    if corrupt_lines:
        with codecs.open(input_file_path, 'r', encoding='gbk', errors='replace') as file:
            lines = file.readlines()

        with codecs.open(output_file_path, 'w', encoding='utf-8', errors='replace') as cleaned_file:
            for line_num, line in enumerate(lines, start=1):
                if line_num not in corrupt_lines:
                    cleaned_file.write(line)

        logger.debug(f"已创建清理后的文件：cleaned_{output_file_path}")


@logger.catch
def get_encoding(file_path):
    """

    :param file_path:
    :return:
    """
    with open(file_path, 'rb') as f:
        return chardet.detect(f.read())['encoding']


@logger.catch
def txt_decode_convert(in_file_path):
    """
    Convert the text file encoding to UTF-8, removing invalid characters.

    :param in_file_path: Path to the text file to be converted.
    """
    file_path_front, file_name = os.path.split(in_file_path)
    file_name_front, file_ext = os.path.splitext(file_name)
    content = ''
    try:
        # 尝试使用检测到的编码读取文件
        encoding = 'gbk'
        with codecs.open(in_file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        # 去除UTF-8中的乱码（替代字符）

        with codecs.open(in_file_path, 'r', encoding='utf-8', errors='replace') as f:
            content += f.read()

        # content = re.sub(r'[\xEF\xBF\xBD]+', '', content)
        content = re.sub(r'\\ufffd', '', content)
        # 定义一个正则表达式模式来匹配无效的UTF-8字符（即替换字符）
        # 在UTF-8中，这通常是'\ufffd'
        invalid_utf8_pattern = re.compile(r'[\ufffd]')

        # 使用正则表达式移除所有无效的UTF-8字符
        cleaned_content = invalid_utf8_pattern.sub('', content)

        # 将内容写入新文件，使用UTF-8编码
        output_file_path = os.path.join(file_path_front, file_name_front + "_utf8.txt")
        with codecs.open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    except Exception as e:
        # 如果读取失败，则使用UTF-8编码重新读取，并去除乱码
        # logger.warning(f"Detected encoding '{e}' caused an error, falling back to UTF-8.")
        logger.warning("unknown error!")
        # with codecs.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        #     content = f.read()
        #
        # # 去除UTF-8中的乱码（替代字符）
        # content = re.sub(r'[\xEF\xBF\xBD]+', '', content)

    logger.success(f"文件编码已转换为UTF-8并保存为：{output_file_path}")



if __name__ == '__main__':
    file_path = r'C:\Users\Administrator\PycharmProjects\spider_image_system\src\utils\spider_finished_keyword.txt'
    file_path_front, file_name = os.path.split(file_path)
    file_name_front, file_ext = os.path.splitext(file_name)
    output_file_path = os.path.join(file_path_front, file_name_front + "_utf8.txt")
    convert_txt(file_path, output_file_path)
    # mixed_content_file(file_path)
    # txt_decode_convert(file_path)
