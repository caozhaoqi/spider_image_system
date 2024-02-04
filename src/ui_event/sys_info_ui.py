import sys
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from utils.sys_info import get_memory_usage, get_cpu_usage, ensure_list_of_floats


class ResourceMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.memory_line = None
        self.cpu_line = None
        self.plot_canvas = None
        self.layout = None
        self.init_ui()
        self.cpu_data = []
        self.memory_data = []
        self.update_data()
        plt.rcParams['font.family'] = 'Microsoft YaHei'
        self.timer = self.startTimer(1000)  # 每秒更新一次数据

    def init_ui(self):
        self.setWindowTitle('系统资源占用')
        self.setGeometry(300, 300, 800, 600)
        self.layout = QVBoxLayout()
        self.plot_canvas = FigureCanvas(plt.Figure())
        self.plot_canvas.figure.add_subplot(111)
        self.plot_canvas.figure.add_axes([0.1, 0.1, 0.8, 0.8])  # 在左下角的位置，占据大部分的绘图区域
        self.plot_canvas.figure.add_axes([0.5, 0.5, 0.3, 0.3])  # 在右上角的位置，占据较小的绘图区域
        self.layout.addWidget(self.plot_canvas)
        self.setLayout(self.layout)

    def update_data(self):
        cpu_percent = get_cpu_usage()
        memory_percent = get_memory_usage()
        self.plot_cpu(cpu_percent)
        self.plot_memory(memory_percent)

    def plot_cpu(self, cpu_percent):
        # 确保 self.cpu_data 和 cpu_percent 是数字列表
        # self.cpu_data = ensure_list_of_floats(self.cpu_data)
        # cpu_percent = ensure_list_of_floats(cpu_percent)
        self.cpu_data = cpu_percent
        # 检查两个列表的长度是否相同
        # if len(self.cpu_data) != len(cpu_percent):
        #     raise ValueError("The length of cpu_data and cpu_percent must be the same.")

        x = range(len(self.cpu_data)) if self.cpu_data else [i + 1 for i in range(len(cpu_percent))]
        y = self.cpu_data if self.cpu_data else cpu_percent
        self.cpu_line, = self.plot_canvas.figure.axes[0].plot(x, y, 'r-')  # 重新绘制CPU折线图
        self.plot_canvas.figure.axes[0].legend([self.cpu_line], ['CPU占用率'])  # 添加图例
        self.plot_canvas.draw()  # 重新绘制图形

    def plot_memory(self, memory_percent):
        # 确保 self.cpu_data 和 cpu_percent 是数字列表
        # self.memory_data = ensure_list_of_floats(self.memory_data)
        # memory_percent = ensure_list_of_floats(memory_percent)
        self.memory_data = memory_percent
        #
        # 检查两个列表的长度是否相同
        # if len(self.memory_data) != len(memory_percent):
        #     raise ValueError("The length of cpu_data and cpu_percent must be the same.")

        x = range(len(self.memory_data)) if self.memory_data else [i + 1 for i in range(len(memory_percent))]
        y = self.memory_data if self.memory_data else memory_percent
        self.memory_line, = self.plot_canvas.figure.axes[1].plot(x, y, 'b-')  # 重新绘制内存折线图
        self.plot_canvas.figure.axes[1].legend([self.memory_line], ['内存占用率'])  # 添加图例
        self.plot_canvas.draw()  # 重新绘制图形

    def timerEvent(self, e):
        self.update_data()  # 更新数据并重新绘制图形


if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = ResourceMonitor()
    monitor.show()
    sys.exit(app.exec_())
