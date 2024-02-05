import pyqtgraph
from loguru import logger
from numpy.distutils.fcompiler import pg

from utils.sys_info import look_sys_info, network_usage
from pyqtgraph import PlotWidget, plot

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import numpy as np


# 定时获取系统信息的函数
@logger.catch
def get_system_info():
    """

    :return:
    """
    memory_usage, cpu_usage = look_sys_info()
    send_bytes, receiver_bytes = network_usage()  # 示例数据
    return memory_usage, cpu_usage, send_bytes, receiver_bytes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = {
            'memory': [],
            'cpu': [],
            'send_bytes': [],
            'receiver_bytes': []
        }
        self.update_data()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 1秒更新一次数据

    def initUI(self):
        self.setWindowTitle('System Monitoring')
        self.setGeometry(300, 300, 800, 600)
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.plotWidgets = []  # 用于存储四个子图的PlotWidget对象
        for i in range(4):  # 创建四个子图
            plotWidget = PlotWidget()  # 创建一个PlotWidget对象作为子图容器
            layout.addWidget(plotWidget)  # 将PlotWidget添加到布局中
            self.plotWidgets.append(plotWidget)  # 将PlotWidget对象存储到列表中以便后续使用
            curve = plotWidget.plot(np.array([]), np.array([]), pen=pyqtgraph.mkPen('r', width=2))  # 初始化曲线对象，用于绘制数据点
            curve.setYRange(0, 100)  # 设置初始的y轴范围，可以根据实际情况调整
            axis = plotWidget.getAxis('bottom')  # 获取x轴对象，用于设置刻度范围和标签等属性
            axis.setLabel('Time')  # 设置x轴标签为'Time'
            axis.setRange(0, 10)  # 设置x轴范围为0到10，可以根据实际情况调整
            axis = plotWidget.getAxis('left')  # 获取y轴对象，用于设置刻度范围和标签等属性
            axis.setLabel('Usage')  # 设置y轴标签为'Usage'
            axis.setRange(0, 100)  # 设置y轴范围为0到100，可以根据实际情况调整
        self.show()  # 显示主窗口

    def update_data(self):
        memory_usage, cpu_usage, send_bytes, receiver_bytes = get_system_info()  # 获取系统信息
        for i, plotWidget in enumerate(self.plotWidgets):  # 更新四个子图的数据点并调整坐标轴刻度范围
            if i == 0:  # 子图1: Memory Usage
                plotWidget.plot(np.arange(len(memory_usage)), memory_usage, pen=pyqtgraph.mkPen('g', width=2))  # 更新数据点并绘制新的曲线
                axis = plotWidget.getAxis('left')  # 获取y轴对象，用于设置刻度范围和标签等属性
                axis.setRange(min(memory_usage), max(memory_usage))  # 根据数据调整y轴范围和刻度
            elif i == 1:  # 子图2: CPU Usage
                plotWidget.plot(np.arange(len(cpu_usage)), cpu_usage, pen=pyqtgraph.mkPen('b', width=2))  # 更新数据点并绘制新的曲线
                axis = plotWidget.getAxis('left')  # 获取y轴对象，用于设置刻度范围和标签等属性
                axis.setRange(min(cpu_usage), max(cpu_usage))  # 根据数据调整y轴范围和刻度
            elif i == 2:  # 子图3: Network Send Bytes
                plotWidget.plot(np.arange(len(send_bytes)), send_bytes, pen=pyqtgraph.mkPen('c', width=2))  # 更新数据点并绘制新的曲线
                axis = plotWidget.getAxis('left')  # 获取y轴对象，用于设置刻度范围
                axis.setRange(min(send_bytes), max(send_bytes))  # 根据数据调整y轴范围和刻度
            else:  # 子图4: Network Receive Bytes
                plotWidget.plot(np.arange(len(receiver_bytes)), receiver_bytes,
                                pen=pyqtgraph.mkPen('m', width=2))  # 更新数据点并绘制新的曲线
                axis = plotWidget.getAxis('left')  # 获取y轴对象，用于设置刻度范围和标签等属性
                axis.setRange(min(receiver_bytes), max(receiver_bytes))  # 根据数据调整y轴范围和刻度


@logger.catch
def show_sys_info():
    """
    显示系统信息。
    """
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show_sys_info()
