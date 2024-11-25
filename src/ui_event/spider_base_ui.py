import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMenuBar, QMenu, QAction, QTabWidget, QWidget, QLineEdit, QPushButton, QHBoxLayout,
    QLabel, QVBoxLayout, QScrollArea, QGridLayout, QSlider, QListWidget, QSizePolicy)
from loguru import logger

from ui_event.base_event import (
    auto_start_spider_image, stop_spider_image, stop_download_image, edit_config_msg,
    visit_web, about_message_lookup, online_look_image, performance_monitor, auto_play_image,
    log_analyze_ui, face_detect_action, convert_folder_name, encoding_tools_convert, detect_installed_flag,
    user_upload_image, user_download_image, unzip_file_method, add_keyword_alert, img_category_ana, model_detect_img,
    start_download_jm, jm_domain_test_method, jm_automatic_method, stop_jm_spider, jm_category_image_method,
    go_file_upload_all
)


@logger.catch
def base_menu(self):
    """Create and return the main menu bar"""
    menu_bar = QMenuBar()
    
    # Image Menu
    image_menu = QMenu('图像', menu_bar)
    image_actions = {
        '自动爬取': lambda: auto_start_spider_image(self),
        '关键字': add_keyword_alert,
        '停止爬取': stop_spider_image,
        '停止下载': stop_download_image,
        '在线查看': online_look_image,
        '自动浏览': auto_play_image,
        '人脸识别': face_detect_action,
        '手动上传': user_upload_image,
        'gofile上传': go_file_upload_all,
        '重新下载': user_download_image,
        'AI鉴图': model_detect_img
    }
    
    for name, handler in image_actions.items():
        action = QAction(name, image_menu)
        action.triggered.connect(handler)
        image_menu.addAction(action)

    # Video Menu  
    video_menu = QMenu('视频', menu_bar)
    video_actions = ['开始生成', '停止生成', '其他']
    for name in video_actions:
        video_menu.addAction(QAction(name, video_menu))

    # JM Menu
    jm_menu = QMenu('JM', menu_bar)
    jm_actions = {
        'JM下载': start_download_jm,
        'JM检测': jm_domain_test_method,
        'JM自动': jm_automatic_method,
        '停止JM': stop_jm_spider,
        'JM处理': jm_category_image_method
    }
    
    for name, handler in jm_actions.items():
        action = QAction(name, jm_menu)
        action.triggered.connect(handler)
        jm_menu.addAction(action)

    # Performance Menu
    performance_menu = QMenu('性能', menu_bar)
    perf_action = QAction('性能监视', performance_menu)
    perf_action.triggered.connect(performance_monitor)
    performance_menu.addAction(perf_action)

    # Tools Menu
    tools_menu = QMenu('工具', menu_bar)
    tools_actions = {
        '图片分析': img_category_ana,
        '日志分析': log_analyze_ui,
        '名称转换': convert_folder_name,
        '编码转换': encoding_tools_convert,
        '驱动检测': detect_installed_flag,
        '解压文件': unzip_file_method
    }
    
    for name, handler in tools_actions.items():
        action = QAction(name, tools_menu)
        action.triggered.connect(handler)
        tools_menu.addAction(action)

    # Settings Menu
    settings_menu = QMenu('设置', menu_bar)
    settings_action = QAction('编辑配置', settings_menu)
    settings_action.triggered.connect(edit_config_msg)
    settings_menu.addAction(settings_action)

    # Help Menu
    help_menu = QMenu('帮助', menu_bar)
    help_action = QAction('访问网站', help_menu)
    help_action.triggered.connect(visit_web)
    help_menu.addAction(help_action)

    # About Menu
    about_menu = QMenu('关于', menu_bar)
    about_action = QAction('版本信息', about_menu)
    about_action.triggered.connect(about_message_lookup)
    about_menu.addAction(about_action)

    # Add all menus to menu bar
    menus = [image_menu, video_menu, jm_menu, performance_menu, 
             tools_menu, settings_menu, help_menu, about_menu]
    for menu in menus:
        menu_bar.addMenu(menu)

    return menu_bar


@logger.catch
def tab_ui_tab(self):
    """Create and return the main tab widget with three tabs"""
    tab_widget = QTabWidget()
    tab1 = QWidget()
    tab2 = QWidget()
    tab3 = QWidget()
    
    tab_widget.addTab(tab1, '图像')
    tab_widget.addTab(tab2, '视频') 
    tab_widget.addTab(tab3, '其他')
    
    return tab1, tab2, tab3, tab_widget


@logger.catch
def tab_1_ui_paint(self):
    """Paint UI for tab 1 (Image tab)"""
    search_item_paint(self)

    # Create scroll area for image display
    h_box_2 = QHBoxLayout()
    label = QLabel(self)
    scroll_area = QScrollArea()
    scroll_area.setWidget(label)
    scroll_area.setParent(self.tab1)
    h_box_2.addWidget(scroll_area)

    # Create button row
    h_box_3 = QHBoxLayout()
    buttons = {
        'before_button': '上一张',
        'download_video_button': '开始下载',
        'next_button': '下一张'
    }
    
    for btn_name, btn_text in buttons.items():
        setattr(self, btn_name, QPushButton(btn_text))
        h_box_3.addWidget(getattr(self, btn_name))

    # Layout everything vertically
    vbox = QVBoxLayout()
    vbox.addLayout(self.grid_layout)
    vbox.addLayout(h_box_2)
    vbox.addLayout(h_box_3)

    self.tab1.setLayout(vbox)
    self.setCentralWidget(self.tab_widget)

    # Connect signals
    self.input_file.clicked.connect(self.input_keyword_process)
    self.download_video_button.clicked.connect(self.download_file_thread)
    self.next_button.clicked.connect(self.next_img)
    self.before_button.clicked.connect(self.before_img)
    self.jump_point_image.clicked.connect(self.jump_point_image_click)
    self.btn_zoom_in.clicked.connect(self.zoom_in_method)
    self.btn_zoom_out.clicked.connect(self.zoom_out_method)
    self.btn_open_data.clicked.connect(self.open_data_dir)
    self.btn_show_log.clicked.connect(self.show_log_output)

    return True


@logger.catch 
def tab_2_ui_paint(self):
    """Paint UI for tab 2 (Video tab)"""
    search_item_paint_tab2(self)

    # Create list widgets layout
    h_box_1_list = QHBoxLayout()
    list_widgets = []
    list_widths = [15, 2, 12, 56, 8, 8]
    
    for i, width in enumerate(list_widths):
        list_widget = QListWidget(self)
        list_widgets.append(list_widget)
        h_box_1_list.addWidget(list_widget, width)
        setattr(self, f'listWidget_{i+1}', list_widget)

    # Create scroll area
    scroll_area_video = QScrollArea()
    scroll_area_video.setLayout(h_box_1_list)
    scroll_area_video.setParent(self.tab2)
    scroll_area_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    h_box_2_video = QHBoxLayout()
    h_box_2_video.addWidget(scroll_area_video)

    # Create buttons
    buttons = {
        'play_video_button': '播放',
        'pause_button_video': '暂停', 
        'generate_button_video': '生成'
    }
    
    for btn_name, btn_text in buttons.items():
        setattr(self, btn_name, QPushButton(btn_text))

    # Create slider
    slider = QSlider(Qt.Horizontal)
    slider.setRange(0, 200)
    slider.setValue(0)
    slider.setTickPosition(QSlider.TicksBelow)
    slider.setTickInterval(20)
    self.slider = slider

    # Layout everything
    v_box_video_slider_layout = QVBoxLayout()
    v_box_video_slider_layout.addLayout(h_box_2_video)
    v_box_video_slider_layout.addWidget(slider)

    h_box_3_video = QHBoxLayout()
    h_box_3_video.addWidget(self.generate_button_video)
    h_box_3_video.addWidget(self.play_video_button)

    vbox_video = QVBoxLayout()
    vbox_video.addLayout(self.grid_layout_video)
    vbox_video.addLayout(v_box_video_slider_layout)
    vbox_video.addLayout(h_box_3_video)

    self.tab2.setLayout(vbox_video)
    self.setCentralWidget(self.tab_widget)

    # Connect signals
    self.play_video_button.clicked.connect(self.play_video)
    self.pause_button_video.clicked.connect(self.pause_video)
    self.generate_button_video.clicked.connect(self.image_video_click)
    self.slider.valueChanged[int].connect(self.set_video_position_click)


@logger.catch
def search_item_paint(self):
    """Paint search items UI"""
    grid_layout = QGridLayout()
    self.setLayout(grid_layout)
    self.grid_layout = grid_layout

    # Create search input
    file_text = QLineEdit()
    grid_layout.addWidget(QLabel("关键字:"), 0, 0)
    grid_layout.addWidget(file_text, 0, 1)
    self.file_text = file_text

    # Create search button
    input_file = QPushButton("开始抓取")
    grid_layout.addWidget(input_file, 0, 2)
    self.input_file = input_file

    # Create filename labels
    grid_layout.addWidget(QLabel("文件名:"), 1, 0)
    file_name_label = QLabel("file_name")
    grid_layout.addWidget(file_name_label, 1, 1)
    self.file_name_label = file_name_label

    show_page_label = QLabel("0/0")
    grid_layout.addWidget(show_page_label, 1, 2)
    self.show_page_label = show_page_label

    # Create image search
    grid_layout.addWidget(QLabel("图片搜索:"), 2, 0)
    image_page = QLineEdit()
    grid_layout.addWidget(image_page, 2, 1)
    self.image_page = image_page

    jump_point_image = QPushButton("跳转搜索")
    grid_layout.addWidget(jump_point_image, 2, 2)
    self.jump_point_image = jump_point_image

    # Create spider status layout
    h_layout_spider = QHBoxLayout()
    h_layout_spider.addStretch()

    spider_labels = [
        ('spider_mode_label', '抓取模式: '),
        ('spider_mode_show_label', '自动模式 '),
        ('spider_progress_label', '抓取进度: '),
        ('spider_progress_show_label', '0/0 ')
    ]

    for name, text in spider_labels:
        label = QLabel(text, self)
        h_layout_spider.addWidget(label)
        setattr(self, name, label)

    grid_layout.addLayout(h_layout_spider, 3, 1, 1, 3)

    # Create download status layout
    h_layout_download = QHBoxLayout()
    h_layout_download.addStretch()

    download_labels = [
        ('download_img_label', '下载进度: '),
        ('download_show_label', '0/0 ')
    ]

    for name, text in download_labels:
        label = QLabel(text, self)
        h_layout_download.addWidget(label)
        setattr(self, name, label)

    grid_layout.addLayout(h_layout_download, 4, 1, 1, 3)

    # Create bottom button layout
    h_layout = QHBoxLayout()
    h_layout.addStretch()

    sys_status_label = QLabel('等待操作中... ', self)
    h_layout.addWidget(sys_status_label)
    self.sys_status_label = sys_status_label

    buttons = [
        ('btn_show_log', '显示日志输出'),
        ('btn_open_data', '打开数据目录'),
        ('btn_zoom_in', '放大'),
        ('btn_zoom_out', '缩小')
    ]

    for name, text in buttons:
        button = QPushButton(text, self)
        h_layout.addWidget(button)
        setattr(self, name, button)

    grid_layout.addLayout(h_layout, 5, 1, 1, 3)


@logger.catch
def search_item_paint_tab2(self):
    """Paint search items UI for tab 2"""
    grid_layout_video = QGridLayout()
    self.setLayout(grid_layout_video)
    self.grid_layout_video = grid_layout_video


@logger.catch
def tab_3_ui_paint(self):
    """Paint UI for tab 3"""
    # Create file input section
    edt_input_file_text_3 = QLineEdit(str(Path(__file__).parent))
    btn_input_file_3 = QPushButton("选择文件夹")
    
    h_box_3 = QHBoxLayout()
    h_box_3.addWidget(QLabel("数据路径:"))
    h_box_3.addWidget(edt_input_file_text_3)
    h_box_3.addWidget(btn_input_file_3)

    self.edt_input_file_text_3 = edt_input_file_text_3
    self.btn_input_file_3 = btn_input_file_3

    # Create scroll area
    label_3 = QLabel(self)
    scroll_area_3 = QScrollArea()
    scroll_area_3.setWidget(label_3)
    scroll_area_3.setParent(self.tab3)
    
    h_box_2_3 = QHBoxLayout()
    h_box_2_3.addWidget(scroll_area_3)

    self.label_3 = label_3

    # Create button row
    buttons = [
        ('un_normal_img_button', '剔除异常图片'),
        ('img_category_button', '分类图片'),
        ('download_gif_zip', '下载压缩包'),
        ('unzip_generate_video', '解压生成视频'),
        ('download_video_zip', '下载内容')
    ]

    h_box_3_3 = QHBoxLayout()
    
    for name, text in buttons:
        button = QPushButton(text)
        h_box_3_3.addWidget(button)
        setattr(self, name, button)

    # Layout everything vertically
    vbox_3 = QVBoxLayout()
    vbox_3.addLayout(h_box_3)
    vbox_3.addLayout(h_box_2_3)
    vbox_3.addLayout(h_box_3_3)

    self.tab3.setLayout(vbox_3)
    self.setCentralWidget(self.tab_widget)

    # Connect signals
    self.btn_input_file_3.clicked.connect(self.input_keyword_process_3)
    self.un_normal_img_button.clicked.connect(self.remove_error_image_click)
    self.img_category_button.clicked.connect(self.img_category_button_click)
    self.download_gif_zip.clicked.connect(self.download_gif_zip_click)
    self.unzip_generate_video.clicked.connect(self.unzip_generate_video_click)
    self.download_video_zip.clicked.connect(self.download_video_zip_click)

    return True
