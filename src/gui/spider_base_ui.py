import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QTabWidget, QWidget, QLineEdit, QPushButton, QHBoxLayout, \
    QLabel, QVBoxLayout, QScrollArea, QGridLayout, QSlider, QListWidget, QSizePolicy, QListView
from loguru import logger
from utils.base_event import about_message_lookup, visit_web, \
    edit_config_msg, stop_spider_image, stop_download_image


@logger.catch
def base_menu(self):
    """
    基础菜单
    :return:
    """
    # 创建菜单栏
    self.menu_bar = QMenuBar()
    self.image_menu = QMenu('图像', self.menu_bar)
    self.start_spider_action = QAction('开始爬取', self.image_menu)
    self.stop_spider_action = QAction('停止爬取', self.image_menu)
    self.stop_spider_action.triggered.connect(lambda: stop_spider_image())
    self.stop_download_action = QAction('停止下载', self.image_menu)
    self.stop_download_action.triggered.connect(lambda: stop_download_image())
    self.other_spider_action = QAction('其他', self.image_menu)
    self.image_menu.addAction(self.start_spider_action)
    self.image_menu.addAction(self.stop_spider_action)
    self.image_menu.addAction(self.stop_download_action)
    self.image_menu.addAction(self.other_spider_action)

    self.video_menu = QMenu('视频', self.menu_bar)
    self.start_generate_action = QAction('开始生成', self.video_menu)
    self.stop_generate_action = QAction('停止生成', self.video_menu)
    self.video_other_action = QAction('其他', self.video_menu)
    self.video_menu.addAction(self.start_generate_action)
    self.video_menu.addAction(self.stop_generate_action)
    self.video_menu.addAction(self.video_other_action)

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
    # 创建选项卡
    self.tab_widget = QTabWidget()
    self.tab1 = QWidget()
    self.tab2 = QWidget()
    self.tab3 = QWidget()
    self.tab_widget.addTab(self.tab1, '图像')
    self.tab_widget.addTab(self.tab2, '视频')
    self.tab_widget.addTab(self.tab3, '其他')
    # 创建表格和设置列名
    return self.tab1, self.tab2, self.tab3, self.tab_widget


@logger.catch
def tab_1_ui_paint(self):
    """

    :param self:
    :return:
    """
    # 搜索栏内容绘制
    search_item_paint(self)

    self.h_box_2 = QHBoxLayout()

    self.label = QLabel(self)
    # 创建一个QScrollArea实例
    self.scroll_area = QScrollArea()
    # 将label添加到scroll_area中
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

    # 创建布局并将表格添加到布局中
    self.tab1.setLayout(self.vbox)
    self.setCentralWidget(self.tab_widget)

    # 基础事件 按钮单击事件
    self.input_file.clicked.connect(self.input_keyword_process)
    self.download_video_button.clicked.connect(self.download_file_thread)
    self.next_button.clicked.connect(self.next_img)
    self.before_button.clicked.connect(self.before_img)
    return True


@logger.catch
def tab_2_ui_paint(self):
    # 搜索栏内容绘制 标题头部显示信息主要包括：文件名 文件名乘 图片数量信息
    search_item_paint_tab2(self)

    # 水平布局  video play布局
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
    # 将label添加到scroll_area中
    self.scroll_area_video.setLayout(self.h_box_1_list)

    # self.scroll_area_video.setWidget(self.listWidget_1)

    # self.scroll_area_video.setFixedSize()
    self.scroll_area_video.setParent(self.tab2)
    # 设置滚动区域的大小策略，使其根据内容自动调整大小
    self.scroll_area_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    # self.scroll_area_video.resize(self.listWidget.maximumSize())
    self.h_box_2_video.addWidget(self.scroll_area_video)
    # 创建用于控制播放的按钮
    self.play_video_button = QPushButton(u"播放")
    self.pause_button_video = QPushButton(u"暂停")
    self.generate_button_video = QPushButton(u"生成")

    # 创建用于控制播放进度的滑块
    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(0, 200)  # 设置滑块范围为0-200
    self.slider.setValue(0)  # 设置初始值为0
    self.slider.setTickPosition(QSlider.TicksBelow)  # 在滑块下方显示刻度
    self.slider.setTickInterval(20)  # 设置刻度间隔为20

    # slider 和 video 布局集合  垂直布局 -
    #                                -
    self.v_box_video_slider_layout = QVBoxLayout()
    self.v_box_video_slider_layout.addLayout(self.h_box_2_video)
    self.v_box_video_slider_layout.addWidget(self.slider)

    # 按钮布局 水平布局 - - -
    self.h_box_3_video = QHBoxLayout()
    self.h_box_3_video.addWidget(self.generate_button_video)
    self.h_box_3_video.addWidget(self.play_video_button)
    # self.h_box_3_video.addWidget(self.pause_button_video)

    # 整体布局 垂直布局
    self.vbox_video = QVBoxLayout()
    self.vbox_video.addLayout(self.grid_layout_video)
    self.vbox_video.addLayout(self.v_box_video_slider_layout)
    self.vbox_video.addLayout(self.h_box_3_video)

    # 创建布局并将表格添加到布局中
    self.tab2.setLayout(self.vbox_video)
    self.setCentralWidget(self.tab_widget)

    # 基础事件 按钮单击事件
    self.play_video_button.clicked.connect(self.play_video)
    self.pause_button_video.clicked.connect(self.pause_video)
    self.generate_button_video.clicked.connect(self.image_video_click)
    self.slider.valueChanged[int].connect(self.set_video_position_click)  # 连接滑块值变化信号和视频位置设置槽函数

    pass


@logger.catch
def search_item_paint(self):
    # 创建网格布局
    self.grid_layout = QGridLayout()
    self.setLayout(self.grid_layout)

    # 创建行和列的索引
    row = 0
    col = 0

    # 创建控件并添加到网格布局中
    self.file_text = QLineEdit(os.path.join(os.path.dirname(__file__), ""))  # 修改为你的路径
    self.grid_layout.addWidget(QLabel("关键字:"), row, col)
    self.grid_layout.addWidget(self.file_text, row, col + 1)  # 0 1
    row += 1
    col = 0

    self.input_file = QPushButton("开始抓取")
    self.grid_layout.addWidget(self.input_file, row - 1, col + 2)  # 0 3
    row += 1
    col += 1

    #     self.grid_layout.addWidget(self.file_name_label, 1, 1)
    self.file_name_show_label = QLabel("文件名：")  # 如果constants中定义了文件名文本，你可以使用constants.file_name_txt来替换"文件名:"
    self.grid_layout.addWidget(self.file_name_show_label, row - 1, col - 1)
    row = 0
    col = 0

    self.file_name_label = QLabel("file_name")
    self.grid_layout.addWidget(self.file_name_label, 1, 1)

    # 你可以继续添加其他控件到下一行，例如:
    self.show_page_label = QLabel("0/0")
    self.grid_layout.addWidget(self.show_page_label, 1, 2)


@logger.catch
def search_item_paint_tab2(self):
    # 创建网格布局
    self.grid_layout_video = QGridLayout()
    self.setLayout(self.grid_layout_video)

    # self.file_name_show_label_video = QLabel("文件名")  # 如果constants中定义了文件名文本，你可以使用constants.file_name_txt来替换"文件名:"
    # self.file_name_show_label_video.setFixedSize(150, 20)  # 设置宽度为200像素，高度自适应c
    # self.grid_layout_video.addWidget(self.file_name_show_label_video, 0, 1)
    #
    # self.file_name_label_video = QLabel("文件大小")
    # self.file_name_label_video.setFixedSize(20, 20)
    # self.grid_layout_video.addWidget(self.file_name_label_video, 0, 2)
    #
    # # 你可以继续添加其他控件到下一行，例如:
    # self.modify_video = QLabel("修改时间")
    # self.modify_video.setFixedSize(120, 20)
    # self.grid_layout_video.addWidget(self.modify_video, 0, 3)
    #
    # # 你可以继续添加其他控件到下一行，例如:
    # self.path_video = QLabel("路径")
    # self.path_video.setFixedSize(560, 20)
    # self.grid_layout_video.addWidget(self.path_video, 0, 4)
    #
    # # 你可以继续添加其他控件到下一行，例如:
    # self.format_video = QLabel("格式")
    # self.format_video.setFixedSize(80, 20)
    # self.grid_layout_video.addWidget(self.format_video, 0, 5)
    #
    # # 你可以继续添加其他控件到下一行，例如:
    # self.author_video = QLabel("作者")
    # self.author_video.setFixedSize(80, 20)
    # self.grid_layout_video.addWidget(self.author_video, 0, 6)


@logger.catch
def tab_3_ui_paint(self):
    """

    :param self:
    :return:
    """
    self.file_text_3 = QLineEdit(
        os.path.join(os.path.dirname(__file__), ""))
    self.input_file_3 = QPushButton(u"选择文件夹")
    self.h_box_3 = QHBoxLayout()
    self.h_box_3.addWidget(QLabel(u"数据路径:"))
    self.h_box_3.addWidget(self.file_text_3)
    self.h_box_3.addWidget(self.input_file_3)

    self.h_box_2_3 = QHBoxLayout()
    self.label_3 = QLabel(self)
    # 创建一个QScrollArea实例
    self.scroll_area_3 = QScrollArea()
    # 将label添加到scroll_area中
    self.scroll_area_3.setWidget(self.label_3)
    self.scroll_area_3.setParent(self.tab3)
    self.h_box_2_3.addWidget(self.scroll_area_3)

    self.un_normal_img_button = QPushButton(u"剔除异常图片")
    self.img_category_button = QPushButton(u"分类图片")
    self.h_box_3_3 = QHBoxLayout()
    self.h_box_3_3.addWidget(self.un_normal_img_button)
    self.h_box_3_3.addStretch()
    self.h_box_3_3.addWidget(self.img_category_button)

    self.vbox_3 = QVBoxLayout()
    self.vbox_3.addLayout(self.h_box_3)
    self.vbox_3.addLayout(self.h_box_2_3)
    self.vbox_3.addLayout(self.h_box_3_3)

    # 创建布局并将表格添加到布局中
    # layout = QVBoxLayout()
    # layout.addWidget(vbox)
    self.tab3.setLayout(self.vbox_3)
    self.setCentralWidget(self.tab_widget)

    # 基础事件 按钮单击事件
    self.input_file_3.clicked.connect(self.input_keyword_process_3)
    self.un_normal_img_button.clicked.connect(self.download_file_thread_3)
    self.img_category_button.clicked.connect(self.img_category_button_click)
    return True
