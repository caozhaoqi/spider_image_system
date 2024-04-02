import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QTabWidget, QWidget, QLineEdit, QPushButton, QHBoxLayout, \
    QLabel, QVBoxLayout, QScrollArea, QGridLayout, QSlider, QListWidget, QSizePolicy
from loguru import logger
from ui_event.base_event import auto_start_spider_image, stop_spider_image, stop_download_image, edit_config_msg, \
    visit_web, about_message_lookup, online_look_image, performance_monitor, auto_play_image, \
    log_analyze_ui, face_detect_action, convert_folder_name, encoding_tools_convert, detect_installed_flag, \
    user_upload_image, user_download_image, unzip_file_method


@logger.catch
def base_menu(self):
    """
    基础菜单
    :return:
    """
    self.menu_bar = QMenuBar()
    self.image_menu = QMenu('图像', self.menu_bar)
    self.start_spider_action = QAction('自动爬取', self.image_menu)
    self.start_spider_action.triggered.connect(lambda: auto_start_spider_image(self))
    self.stop_spider_action = QAction('停止爬取', self.image_menu)
    self.stop_spider_action.triggered.connect(lambda: stop_spider_image())
    self.stop_download_action = QAction('停止下载', self.image_menu)
    self.stop_download_action.triggered.connect(lambda: stop_download_image())
    self.online_look_action = QAction('在线查看', self.image_menu)
    self.online_look_action.triggered.connect(lambda: online_look_image())
    self.auto_all_image_action = QAction('自动浏览', self.image_menu)
    self.auto_all_image_action.triggered.connect(lambda: auto_play_image())
    self.image_face_detect_action = QAction('人脸识别', self.image_menu)
    self.image_face_detect_action.triggered.connect(lambda: face_detect_action())
    self.user_upload_image_action = QAction("手动上传", self.image_menu)
    self.user_upload_image_action.triggered.connect(lambda: user_upload_image())
    self.user_download_re_action = QAction("重新下载", self.image_menu)
    self.user_download_re_action.triggered.connect(lambda: user_download_image())
    self.image_menu.addAction(self.start_spider_action)
    self.image_menu.addAction(self.stop_spider_action)
    self.image_menu.addAction(self.stop_download_action)
    self.image_menu.addAction(self.online_look_action)
    self.image_menu.addAction(self.auto_all_image_action)
    self.image_menu.addAction(self.image_face_detect_action)
    self.image_menu.addAction(self.user_upload_image_action)
    self.image_menu.addAction(self.user_download_re_action)

    self.video_menu = QMenu('视频', self.menu_bar)
    self.start_generate_action = QAction('开始生成', self.video_menu)
    self.stop_generate_action = QAction('停止生成', self.video_menu)
    self.video_other_action = QAction('其他', self.video_menu)
    self.video_menu.addAction(self.start_generate_action)
    self.video_menu.addAction(self.stop_generate_action)
    self.video_menu.addAction(self.video_other_action)

    self.performance_menu = QMenu('性能', self.menu_bar)
    self.look_performance = QAction('性能监视', self.performance_menu)
    self.look_performance.triggered.connect(lambda: performance_monitor())
    self.performance_menu.addAction(self.look_performance)

    self.tools_menu = QMenu('工具', self.menu_bar)
    self.log_analyze = QAction('日志分析', self.tools_menu)
    self.folder_name = QAction('名称转换', self.tools_menu)
    self.encoding_tools = QAction('编码转换', self.tools_menu)
    self.test_driver = QAction('驱动检测', self.tools_menu)
    self.unzip_file_menu = QAction('解压文件', self.tools_menu)
    self.log_analyze.triggered.connect(lambda: log_analyze_ui())
    self.folder_name.triggered.connect(lambda: convert_folder_name())
    self.encoding_tools.triggered.connect(lambda: encoding_tools_convert())
    self.test_driver.triggered.connect(lambda:  detect_installed_flag())
    self.unzip_file_menu.triggered.connect(lambda: unzip_file_method())
    self.tools_menu.addAction(self.log_analyze)
    self.tools_menu.addAction(self.folder_name)
    self.tools_menu.addAction(self.encoding_tools)
    self.tools_menu.addAction(self.test_driver)
    self.tools_menu.addAction(self.unzip_file_menu)

    self.settings_menu = QMenu('设置', self.menu_bar)
    self.edit_settings_action = QAction('编辑配置', self.settings_menu)
    self.edit_settings_action.triggered.connect(lambda: edit_config_msg())
    self.settings_menu.addAction(self.edit_settings_action)
    self.help_menu = QMenu('帮助', self.menu_bar)
    self.help_web = QAction('访问网站', self.help_menu)
    self.help_menu.addAction(self.help_web)
    self.help_web.triggered.connect(lambda: visit_web())
    self.about_menu = QMenu('关于', self.menu_bar)
    self.about_msg = QAction('版本信息', self.about_menu)
    self.about_msg.triggered.connect(lambda: about_message_lookup())
    self.about_menu.addAction(self.about_msg)

    self.menu_bar.addMenu(self.image_menu)
    self.menu_bar.addMenu(self.video_menu)
    self.menu_bar.addMenu(self.performance_menu)
    self.menu_bar.addMenu(self.tools_menu)
    self.menu_bar.addMenu(self.settings_menu)
    self.menu_bar.addMenu(self.help_menu)
    self.menu_bar.addMenu(self.about_menu)
    return self.menu_bar


@logger.catch
def tab_ui_tab(self):
    """
    选项卡生成
    :return:
    """
    self.tab_widget = QTabWidget()
    self.tab1 = QWidget()
    self.tab2 = QWidget()
    self.tab3 = QWidget()
    self.tab_widget.addTab(self.tab1, '图像')
    self.tab_widget.addTab(self.tab2, '视频')
    self.tab_widget.addTab(self.tab3, '其他')
    return self.tab1, self.tab2, self.tab3, self.tab_widget


@logger.catch
def tab_1_ui_paint(self):
    """
    tab1 ui paint
    :param self:
    :return:
    """
    search_item_paint(self)

    self.h_box_2 = QHBoxLayout()

    self.label = QLabel(self)
    self.scroll_area = QScrollArea()
    self.scroll_area.setWidget(self.label)
    self.scroll_area.setParent(self.tab1)
    self.h_box_2.addWidget(self.scroll_area)

    self.download_video_button = QPushButton(u"开始下载")
    self.next_button = QPushButton(u"下一张")
    self.before_button = QPushButton(u"上一张")
    self.h_box_3 = QHBoxLayout()
    self.h_box_3.addWidget(self.before_button)
    self.h_box_3.addWidget(self.download_video_button)
    self.h_box_3.addWidget(self.next_button)

    self.vbox = QVBoxLayout()
    self.vbox.addLayout(self.grid_layout)
    self.vbox.addLayout(self.h_box_2)
    self.vbox.addLayout(self.h_box_3)

    self.tab1.setLayout(self.vbox)
    self.setCentralWidget(self.tab_widget)

    self.input_file.clicked.connect(self.input_keyword_process)
    self.download_video_button.clicked.connect(self.download_file_thread)
    self.next_button.clicked.connect(self.next_img)
    self.before_button.clicked.connect(self.before_img)
    self.jump_point_image.clicked.connect(self.jump_point_image_click)
    self.btn_zoom_in.clicked.connect(self.zoom_in_method)
    self.btn_zoom_out.clicked.connect(self.zoom_out_method)
    return True


@logger.catch
def tab_2_ui_paint(self):
    """
    tab2 ui paint
    :param self:
    :return:
    """
    search_item_paint_tab2(self)

    self.h_box_2_video = QHBoxLayout()
    self.h_box_1_list = QHBoxLayout()
    self.listWidget_1 = QListWidget(self)
    self.listWidget_2 = QListWidget(self)
    self.listWidget_3 = QListWidget(self)
    self.listWidget_4 = QListWidget(self)
    self.listWidget_5 = QListWidget(self)
    self.listWidget_6 = QListWidget(self)
    self.h_box_1_list.addWidget(self.listWidget_1, 15)
    self.h_box_1_list.addWidget(self.listWidget_2, 2)
    self.h_box_1_list.addWidget(self.listWidget_3, 12)
    self.h_box_1_list.addWidget(self.listWidget_4, 56)
    self.h_box_1_list.addWidget(self.listWidget_5, 8)
    self.h_box_1_list.addWidget(self.listWidget_6, 8)

    self.scroll_area_video = QScrollArea()
    self.scroll_area_video.setLayout(self.h_box_1_list)

    self.scroll_area_video.setParent(self.tab2)
    self.scroll_area_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.h_box_2_video.addWidget(self.scroll_area_video)
    self.play_video_button = QPushButton(u"播放")
    self.pause_button_video = QPushButton(u"暂停")
    self.generate_button_video = QPushButton(u"生成")

    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(0, 200)
    self.slider.setValue(0)
    self.slider.setTickPosition(QSlider.TicksBelow)
    self.slider.setTickInterval(20)

    self.v_box_video_slider_layout = QVBoxLayout()
    self.v_box_video_slider_layout.addLayout(self.h_box_2_video)
    self.v_box_video_slider_layout.addWidget(self.slider)

    self.h_box_3_video = QHBoxLayout()
    self.h_box_3_video.addWidget(self.generate_button_video)
    self.h_box_3_video.addWidget(self.play_video_button)

    self.vbox_video = QVBoxLayout()
    self.vbox_video.addLayout(self.grid_layout_video)
    self.vbox_video.addLayout(self.v_box_video_slider_layout)
    self.vbox_video.addLayout(self.h_box_3_video)

    self.tab2.setLayout(self.vbox_video)
    self.setCentralWidget(self.tab_widget)

    self.play_video_button.clicked.connect(self.play_video)
    self.pause_button_video.clicked.connect(self.pause_video)
    self.generate_button_video.clicked.connect(self.image_video_click)
    self.slider.valueChanged[int].connect(self.set_video_position_click)  # 连接滑块值变化信号和视频位置设置槽函数
    pass


@logger.catch
def search_item_paint(self):
    """
    search item ui add
    :param self:
    :return:
    """
    self.grid_layout = QGridLayout()
    self.setLayout(self.grid_layout)

    row = 0
    col = 0

    self.file_text = QLineEdit()
    self.grid_layout.addWidget(QLabel("关键字:"), row, col)
    self.grid_layout.addWidget(self.file_text, row, col + 1)  # 0 1
    row += 1
    col = 0

    self.input_file = QPushButton("开始抓取")
    self.grid_layout.addWidget(self.input_file, row - 1, col + 2)  # 0 3
    row += 1
    col += 1

    self.file_name_show_label = QLabel("文件名:")
    self.grid_layout.addWidget(self.file_name_show_label, row - 1, col - 1)

    self.file_name_label = QLabel("file_name")
    self.grid_layout.addWidget(self.file_name_label, 1, 1)

    self.show_page_label = QLabel("0/0")
    self.grid_layout.addWidget(self.show_page_label, 1, 2)

    self.image_search_label = QLabel("图片搜索:")
    self.grid_layout.addWidget(self.image_search_label, 2, 0)

    self.image_page = QLineEdit()
    self.grid_layout.addWidget(self.image_page, 2, 1)

    self.jump_point_image = QPushButton("跳转搜索")
    self.grid_layout.addWidget(self.jump_point_image, 2, 2)

    h_layout = QHBoxLayout()

    h_layout.addStretch()
    self.btn_zoom_in = QPushButton('放大', self)
    h_layout.addWidget(self.btn_zoom_in)

    self.btn_zoom_out = QPushButton('缩小', self)
    h_layout.addWidget(self.btn_zoom_out)
    self.grid_layout.addLayout(h_layout, 3, 1, 1, 3)


@logger.catch
def search_item_paint_tab2(self):
    self.grid_layout_video = QGridLayout()
    self.setLayout(self.grid_layout_video)


@logger.catch
def tab_3_ui_paint(self):
    """

    :param self:
    :return:
    """
    self.edt_input_file_text_3 = QLineEdit(
        os.path.join(os.path.dirname(__file__), ""))
    self.btn_input_file_3 = QPushButton(u"选择文件夹")
    self.h_box_3 = QHBoxLayout()
    self.h_box_3.addWidget(QLabel(u"数据路径:"))
    self.h_box_3.addWidget(self.edt_input_file_text_3)
    self.h_box_3.addWidget(self.btn_input_file_3)

    self.h_box_2_3 = QHBoxLayout()
    self.label_3 = QLabel(self)
    self.scroll_area_3 = QScrollArea()
    self.scroll_area_3.setWidget(self.label_3)
    self.scroll_area_3.setParent(self.tab3)
    self.h_box_2_3.addWidget(self.scroll_area_3)

    self.un_normal_img_button = QPushButton(u"剔除异常图片")
    self.img_category_button = QPushButton(u"分类图片")
    self.h_box_3_3 = QHBoxLayout()
    self.h_box_3_3.addWidget(self.un_normal_img_button)
    self.h_box_3_3.addWidget(self.img_category_button)

    self.download_gif_zip = QPushButton(u"下载压缩包")
    self.unzip_generate_video = QPushButton(u"解压生成视频")
    self.h_box_3_3.addWidget(self.download_gif_zip)
    self.h_box_3_3.addWidget(self.unzip_generate_video)

    self.download_video_zip = QPushButton(u"下载内容")
    self.h_box_3_3.addWidget(self.download_video_zip)

    self.vbox_3 = QVBoxLayout()
    self.vbox_3.addLayout(self.h_box_3)
    self.vbox_3.addLayout(self.h_box_2_3)
    self.vbox_3.addLayout(self.h_box_3_3)

    self.tab3.setLayout(self.vbox_3)
    self.setCentralWidget(self.tab_widget)

    self.btn_input_file_3.clicked.connect(self.input_keyword_process_3)
    self.un_normal_img_button.clicked.connect(self.remove_error_image_click)
    self.img_category_button.clicked.connect(self.img_category_button_click)
    self.download_gif_zip.clicked.connect(self.download_gif_zip_click)
    self.unzip_generate_video.clicked.connect(self.unzip_generate_video_click)
    self.download_video_zip.clicked.connect(self.download_video_zip_click)
    return True
