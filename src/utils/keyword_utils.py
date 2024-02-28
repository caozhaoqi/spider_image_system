import os

from loguru import logger
from pypinyin import lazy_pinyin, Style

from run import constants


@logger.catch
def exists_keyword_finish_txt(keyword):
    """
    exists keyword from download_finished_txt.txt
    :param keyword:
    :return:
    """
    keyword = ''.join(lazy_pinyin(keyword, style=Style.TONE3))
    txt_keyword = keyword+"_img.txt"
    exists_keyword_flag = False
    # read download_finish_keyword.txt
    file_name = os.path.join(constants.data_path, "download_finished_txt.txt")
    with open(file_name, 'r') as f:
        txt_list = f.readlines()

    for txt in txt_list:
        if txt_keyword in txt:
            exists_keyword_flag = True
            # logger.debug("exists keyword from download_finish_txt.txt")
            break
    if exists_keyword_flag:
        # 使用列表推导式创建新列表，不包含含有关键词的行
        filtered_txt_list = [txt for txt in txt_list if txt_keyword not in txt]

        # 将新列表写回文件，覆盖原内容
        with open(file_name, 'w', encoding='utf-8') as f:
            f.writelines(filtered_txt_list)
        logger.debug(f"already delete keyword_img: {txt_keyword} download_finish_txt.txt!")
        return True
    else:
        logger.info(f"not found exists keyword: {keyword} from download_finish_txt.txt!")
        return False
