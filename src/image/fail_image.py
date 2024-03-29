import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from loguru import logger
from run import constants


@logger.catch
def process_error_image(error_image_list):
    """

    :param error_image_list:
    :return:
    """
    new_error_image = []
    for error_image in error_image_list:
        if constants.s1_url in error_image or constants.s2_url in error_image:
            error_image = error_image.replace(constants.s1_url, constants.target_url)
            error_image = error_image.replace(constants.s2_url, constants.target_url)
            new_error_image.append(error_image)
        elif constants.target_url in error_image:
            error_image = error_image.replace(constants.target_url, constants.s1_url)
            error_image = error_image.replace(constants.target_url, constants.s2_url)
            new_error_image.append(error_image)
        else:
            new_error_image.append(error_image)
    return new_error_image
