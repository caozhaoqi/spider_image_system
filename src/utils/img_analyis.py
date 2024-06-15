import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from run import constants
from image.img_switch import find_images
from utils.http_utils import match_img_result


@logger.catch
def img_analyze_data_output_new():
    """
    log analyze data analyze
    :return:
    """

    category_counts = {}
    data = find_images(constants.data_path)
    for img_path in data:
        category = match_img_result(img_path)

        if category not in category_counts:
            category_counts[category] = 0

        category_counts[category] += 1

    categories = list(category_counts.keys())

    counts = list(category_counts.values())

    return categories, counts

#
# if __name__ == '__main__':
#     img_analyze_data_output_new()
