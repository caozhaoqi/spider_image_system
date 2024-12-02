"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import time
from PyQt5 import QtGui, QtCore, QtWidgets, QtChart
from PyQt5.QtWidgets import QDialog
from loguru import logger

from run import constants
from utils.sys_info import look_sys_info, network_usage


@logger.catch
def get_system_info():
    """Get current system resource usage information"""
    memory_usage, cpu_usage = look_sys_info()
    send_bytes, receiver_bytes = network_usage()
    return memory_usage, cpu_usage, send_bytes, receiver_bytes


class SystemMonitor(QDialog):
    """System resource usage monitoring dialog"""

    def __init__(self):
        super().__init__()
        self.axisX = None
        self.axisY = None
        self.receive_bytes_series = None
        self.send_bytes_series = None
        self.cpu_series = None
        self.memory_series = None
        self.chart_view = None
        self.chart = None

        constants.UIConfig.performance_monitor_visible = True

        self.init_ui()

        # Setup update timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)

    @logger.catch
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle('System Monitor')
        self.resize(800, 600)

        # Create chart
        self.chart = QtChart.QChart()
        self.chart.setTitle("System Resource Usage")
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        # Setup layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

        # Create data series
        self.memory_series = QtChart.QLineSeries()
        self.cpu_series = QtChart.QLineSeries()
        self.send_bytes_series = QtChart.QLineSeries()
        self.receive_bytes_series = QtChart.QLineSeries()

        # Add series to chart
        series_list = [self.memory_series, self.cpu_series,
                       self.send_bytes_series, self.receive_bytes_series]
        for series in series_list:
            self.chart.addSeries(series)

        # Setup axes
        self.axisX = QtChart.QValueAxis()
        self.axisY = QtChart.QValueAxis()

        # Attach axes to series
        for series in series_list:
            self.chart.setAxisX(self.axisX, series)
            self.chart.setAxisY(self.axisY, series)

        self.axisY.setLabelFormat("%d")
        self.axisX.setTitleText("Time (s)")
        self.axisY.setTitleText("Value")

    @logger.catch
    def update_data(self):
        """Update chart data with current system metrics"""
        if not constants.UIConfig.performance_monitor_visible:
            return

        # Get current metrics
        mem_usage, cpu_usage = look_sys_info()
        send_bytes, receive_bytes = network_usage()
        current_time = time.time()

        # Update time range
        start_time = current_time - constants.fire_wall_delay_time
        self.axisX.setRange(start_time, current_time)

        # Update value range
        metrics = [mem_usage, cpu_usage, send_bytes, receive_bytes]
        min_value = min(metrics)
        max_value = max(metrics)
        self.axisY.setRange(min_value, max_value * 1.5)

        # Update series data
        self.memory_series.append(current_time, mem_usage)
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
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('System monitor dialog closing')
        self.timer.stop()
        constants.UIConfig.performance_monitor_visible = False
        super().closeEvent(event)
