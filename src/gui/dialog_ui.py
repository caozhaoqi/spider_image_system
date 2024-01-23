import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QComboBox, QMessageBox
from loguru import logger

from src.utils.SpiderConfigModel import SpiderConfigModel
from src.utils.ini_file_spider import write_minio_config_to_file


class Dialog(QDialog):
    def __init__(self):
        """

        """
        super().__init__()
        self.s1_url_line = None
        self.s1_url_label = None
        self.visit_url_line = None
        self.visit_url_label = None
        self.r18_mode_label = None
        self.detail_delta_time_label = None
        self.search_delta_time_label = None
        self.proxy_flag_label = None
        self.s2_url_label = None
        self.target_url_label = None
        self.all_show_label = None
        self.comboBox_r18 = None
        self.detail_delta_time_line = None
        self.search_delta_time_line = None
        self.comboBox_proxy = None
        self.comboBox_all_show = None
        self.r18_mode_check = None
        self.target_url_line = None
        self.s2_url_line = None
        self.init_ui()

    @logger.catch
    def init_ui(self):
        """

        :return:
        """
        self.setWindowTitle('编辑工具配置')
        self.setFixedSize(600, 800)
        # 创建输入框和标签
        self.visit_url_label = QLabel('访问网站 URL:')
        self.visit_url_line = QLineEdit('pixiv.net')
        self.s1_url_label = QLabel('源1 图片服务器 URL:')
        self.s1_url_line = QLineEdit('i.pximg.net')
        self.s2_url_label = QLabel('源2 图片服务器 URL:')
        self.s2_url_line = QLineEdit('s.pximg.net')
        self.target_url_label = QLabel('目标 图片服务器 URL:')
        self.target_url_line = QLineEdit('pixiv.322333.xyz')
        self.r18_mode_label = QLabel('R18 模式:')
        self.comboBox_r18 = QComboBox(self)
        self.comboBox_r18.addItem("False")
        self.comboBox_r18.addItem("True")
        self.all_show_label = QLabel('全部显示:')
        self.comboBox_all_show = QComboBox(self)
        self.comboBox_all_show.addItem("False")
        self.comboBox_all_show.addItem("True")
        self.proxy_flag_label = QLabel('代理开关:')
        self.comboBox_proxy = QComboBox(self)
        self.comboBox_proxy.addItem("False")
        self.comboBox_proxy.addItem("True")
        # self.proxy_flag_check = QPushButton('True')
        self.search_delta_time_label = QLabel('搜索延迟时间:')
        self.search_delta_time_line = QLineEdit('7')
        self.detail_delta_time_label = QLabel('详情延迟时间:')
        self.detail_delta_time_line = QLineEdit('3')

        # 创建保存和取消按钮
        save_button = QPushButton('保存')
        cancel_button = QPushButton('取消')

        # 布局设置
        layout = QVBoxLayout()

        layout.addWidget(self.s1_url_label)
        layout.addWidget(self.s1_url_line)

        layout.addWidget(self.s2_url_label)
        layout.addWidget(self.s2_url_line)

        layout.addWidget(self.visit_url_label)
        layout.addWidget(self.visit_url_line)

        layout.addWidget(self.target_url_label)
        layout.addWidget(self.target_url_line)

        layout.addWidget(self.r18_mode_label)
        layout.addWidget(self.comboBox_r18)

        layout.addWidget(self.all_show_label)
        layout.addWidget(self.comboBox_all_show)

        layout.addWidget(self.proxy_flag_label)
        layout.addWidget(self.comboBox_proxy)

        layout.addWidget(self.search_delta_time_label)
        layout.addWidget(self.search_delta_time_line)

        layout.addWidget(self.detail_delta_time_label)
        layout.addWidget(self.detail_delta_time_line)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

        # 连接信号和槽
        save_button.clicked.connect(lambda: save_data(self))
        cancel_button.clicked.connect(self.reject)


@logger.catch
def save_data(self):
    """

    :param self:
    :return:
    """
    s1_url = self.s1_url_line.text()
    s2_url = self.s2_url_line.text()
    visit_url = self.visit_url_line.text()
    target_url = self.target_url_line.text()
    r18_mode = self.comboBox_r18.currentText()
    all_show = self.comboBox_all_show.currentText()
    proxy_flag = self.comboBox_proxy.currentText()
    search_delta_time = int(self.search_delta_time_line.text()) if self.search_delta_time_line else None
    detail_delta_time = int(self.detail_delta_time_line.text()) if self.detail_delta_time_line else None
    # 在这里你可以根据需要保存这些数据，例如保存到文件或发送到服务器
    logger.debug(f"Source1 URL: {s1_url}")
    logger.debug(f"Source2 URL: {s2_url}")
    logger.debug(f"visit URL: {visit_url}")
    logger.debug(f"Target URL: {target_url}")
    logger.debug(f"R18 Mode: {r18_mode}")
    logger.debug(f"All Show: {all_show}")
    logger.debug(f"Proxy Flag: {proxy_flag}")
    logger.debug(f"Search Delta Time: {search_delta_time}")
    logger.debug(f"Detail Delta Time: {detail_delta_time}")
    spider_config = SpiderConfigModel()
    spider_config.s1_url = s1_url
    spider_config.s2_url = s2_url
    spider_config.visit_url = visit_url
    spider_config.target_url = target_url
    spider_config.r18_mode = r18_mode
    spider_config.all_show = all_show
    spider_config.proxy_flag = proxy_flag
    spider_config.search_delta_time = search_delta_time
    spider_config.detail_delta_time = detail_delta_time
    write_minio_config_to_file(minio_config=spider_config)
    # dialog = Dialog()
    QMessageBox.critical(self, u"保存", u"配置写入成功！")
    self.hide()
    pass
