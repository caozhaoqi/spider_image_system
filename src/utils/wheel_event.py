import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QDesktopWidget
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # v_layout_main = QVBoxLayout(self)
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout(self)

        self.setWindowTitle('Image Viewer')
        self.label = QLabel(self)
        self.pixmap = QPixmap(r"C:\Users\Administrator\PycharmProjects\spider_image_system\src\gui\data\img_url"
                              r"\yaoyao_img_result\images\114325054_p0_master1200.jpg")  # 替换为你的图片路径
        self.label.setPixmap(self.pixmap)
        # self.label.setScaledContents(True)  # 这会使QLabel根据内容自动调整大小
        screen = QDesktopWidget().screenGeometry()
        # # 设置窗口大小为屏幕大小
        self.label.resize(screen.width(), screen.height())
        self.label.setLayout(v_layout)

        self.label.move(50, 50)  # 设置标签的位置
        self.btn_zoom_in = QPushButton('放大', self)
        self.btn_zoom_out = QPushButton('缩小', self)

        h_layout.addWidget(self.btn_zoom_out)
        h_layout.addWidget(self.btn_zoom_in)
        v_layout.addLayout(h_layout)
        v_layout.addStretch()
        # v_layout.addStretch()
        v_layout.addWidget(self.label)
        # v_layout_main.addLayout(v_layout)
        # self.setLayout(v_layout_main)

        # self.isCtrlDown = False
        self.isDragging = False
        self.dragStartPos = None
        self.lastMousePos = None
        self.scaleFactor = 1.0
        self.label.installEventFilter(self)
        # 连接按钮的点击事件到相应的槽函数
        self.btn_zoom_in.clicked.connect(self.zoomIn)
        self.btn_zoom_out.clicked.connect(self.zoomOut)
        self.showMaximized()  # 最大化窗口

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.isDragging = True
                self.dragStartPos = event.pos() - self.label.pos()  # 记录鼠标和标签的相对位置
                self.lastMousePos = event.pos()  # 记录上一次鼠标的位置
        elif event.type() == QEvent.MouseMove and self.isDragging:
            dx = event.pos().x() - self.lastMousePos.x()  # 计算鼠标的移动距离
            dy = event.pos().y() - self.lastMousePos.y()  # 计算鼠标的移动距离
            newPos = self.label.pos() + QPoint(dx, dy)  # 更新标签的位置
            self.label.move(newPos)  # 移动标签到新位置
            self.lastMousePos = event.pos()  # 更新上一次鼠标的位置
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.isDragging = False
        return super().eventFilter(obj, event)

    def zoomIn(self):
        new_size = self.pixmap.size() * 1.1  # 放大10%
        self.pixmap = self.pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)

    def zoomOut(self):
        new_size = self.pixmap.size() * 0.9  # 缩小90%
        self.pixmap = self.pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
