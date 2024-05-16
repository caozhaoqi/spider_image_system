import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QWidget, QTextEdit
from loguru import logger
from run import constants


class KeywordDialog(QDialog):
    def __init__(self):
        """

        """
        super().__init__()
        self.keyword_label = None
        self.keyword_edt = None

        self.init_ui()

    @logger.catch
    def init_ui(self):
        """

        :return:
        """
        self.setWindowTitle('添加关键字(以,分割)')
        self.setFixedSize(600, 400)

        self.keyword_label = QLabel('关键字:')
        self.keyword_edt = QTextEdit()

        # 创建保存和取消按钮
        save_button = QPushButton('保存')
        cancel_button = QPushButton('取消')

        # 布局设置
        layout = QVBoxLayout()

        window_video = QWidget()
        h_layout_video = QHBoxLayout(window_video)
        h_layout_video.addWidget(self.keyword_label)
        h_layout_video.addWidget(self.keyword_edt)
        h_lay = QHBoxLayout(window_video)
        h_lay.addWidget(save_button)
        h_lay.addWidget(cancel_button)
        # layout.addWidget(save_button)
        # layout.addWidget(cancel_button)
        layout.addWidget(window_video)
        layout.addLayout(h_lay)
        self.setLayout(layout)

        # 连接信号和槽
        save_button.clicked.connect(lambda: save_data(self))
        cancel_button.clicked.connect(self.reject)

    @logger.catch
    def closeEvent(self, event, _=None):
        """
        对话框关闭
        :param _:
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('keyword Dialog is closing!')
        # constants.edit_config_msg_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(KeywordDialog, self).closeEvent(event)


@logger.catch
def save_data(self):
    """
    save data ini file
    :param self:
    :return:
    """
    #
    keyword_txt = self.keyword_edt.toPlainText()
    auto_spider_file_path = os.path.join(constants.data_path, "auto_spider_img")

    if not os.path.exists(auto_spider_file_path):
        os.makedirs(auto_spider_file_path)

    file_name = 'spider_img_keyword.txt'
    # 使用split()方法按','切割字符串
    split_string = keyword_txt.split(',')
    if not split_string or split_string == ['']:
        logger.warning(f"not input keyword: {keyword_txt}")
        return False
    full_file_path = os.path.join(auto_spider_file_path, file_name)
    # 打开文件以写入模式
    with open(full_file_path, 'w', encoding='utf-8') as file:
        # 将切割后的字符串逐行写入文件
        for item in split_string:
            file.write("%s\n" % item)

    logger.success(f"add success, please re click spider menu start spider: {keyword_txt}")
    # super(KeywordDialog, self).closeEvent(event)
    self.close()
