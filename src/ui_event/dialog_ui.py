import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QComboBox, QMessageBox, \
    QCheckBox, QHBoxLayout, QWidget
from loguru import logger
from run import constants
from file.ini_file_spider import write_minio_config_to_file
from run.constants import visit_url, s2_url, s1_url, target_url, spider_images_max_count, sis_log_level, r18_mode, \
    all_show, proxy_flag, proxy_server_ip, proxy_server_port, search_delta_time, detail_delta_time, output_video_fps, \
    output_video_width, output_video_height
from model.SpiderConfigModel import SpiderConfigModel


class Dialog(QDialog):
    def __init__(self):
        """

        """
        super().__init__()
        self.output_video_height_label = None
        self.output_video_height_line = None
        self.output_video_width_line = None
        self.output_video_width_label = None
        self.s1_proxy_server_port_line = None
        self.s1_proxy_server_port_label = None
        self.s1_proxy_server_ip_line = None
        self.s1_proxy_server_ip_label = None
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
        self.target_url_line = None
        self.s2_url_line = None
        self.init_ui()

    @logger.catch
    def init_ui(self):
        """

        :return:
        """
        self.setWindowTitle('编辑工具配置(Edit tools config)')
        self.setFixedSize(800, 800)
        # 创建输入框和标签
        self.visit_url_label = QLabel('访问网站 URL(visit_url):')
        self.visit_url_line = QLineEdit(visit_url)

        self.s1_url_label = QLabel('源1图片服务器URL(s1_url):')
        self.s1_url_line = QLineEdit(s1_url)

        self.s2_url_label = QLabel('源2图片服务器URL(s2_url):')
        self.s2_url_line = QLineEdit(s2_url)

        self.target_url_label = QLabel('目标图片服务器URL(target_url):')
        self.target_url_line = QLineEdit(target_url)

        self.spider_image_max_count_label = QLabel('抓取图片最大值(spider_img_max):')
        self.spider_image_max_count_line = QLineEdit(str(spider_images_max_count))

        self.sis_log_level_label = QLabel("日志级别(log_level)")
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

        self.s1_proxy_server_ip_label = QLabel('代理服务器地址(ip):')
        self.s1_proxy_server_ip_line = QLineEdit(proxy_server_ip)

        self.s1_proxy_server_port_label = QLabel('代理服务器端口(port):')
        self.s1_proxy_server_port_line = QLineEdit(str(proxy_server_port))

        self.search_delta_time_label = QLabel('搜索延迟时间(s):')
        self.search_delta_time_line = QLineEdit(str(search_delta_time))

        self.detail_delta_time_label = QLabel('详情延迟时间(s):')
        self.detail_delta_time_line = QLineEdit(str(detail_delta_time))

        self.output_video_fps_label = QLabel('输出视频帧率(fps):')
        self.output_video_fps_line = QLineEdit(str(output_video_fps))

        self.output_video_width_label = QLabel('输出视频宽度(16:9):')
        self.output_video_width_line = QLineEdit(str(output_video_width))

        self.output_video_height_label = QLabel('输出视频高度(16:9):')
        self.output_video_height_line = QLineEdit(str(output_video_height))

        # 创建保存和取消按钮
        save_button = QPushButton('保存(save)')
        cancel_button = QPushButton('取消(cancel)')

        # 布局设置
        layout = QVBoxLayout()

        window_visit_url = QWidget()
        h_layout_visit_url = QHBoxLayout(window_visit_url)
        h_layout_visit_url.addWidget(self.visit_url_label)
        h_layout_visit_url.addWidget(self.visit_url_line)
        layout.addWidget(window_visit_url)

        window_s1_url_label = QWidget()
        h_layout_s1_url_label = QHBoxLayout(window_s1_url_label)
        h_layout_s1_url_label.addWidget(self.s1_url_label)
        h_layout_s1_url_label.addWidget(self.s1_url_line)
        layout.addWidget(window_s1_url_label)

        window_s2_url_label = QWidget()
        h_layout_s2_url_label = QHBoxLayout(window_s2_url_label)
        h_layout_s2_url_label.addWidget(self.s2_url_label)
        h_layout_s2_url_label.addWidget(self.s2_url_line)
        layout.addWidget(window_s2_url_label)

        window_target_url_label = QWidget()
        h_layout_target_url_label = QHBoxLayout(window_target_url_label)
        h_layout_target_url_label.addWidget(self.target_url_label)
        h_layout_target_url_label.addWidget(self.target_url_line)
        layout.addWidget(window_target_url_label)

        window_log_image = QWidget()
        h_layout_log_image = QHBoxLayout(window_log_image)
        h_layout_log_image.addWidget(self.spider_image_max_count_label)
        h_layout_log_image.addWidget(self.spider_image_max_count_line)
        h_layout_log_image.addWidget(self.sis_log_level_label)
        h_layout_log_image.addWidget(self.comboBox_sis_log_level)
        layout.addWidget(window_log_image)

        window_video = QWidget()
        h_layout_video = QHBoxLayout(window_video)
        h_layout_video.addWidget(self.output_video_fps_label)
        h_layout_video.addWidget(self.output_video_fps_line)
        h_layout_video.addWidget(self.output_video_width_label)
        h_layout_video.addWidget(self.output_video_width_line)
        h_layout_video.addWidget(self.output_video_height_label)
        h_layout_video.addWidget(self.output_video_height_line)
        layout.addWidget(window_video)

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
        layout.addWidget(window)

        window_proxy = QWidget()
        h_layout_proxy = QHBoxLayout(window_proxy)
        h_layout_proxy.addWidget(self.s1_proxy_server_ip_label)
        h_layout_proxy.addWidget(self.s1_proxy_server_ip_line)

        h_layout_proxy.addWidget(self.s1_proxy_server_port_label)
        h_layout_proxy.addWidget(self.s1_proxy_server_port_line)
        layout.addWidget(window_proxy)

        window_delta_time = QWidget()
        h_layout_delta_time = QHBoxLayout(window_delta_time)
        h_layout_delta_time.addWidget(self.search_delta_time_label)
        h_layout_delta_time.addWidget(self.search_delta_time_line)

        h_layout_delta_time.addWidget(self.detail_delta_time_label)
        h_layout_delta_time.addWidget(self.detail_delta_time_line)
        layout.addWidget(window_delta_time)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

        # 连接信号和槽
        save_button.clicked.connect(lambda: save_data(self))
        cancel_button.clicked.connect(self.reject)

    def reject(self):
        """

        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('config msg dialog Dialog is cancel closing!')
        constants.edit_config_msg_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(Dialog, self).reject()

    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('config msg dialog Dialog is close closing!')
        constants.edit_config_msg_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(Dialog, self).closeEvent(event)


@logger.catch
def save_data(self):
    """
    save data ini file
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
    output_video_width_txt = self.output_video_width_line.text()
    output_video_height_txt = self.output_video_height_line.text()
    proxy_server_ip_txt = self.s1_proxy_server_ip_line.text()
    proxy_server_port_txt = self.s1_proxy_server_port_line.text()
    if self.checkBox_r18.isChecked():
        r18_mode_txt = True
    else:
        r18_mode_txt = False
    if self.checkBox_all_show.isChecked():
        all_show_txt = True
    else:
        all_show_txt = False
    if self.checkBox_proxy.isChecked():
        proxy_flag_txt = True
    else:
        proxy_flag_txt = False
    search_delta_time_txt = int(self.search_delta_time_line.text()) if self.search_delta_time_line else None
    detail_delta_time_txt = int(self.detail_delta_time_line.text()) if self.detail_delta_time_line else None
    logger.debug("update config ini file mgs: ")
    logger.debug(f"Source1 URL: {s1_url_txt}")
    logger.debug(f"Source2 URL: {s2_url_txt}")
    logger.debug(f"visit URL: {visit_url_txt}")
    logger.debug(f"Target URL: {target_url_txt}")
    logger.debug(f"R18 Mode: {r18_mode_txt}")
    logger.debug(f"All Show: {all_show_txt}")
    logger.debug(f"Proxy Flag: {proxy_flag_txt}")
    logger.debug(f"proxy server ip: {proxy_server_ip_txt}")
    logger.debug(f"proxy server port: {proxy_server_port_txt}")
    logger.debug(f"Search Delta Time: {search_delta_time_txt}")
    logger.debug(f"Detail Delta Time: {detail_delta_time_txt}")
    logger.debug(f"spider_images_max_count: {spider_images_max_count_txt}")
    logger.debug(f"sis_log_level: {sis_log_level_txt}")
    logger.debug(f"output_video_fps_txt: {output_video_fps_txt}")
    logger.debug(f"output_video_width: {output_video_width_txt}")
    logger.debug(f"output_video_height: {output_video_height_txt}")

    spider_config = SpiderConfigModel()
    spider_config.s1_url = s1_url_txt
    spider_config.s2_url = s2_url_txt
    spider_config.visit_url = visit_url_txt
    spider_config.target_url = target_url_txt
    spider_config.r18_mode = r18_mode_txt
    spider_config.all_show = all_show_txt
    spider_config.proxy_flag = proxy_flag_txt
    spider_config.proxy_server_ip = proxy_server_ip_txt
    spider_config.proxy_server_port = proxy_server_port_txt
    spider_config.search_delta_time = search_delta_time_txt
    spider_config.detail_delta_time = detail_delta_time_txt
    spider_config.spider_images_max_count = spider_images_max_count_txt
    spider_config.sis_log_level = sis_log_level_txt
    spider_config.output_video_fps = output_video_fps_txt
    spider_config.output_video_width = output_video_width_txt
    spider_config.output_video_height = output_video_height_txt
    if write_minio_config_to_file(minio_config=spider_config):
        QMessageBox(QMessageBox.Information, "保存", "配置写入成功,程序即将退出,请重新启动应用以使配置生效！").exec_()
        self.hide()
        constants.edit_config_msg_visible = False
        # sys.exit()
    else:
        QMessageBox(QMessageBox.Warning, "错误", "发生未知错误,写入配置失败,请检查log信息！").exec_()
    pass
