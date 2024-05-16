import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from loguru import logger
from run import constants
from utils.sys_info import look_sys_info, network_usage
from PyQt5 import QtWidgets, QtChart


@logger.catch
def get_system_info():
    """

    :return:
    """
    memory_usage, cpu_usage = look_sys_info()
    send_bytes, receiver_bytes = network_usage()
    return memory_usage, cpu_usage, send_bytes, receiver_bytes


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
        self.init_ui()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

    @logger.catch
    def init_ui(self, _=None):
        """

        :return:
        """
        self.setWindowTitle('System Monitor')
        self.resize(800, 600)

        self.chart = QtChart.QChart()
        self.chart.setTitle("System Resource Usage")
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

        self.memory_series = QtChart.QLineSeries()
        self.cpu_series = QtChart.QLineSeries()
        self.send_bytes_series = QtChart.QLineSeries()
        self.receive_bytes_series = QtChart.QLineSeries()
        self.chart.addSeries(self.memory_series)
        self.chart.addSeries(self.cpu_series)
        self.chart.addSeries(self.send_bytes_series)
        self.chart.addSeries(self.receive_bytes_series)

        self.axisX = QtChart.QValueAxis()
        self.axisY = QtChart.QValueAxis()

        self.chart.setAxisX(self.axisX, self.memory_series)
        self.chart.setAxisX(self.axisX, self.cpu_series)
        self.chart.setAxisY(self.axisY, self.memory_series)
        self.chart.setAxisY(self.axisY, self.cpu_series)
        self.chart.setAxisX(self.axisX, self.send_bytes_series)
        self.chart.setAxisX(self.axisX, self.receive_bytes_series)
        self.chart.setAxisY(self.axisY, self.send_bytes_series)
        self.chart.setAxisY(self.axisY, self.receive_bytes_series)

        self.axisY.setLabelFormat("%d")
        self.axisX.setTitleText("Time (s)")
        self.axisY.setTitleText("Value")

    @logger.catch
    def update_data(self, _=None):
        """

        :return:
        """
        if constants.performance_monitor_visible:
            mem_usage, cpu_usage = look_sys_info()
            send_bytes, receive_bytes = network_usage()
            current_time = time.time()

            start_time = current_time - constants.fire_wall_delay_time
            end_time = current_time

            self.axisX.setRange(start_time, end_time)

            minValue = min(mem_usage, cpu_usage, send_bytes, receive_bytes)
            maxValue = max(mem_usage, cpu_usage, send_bytes, receive_bytes)

            self.axisY.setRange(minValue, maxValue + maxValue / 2)

            min_memory_usage = minValue
            max_memory_usage = maxValue

            current_memory_usage = mem_usage

            if current_memory_usage > max_memory_usage:
                max_memory_usage = current_memory_usage
                self.chart.setAxisRange(QtChart.QValueAxis.YAxis, min_memory_usage, max_memory_usage)
            elif current_memory_usage < min_memory_usage:
                min_memory_usage = current_memory_usage
                self.chart.setAxisRange(QtChart.QValueAxis.YAxis, min_memory_usage, max_memory_usage)

            self.memory_series.append(current_time, current_memory_usage)
            self.memory_series.setName("Memory Usage")

            self.cpu_series.append(current_time, cpu_usage)
            self.cpu_series.setName("CPU Usage")

            self.send_bytes_series.append(current_time, send_bytes)
            self.send_bytes_series.setName("Sent Bytes")

            self.receive_bytes_series.append(current_time, receive_bytes)
            self.receive_bytes_series.setName("Received Bytes")

            self.chart.legend().setVisible(True)

            self.chart_view.update()

    @logger.catch
    def closeEvent(self, event, _=None):
        """
        对话框关闭
        :param event:
        :return:
        """
        logger.debug('AutoImageDialog Dialog is closing!')
        self.timer.stop()
        constants.performance_monitor_visible = False
        super(SystemMonitor, self).closeEvent(event)
