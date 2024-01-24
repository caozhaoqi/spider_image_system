import os
import sys
from functools import partial

import cv2
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QTabWidget, QWidget, QLineEdit, QPushButton, QHBoxLayout, \
    QLabel, QVBoxLayout, QScrollArea
from PyQt5.uic.properties import QtGui
from loguru import logger

from gui.video_ui import VideoPlayer
from utils.base_event import about_message_lookup, visit_web, \
    edit_config_msg


@logger.catch
def base_menu(self):
    """
    基础菜单
    :return:
    """
    # 创建菜单栏
    self.menu_bar = QMenuBar()
    self.file_menu = QMenu('文件', self.menu_bar)
    self.new_action = QAction('新建', self.file_menu)
    self.edit_action = QAction('编辑', self.file_menu)
    self.save_action = QAction('保存', self.file_menu)
    self.file_menu.addAction(self.new_action)
    self.file_menu.addAction(self.edit_action)
    self.file_menu.addAction(self.save_action)

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

    self.menu_bar.addMenu(self.file_menu)
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
    self.tab_widget.addTab(self.tab1, 'pixiv')
    self.tab_widget.addTab(self.tab2, 'net')
    self.tab_widget.addTab(self.tab3, '其他')
    # 创建表格和设置列名
    return self.tab1, self.tab2, self.tab3, self.tab_widget


@logger.catch
def tab_1_ui_paint(self):
    """

    :param self:
    :return:
    """
    self.file_text = QLineEdit(
        os.path.join(os.path.dirname(__file__), ""))
    self.input_file = QPushButton(u"开始抓取")
    self.h_box = QHBoxLayout()
    self.h_box.addWidget(QLabel(u"关键字:"))
    self.h_box.addWidget(self.file_text)
    self.h_box.addWidget(self.input_file)

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
    self.vbox.addLayout(self.h_box)
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
    # self.layout = QVBoxLayout()
    # self.setLayout(self.layout)

    # self.tabWidget = QTabWidget(self)
    # self.tabWidget.setTabPosition(QTabWidget.West)
    # self.tab = QWidget()
    # self.tabWidget.addTab(self.tab2, 'Video')
    # self.layout.addWidget(self.tabWidget)

    # self.video_player = cv2.VideoCapture('./data/video/1703471146086.mp4')  # 替换为您的视频文件路径
    # if not self.video_player.isOpened():
    #     print("无法打开视频文件")
    #     sys.exit()
    #
    # self.display_frame = cv2.cvtColor(cv2.flip(cv2.VideoCapture(self.video_player).read()[1], 0), cv2.COLOR_BGR2RGB)
    # self.display_image = QLabel(self.tab2)
    # self.display_image.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(self.display_frame, 'RGB')))
    # self.layout.addWidget(self.display_image)
    # self.tab_video = TabWithVideo()
    # 创建布局并将表格添加到布局中
    # self.tab2.setLayout(self.tab_video.layout)
    # self.setCentralWidget(self.tab_widget)
    pass


class TabWithVideo(QWidget):
    def __init__(self):
        super().__init__()
        self.download_video_button = None
        self.layout = None
        self.videoPlayer = None
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.videoPlayer = VideoPlayer()  # 创建 VideoPlayer 实例
        self.download_video_button = QPushButton(u"开始下载")
        self.layout.addWidget(self.videoPlayer)  # 将 VideoPlayer 添加到布局中
        self.layout.addWidget(self.download_video_button)
        self.download_video_button.clicked.connect(self.player_video)

        # self.tab2.setLayout(layout)
    def player_video(self):
        self.videoPlayer.playVideo("")
        logger.debug("video playing.")
