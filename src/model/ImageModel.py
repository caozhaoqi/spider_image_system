"""

"""


class ImageModel:

    def __init__(self, image_index, txt_name, image_url, image_name, download_date, txt_index, continue_flag):
        """

        :param image_index:
        :param txt_name:
        :param image_url:
        :param image_name:
        :param download_date:
        :param txt_index:
        """
        self.image_index = image_index
        self.txt_name = txt_name
        self.image_url = image_url
        self.image_name = image_name
        self.download_date = download_date
        self.txt_index = txt_index
        self.continue_flag = continue_flag

    image_index = 0
    txt_index = 0
    txt_name = ''
    image_url = ''
    image_name = ''
    download_date = ''
    continue_flag = False
