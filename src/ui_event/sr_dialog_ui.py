import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout


class SRCharacterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('角色信息')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.addRow("角色目标等级", QLineEdit())
        form_layout.addRow("目标天赋", QLineEdit())
        form_layout.addRow("武器目标等级", QLineEdit())
        form_layout.addRow("武器星级", QLineEdit())
        form_layout.addRow("角色星级", QLineEdit())
        form_layout.addRow("圣遗物等级", QLineEdit())

        layout.addLayout(form_layout)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SRCharacterDialog()
    dialog.show()
    sys.exit(app.exec_())
