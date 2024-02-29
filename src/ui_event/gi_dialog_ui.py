import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton, QHBoxLayout
from loguru import logger

from run import constants
from utils.genshin_impact_cal import get_result_str


class GICharacterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.shenyuan_num = None
        self.big_month_card_ys = None
        self.other_ys = None
        self.day_ys = None
        self.small_month_card_ys = None
        self.relic_level_line_edit_flower = None
        self.relic_level_line_edit_sl = None
        self.relic_level_line_edit_bz = None
        self.relic_level_line_edit_t = None
        self.relic_level_line_edit_ym = None

        self.character_star_line_edit = None
        self.weapon_star_line_edit = None
        self.weapon_level_line_edit = None
        self.talent_line_edit_A = None
        self.talent_line_edit_E = None
        self.talent_line_edit_Q = None

        self.level_line_edit = None
        self.result_label = None
        self.calculate_button = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('genshin impact view tools')

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.level_line_edit = QLineEdit()
        self.talent_line_edit_A = QLineEdit()
        self.talent_line_edit_E = QLineEdit()
        self.talent_line_edit_Q = QLineEdit()

        self.weapon_level_line_edit = QLineEdit()
        self.weapon_star_line_edit = QLineEdit()
        self.character_star_line_edit = QLineEdit()
        self.relic_level_line_edit_ym = QLineEdit()
        self.relic_level_line_edit_flower = QLineEdit()
        self.relic_level_line_edit_sl = QLineEdit()
        self.relic_level_line_edit_bz = QLineEdit()
        self.relic_level_line_edit_t = QLineEdit()
        # yue ka day
        self.small_month_card_ys = QLineEdit()
        # mei ri wei tuo day
        self.day_ys = QLineEdit()
        #  da yue ka day
        self.big_month_card_ys = QLineEdit()
        # other
        self.other_ys = QLineEdit()
        self.shenyuan_num = QLineEdit()

        form_layout.addRow("角色星级", self.character_star_line_edit)
        form_layout.addRow("角色目标等级", self.level_line_edit)

        form_layout.addRow("目标天赋-A", self.talent_line_edit_A)
        form_layout.addRow("目标天赋-E", self.talent_line_edit_E)
        form_layout.addRow("目标天赋-Q", self.talent_line_edit_Q)

        form_layout.addRow("武器星级", self.weapon_star_line_edit)
        form_layout.addRow("武器目标等级", self.weapon_level_line_edit)

        form_layout.addRow("圣遗物-花等级", self.relic_level_line_edit_flower)
        form_layout.addRow("圣遗物-羽毛等级", self.relic_level_line_edit_ym)
        form_layout.addRow("圣遗物-沙漏等级", self.relic_level_line_edit_sl)
        form_layout.addRow("圣遗物-杯子等级", self.relic_level_line_edit_bz)
        form_layout.addRow("圣遗物-头等级", self.relic_level_line_edit_t)

        form_layout.addRow("小月卡天数", self.small_month_card_ys)
        form_layout.addRow("大月卡天数", self.big_month_card_ys)
        form_layout.addRow("委托天数", self.day_ys)
        form_layout.addRow("深渊期数", self.shenyuan_num)
        form_layout.addRow("other", self.other_ys)

        self.calculate_button = QPushButton("计算")
        self.result_label = QLabel("结果将在这里显示")

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.calculate_button)
        # h_layout.addWidget(self.result_label)

        layout.addLayout(form_layout)
        layout.addLayout(h_layout)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.calculate_button.clicked.connect(self.calculate)

    def calculate(self):
        level = self.level_line_edit.text()
        talent_A = self.talent_line_edit_A.text()
        talent_E = self.talent_line_edit_A.text()
        talent_Q = self.talent_line_edit_A.text()

        weapon_level = self.weapon_level_line_edit.text()
        weapon_star = self.weapon_star_line_edit.text()
        character_star = self.character_star_line_edit.text()
        relic_level_flower = self.relic_level_line_edit_flower.text()
        relic_level_t = self.relic_level_line_edit_t.text()
        relic_level_bz = self.relic_level_line_edit_bz.text()
        relic_level_sl = self.relic_level_line_edit_sl.text()
        # 270475 3780000
        relic_level_ym = self.relic_level_line_edit_ym.text()

        big_day_month_card = self.big_month_card_ys.text()
        small_day_month_card = self.small_month_card_ys.text()
        shenyuan_num = self.shenyuan_num.text()
        if self.shenyuan_num != '' and big_day_month_card != '':
            other_ys_ = int(self.other_ys.text()) + int(big_day_month_card) + int(shenyuan_num) * 600 + 5 * 160
        else:
            other_ys_ = self.other_ys.text()
        if talent_A == '' or talent_E == '' or talent_Q == '' or small_day_month_card == '' or level == '' or weapon_level \
                == '' or relic_level_flower == '' or relic_level_bz == '' or relic_level_ym == '' or relic_level_t == '' or \
                relic_level_sl == '':
            self.result_label.setText('input msg null!')
            return False
        result = get_result_str(talent_Q, talent_E, talent_A, small_day_month_card, other_ys_, level, weapon_star,
                                weapon_level, relic_level_flower, relic_level_bz, relic_level_sl, relic_level_t,
                                relic_level_ym)
        self.result_label.setText(result)

    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('GICharacterDialog Dialog is closing!')
        constants.genshin_impact_view_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(GICharacterDialog, self).closeEvent(event)

