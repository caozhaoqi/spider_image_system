import time

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from loguru import logger
from utils.sys_info import look_sys_info, network_usage


@logger.catch
def get_system_info():
    """

    :return:
    """
    memory_usage, cpu_usage = look_sys_info()
    send_bytes, receiver_bytes = network_usage()  # 示例数据
    return memory_usage, cpu_usage, send_bytes, receiver_bytes


import sys
from PyQt5 import QtWidgets, QtChart


class SystemMonitor(QDialog):
    def __init__(self):
        """

        """

        super().__init__()
        self.axisX = None
        self.axisY = None
        self.receive_bytes_series = None
        self.send_bytes_series = None
        self.cpu_series = None
        self.memory_series = None
        self.chart_view = None
        self.chart = None
        self.initUI()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # 每秒更新一次数据

    def initUI(self):
        """

        :return:
        """
        self.setWindowTitle('System Monitor')
        self.setGeometry(300, 300, 800, 600)
        self.chart = QtChart.QChart()
        self.chart.setTitle("System Resource Usage")
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

        # 初始化数据系列和坐标轴
        self.memory_series = QtChart.QLineSeries()
        self.cpu_series = QtChart.QLineSeries()
        self.send_bytes_series = QtChart.QLineSeries()
        self.receive_bytes_series = QtChart.QLineSeries()
        self.chart.addSeries(self.memory_series)
        self.chart.addSeries(self.cpu_series)
        self.chart.addSeries(self.send_bytes_series)
        self.chart.addSeries(self.receive_bytes_series)

        # # 创建坐标轴对象
        self.axisX = QtChart.QValueAxis()
        self.axisY = QtChart.QValueAxis()

        # 设置坐标轴范围
        # self.axisY.setRange(0, 100)  # 例如设置为0到100的范围

        # 将坐标轴应用到图表上
        self.chart.setAxisX(self.axisX, self.memory_series)
        self.chart.setAxisX(self.axisX, self.cpu_series)
        self.chart.setAxisY(self.axisY, self.memory_series)
        self.chart.setAxisY(self.axisY, self.cpu_series)
        self.chart.setAxisX(self.axisX, self.send_bytes_series)
        self.chart.setAxisX(self.axisX, self.receive_bytes_series)
        self.chart.setAxisY(self.axisY, self.send_bytes_series)
        self.chart.setAxisY(self.axisY, self.receive_bytes_series)

        # 设置坐标轴的其他属性，例如标签、格式等
        self.axisX.setLabelFormat("%.2f")  # 设置X轴标签格式为小数点后两位
        self.axisY.setLabelFormat("%d")  # 设置Y轴标签格式为整数
        self.axisX.setTitleText("Time (s)")  # 设置X轴标题
        self.axisY.setTitleText("Value")  # 设置Y轴标题

    def update_data(self):
        """

        :return:
        """
        mem_usage, cpu_usage = look_sys_info()  # 假设这个函数返回内存和CPU使用情况
        send_bytes, receive_bytes = network_usage()  # 示例数据，实际应为网络使用情况函数调用
        current_time = time.time()  # 获取当前时间戳
        # 计算前10秒和后10秒的时间戳
        start_time = current_time - 30  # 当前时间前10秒
        end_time = current_time  # 当前时间后10秒
        # 设置时间窗口
        self.axisX.setRange(start_time, end_time)

        # 如果需要，根据数据动态调整坐标轴范围
        minValue = min(mem_usage, cpu_usage, send_bytes, receive_bytes)
        maxValue = max(mem_usage, cpu_usage, send_bytes, receive_bytes)
        # 例如，如果内存使用量增长过快，可能需要扩大Y轴范围
        # self.axis_y = QtChart.QValueAxis()
        self.axisY.setRange(minValue, maxValue)

        min_memory_usage = minValue  # 初始最小内存使用量
        max_memory_usage = maxValue  # 初始最大内存使用量

        # 在每次更新数据之前，检查当前内存使用量与上一次的值
        current_memory_usage = mem_usage

        if current_memory_usage > max_memory_usage:
            # 如果当前内存使用量超过了当前的最大值，更新最大值并相应调整Y轴范围
            max_memory_usage = current_memory_usage
            self.chart.setAxisRange(QtChart.QValueAxis.YAxis, min_memory_usage, max_memory_usage)
        elif current_memory_usage < min_memory_usage:
            # 如果当前内存使用量低于了当前的最小值，更新最小值并相应调整Y轴范围
            min_memory_usage = current_memory_usage
            self.chart.setAxisRange(QtChart.QValueAxis.YAxis, min_memory_usage, max_memory_usage)

        # 更新内存使用数据系列
        self.memory_series.append(current_time, current_memory_usage)

        # 更新CPU使用数据系列
        self.cpu_series.append(current_time, cpu_usage)

        # 更新发送字节数据系列
        self.send_bytes_series.append(current_time, send_bytes)

        # 更新接收字节数据系列
        self.receive_bytes_series.append(current_time, receive_bytes)

        # 确保图表视图重绘或刷新以显示更新后的数据
        self.chart_view.update()


@logger.catch
def show_sys_info_ui():
    """
    show sys info ui
    :return:
    """
    # app = QtWidgets.QApplication(sys.argv)
    monitor = SystemMonitor()
    monitor.show()
    monitor.showMaximized()
    monitor.exec_()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    show_sys_info_ui()
