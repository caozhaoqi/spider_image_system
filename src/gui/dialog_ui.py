import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QComboBox, QMessageBox, \
    QCheckBox, QHBoxLayout, QWidget
from loguru import logger

from gui.constants import visit_url, s1_url, s2_url, target_url, r18_mode, all_show, proxy_flag, \
    spider_images_max_count, search_delta_time, detail_delta_time, output_video_fps, sis_log_level
from utils.SpiderConfigModel import SpiderConfigModel
from utils.ini_file_spider import write_minio_config_to_file


class Dialog(QDialog):
    def __init__(self):
        """

        """
        super().__init__()
        self.detail_delta_time_label = None
        self.output_video_fps_line = None
        self.sis_log_level_label = None
        self.comboBox_sis_log_level = None
        self.spider_image_max_count_line = None
        self.spider_image_max_count_label = None
        self.s1_url_line = None
        self.s1_url_label = None
        self.visit_url_line = None
        self.visit_url_label = None
        self.r18_mode_label = None
        self.output_video_fps_label = None
        self.search_delta_time_label = None
        self.proxy_flag_label = None
        self.s2_url_label = None
        self.target_url_label = None
        self.all_show_label = None
        self.checkBox_r18 = None
        self.detail_delta_time_line = None
        self.search_delta_time_line = None
        self.checkBox_proxy = None
        self.checkBox_all_show = None
        # self.r18_mode_check = None
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
        self.visit_url_label = QLabel('访问网站 URL(visit_url):')
        self.visit_url_line = QLineEdit(visit_url)

        self.s1_url_label = QLabel('源1 图片服务器 URL(s1_url):')
        self.s1_url_line = QLineEdit(s1_url)

        self.s2_url_label = QLabel('源2 图片服务器 URL(s2_url):')
        self.s2_url_line = QLineEdit(s2_url)

        self.target_url_label = QLabel('目标 图片服务器 URL(target_url):')
        self.target_url_line = QLineEdit(target_url)

        self.spider_image_max_count_label = QLabel('抓取图片最大值:')
        self.spider_image_max_count_line = QLineEdit(spider_images_max_count)

        self.sis_log_level_label = QLabel("日志级别")
        self.comboBox_sis_log_level = QComboBox()
        self.comboBox_sis_log_level.addItem("INFO")
        self.comboBox_sis_log_level.addItem("DEBUG")
        self.comboBox_sis_log_level.addItem("ERROR")
        self.comboBox_sis_log_level.addItem("WARNING")
        index = self.comboBox_sis_log_level.findText(sis_log_level)  # 查找文本的索引
        if index >= 0:
            self.comboBox_sis_log_level.setCurrentIndex(index)  # 设置默认选中项

        self.r18_mode_label = QLabel('R18(r18_mode):')
        self.checkBox_r18 = QCheckBox(self)  # Converted to QCheckBox
        if r18_mode == 'True':
            self.checkBox_r18.setChecked(True)  # Set default state to False
        else:
            self.checkBox_r18.setChecked(False)

        self.all_show_label = QLabel('全显示(all_show):')
        self.checkBox_all_show = QCheckBox(self)  # Converted to QCheckBox
        if all_show == 'True':
            self.checkBox_all_show.setChecked(True)
        else:
            self.checkBox_all_show.setChecked(False)  # Set default state to False

        self.proxy_flag_label = QLabel('代理(proxy_flag):')
        self.checkBox_proxy = QCheckBox(self)  # Converted to QCheckBox
        if proxy_flag == 'True':
            self.checkBox_proxy.setChecked(True)
        else:
            self.checkBox_proxy.setChecked(False)  # Set default state to False

        self.search_delta_time_label = QLabel('搜索延迟时间(s):')
        self.search_delta_time_line = QLineEdit(str(search_delta_time))

        self.detail_delta_time_label = QLabel('详情延迟时间(s):')
        self.detail_delta_time_line = QLineEdit(str(detail_delta_time))

        self.output_video_fps_label = QLabel('输出视频帧率(fps/s):')
        self.output_video_fps_line = QLineEdit(str(output_video_fps))

        # 创建保存和取消按钮
        save_button = QPushButton('保存')
        cancel_button = QPushButton('取消')

        # 布局设置
        layout = QVBoxLayout()

        layout.addWidget(self.visit_url_label)
        layout.addWidget(self.visit_url_line)

        layout.addWidget(self.s1_url_label)
        layout.addWidget(self.s1_url_line)

        layout.addWidget(self.s2_url_label)
        layout.addWidget(self.s2_url_line)

        layout.addWidget(self.target_url_label)
        layout.addWidget(self.target_url_line)

        layout.addWidget(self.spider_image_max_count_label)
        layout.addWidget(self.spider_image_max_count_line)

        layout.addWidget(self.sis_log_level_label)
        layout.addWidget(self.comboBox_sis_log_level)

        layout.addWidget(self.output_video_fps_label)
        layout.addWidget(self.output_video_fps_line)

        window = QWidget()
        h_layout = QHBoxLayout(window)

        h_layout.addWidget(self.r18_mode_label)
        h_layout.addWidget(self.checkBox_r18)

        # 添加第二组控件
        h_layout.addWidget(self.all_show_label)
        h_layout.addWidget(self.checkBox_all_show)

        # 添加第三组控件
        h_layout.addWidget(self.proxy_flag_label)
        h_layout.addWidget(self.checkBox_proxy)

        window.setLayout(h_layout)
        # window.s(600,10)
        layout.addWidget(window)

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
    s1_url_txt = self.s1_url_line.text()
    s2_url_txt = self.s2_url_line.text()
    visit_url_txt = self.visit_url_line.text()
    target_url_txt = self.target_url_line.text()
    spider_images_max_count_txt = self.spider_image_max_count_line.text()
    sis_log_level_txt = self.comboBox_sis_log_level.currentText()
    output_video_fps_txt = self.output_video_fps_line.text()
    if self.checkBox_r18.isChecked():
        r18_mode_txt = True
    else:
        r18_mode_txt = False
    if self.checkBox_all_show.isChecked():
        all_show_txt = True
    else:
        all_show_txt = False
    # all_show_txt = self.checkBox_all_show.currentText()
    if self.checkBox_proxy.isChecked():
        proxy_flag_txt = True
    else:
        proxy_flag_txt = False
    search_delta_time_txt = int(self.search_delta_time_line.text()) if self.search_delta_time_line else None
    detail_delta_time_txt = int(self.detail_delta_time_line.text()) if self.detail_delta_time_line else None
    # 在这里你可以根据需要保存这些数据，例如保存到文件或发送到服务器
    logger.debug(f"Source1 URL: {s1_url_txt}")
    logger.debug(f"Source2 URL: {s2_url_txt}")
    logger.debug(f"visit URL: {visit_url_txt}")
    logger.debug(f"Target URL: {target_url_txt}")
    logger.debug(f"R18 Mode: {r18_mode_txt}")
    logger.debug(f"All Show: {all_show_txt}")
    logger.debug(f"Proxy Flag: {proxy_flag_txt}")
    logger.debug(f"Search Delta Time: {search_delta_time_txt}")
    logger.debug(f"Detail Delta Time: {detail_delta_time_txt}")
    logger.debug(f"spider_images_max_count: {spider_images_max_count_txt}")
    logger.debug(f"sis_log_level: {sis_log_level_txt}")
    logger.debug(f"output_video_fps_txt: {output_video_fps_txt}")

    spider_config = SpiderConfigModel()
    spider_config.s1_url = s1_url_txt
    spider_config.s2_url = s2_url_txt
    spider_config.visit_url = visit_url_txt
    spider_config.target_url = target_url_txt
    spider_config.r18_mode = r18_mode_txt
    spider_config.all_show = all_show_txt
    spider_config.proxy_flag = proxy_flag_txt
    spider_config.search_delta_time = search_delta_time_txt
    spider_config.detail_delta_time = detail_delta_time_txt
    spider_config.spider_images_max_count = spider_images_max_count_txt
    spider_config.sis_log_level = sis_log_level_txt
    spider_config.output_video_fps = output_video_fps_txt
    write_minio_config_to_file(minio_config=spider_config)
    # dialog = Dialog()
    QMessageBox.critical(self, u"保存", u"配置写入成功,程序即将退出,请重新启动应用配置！")
    self.hide()
    sys.exit()
    pass
