import os
from functools import partial

from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QTabWidget, QWidget, QLineEdit, QPushButton, QHBoxLayout, \
    QLabel, QVBoxLayout, QScrollArea
from loguru import logger

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

    self.download_img_button = QPushButton(u"开始下载")
    self.next_button = QPushButton(u"下一张")
    self.before_button = QPushButton(u"上一张")
    self.h_box_3 = QHBoxLayout()
    self.h_box_3.addWidget(self.before_button)
    self.h_box_3.addWidget(self.download_img_button)
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
    self.download_img_button.clicked.connect(self.download_file_thread)
    self.next_button.clicked.connect(self.next_img)
    self.before_button.clicked.connect(self.before_img)
    return True
