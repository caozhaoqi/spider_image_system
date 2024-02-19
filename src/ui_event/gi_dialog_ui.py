import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton, QHBoxLayout
from loguru import logger

from utils.genshin_impact_cal import cal_role_book, cal_ys_total, cal_weapons_materials, cal_role_talent, get_result_str


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
        self.initUI()

    def initUI(self):
        self.setWindowTitle('genshin impact view tools')
        self.setFixedSize(800, 800)

        # 创建垂直布局
        layout = QVBoxLayout()

        # 创建表单布局
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

        form_layout.addRow("目标天赋A", self.talent_line_edit_A)
        form_layout.addRow("目标天赋E", self.talent_line_edit_E)
        form_layout.addRow("目标天赋Q", self.talent_line_edit_Q)

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

        # 创建计算按钮和结果显示
        self.calculate_button = QPushButton("计算")
        self.result_label = QLabel("结果将在这里显示")

        # 创建水平布局用于放置计算按钮和结果显示
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.calculate_button)
        # h_layout.addWidget(self.result_label)

        # 将表单布局和水平布局添加到垂直布局中
        layout.addLayout(form_layout)
        layout.addLayout(h_layout)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        # 连接计算按钮的点击事件到计算槽函数
        self.calculate_button.clicked.connect(self.calculate)

    def calculate(self):
        # 获取输入框的内容
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

        relic_count_result = relic_level_flower * 270475 / 20 + relic_level_t * 270475 / 20 + relic_level_ym * 270475 \
                             / 20 + relic_level_sl * 270475 / 20 + relic_level_bz * 270475 / 20
        big_day_month_card = self.big_month_card_ys.text()
        small_day_month_card = self.small_month_card_ys.text()
        shenyuan_num = self.shenyuan_num.text()
        if self.shenyuan_num != '':
            other_ys_ = self.other_ys.text() + big_day_month_card + shenyuan_num * 600 + 5 * 160
        else:
            other_ys_ = self.other_ys.text()
        result = get_result_str(talent_Q, talent_E, talent_A, small_day_month_card, other_ys_, level, weapon_star,
                                weapon_level)
        result = result + relic_count_result
        self.result_label.setText(result)


@logger.catch
def show_image_auto_viewer():
    """
    show image to tool
    :return:
    """
    dialog_gi = GICharacterDialog()
    dialog_gi.showMaximized()
    dialog_gi.show()
    dialog_gi.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = GICharacterDialog()
    dialog.show()
    # dialog.showMaximized()
    sys.exit(app.exec_())
