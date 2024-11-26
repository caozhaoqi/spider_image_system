import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtChart import (
    QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, 
    QValueAxis, QPieSeries
)
from PyQt5.QtGui import QPainter
from loguru import logger
from run import constants
from utils.img_analyis import img_analyze_data_output_new


class ImgAnalyzeHistogram(QDialog):
    """Dialog for displaying image analysis histograms and pie charts"""

    def __init__(self):
        super().__init__()
        self.pie_chart = None
        self.series_pie = None
        self.h_layout = None
        self.pie_chart_view = None
        self.chart_view = None
        self.layout = None
        self.error_counts = None
        self.window_title = None
        self.next_button = None
        self.chart = None
        self.max_value = None
        self.min_value = None
        self.axis_x = None
        self.axis_y = None
        self.group_size = 5
        self.series = None
        self.current_group = 0
        self.log_data = None
        self.log_item = None

        # 设置对话框模态
        self.setModal(True)
        self.init_ui("Image Category Analysis")

    @logger.catch
    def init_ui(self, window_title):
        """Initialize the UI components"""
        self.resize(800, 600)
        self.window_title = window_title
        self.error_counts, self.log_item = self.parse_img_data()

        self.setWindowTitle(self.window_title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create horizontal layout for charts
        self.h_layout = QHBoxLayout()
        
        # Create and setup bar chart
        self.chart = self.create_chart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Create pie chart
        self.pie_chart_view = self.create_pie_chart()

        # Create next button
        self.next_button = QPushButton('Next Group')
        self.next_button.clicked.connect(self.showNextGroup)

        # Add widgets to layouts
        self.h_layout.addWidget(self.chart_view, stretch=1)
        self.h_layout.addWidget(self.pie_chart_view, stretch=1)
        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.next_button)

    @logger.catch
    def parse_img_data(self):
        """Get image analysis data"""
        return img_analyze_data_output_new()

    @logger.catch
    def create_chart(self):
        """Create and configure bar chart"""
        chart = QChart()
        chart.setTitle("Bar Chart View")
        chart.legend().hide()
        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.series = QBarSeries()
        self.series.setLabelsVisible()

        self.axis_x = QBarCategoryAxis()
        self.axis_y = QValueAxis()

        return chart

    @logger.catch
    def create_pie_chart(self):
        """Create and configure pie chart"""
        self.series_pie = QPieSeries()
        self.pie_chart = QChart()
        chart_view = QChartView(self.pie_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    @logger.catch
    def showNextGroup(self):
        """Show next group of data"""
        try:
            self.current_group = (self.current_group + 1) % (len(self.error_counts) // self.group_size)
            self.updateChart()
        except Exception as e:
            logger.warning(f"Error showing next group: {e}")

    @logger.catch
    def showEvent(self, event):
        """重写显示事件"""
        super().showEvent(event)
        self.updateChart()  # 更新图表

    @logger.catch
    def show(self):
        """重写 show 方法，使用 exec_ 代替"""
        return self.exec_()

    @logger.catch
    def updateChart(self):
        """Update both charts with current data"""
        # Clear existing series
        for series in self.chart.series():
            self.chart.removeSeries(series)
        for series in self.pie_chart.series():
            self.pie_chart.removeSeries(series)
        self.series.clear()
        self.series_pie.clear()

        # Get current group data
        start_idx = self.current_group * self.group_size
        end_idx = start_idx + self.group_size
        update_data = list(zip(
            self.log_item[start_idx:end_idx],
            self.error_counts[start_idx:end_idx]
        ))

        # Update bar chart
        series = QBarSeries()
        
        # Process data for both charts
        for number, name in update_data:
            # Bar chart data
            bar_set = QBarSet(name)
            bar_set.append(float(number))
            series.append(bar_set)
            
            # Pie chart data
            self.series_pie.append(name, float(number))  # Use name as label, number as value
        
        # Configure axes
        self.axis_x.append([name for _, name in update_data])
        if update_data:
            self.axis_y.setRange(0, max(float(number) for number, _ in update_data))

        # Add series and axes to bar chart
        self.chart.addSeries(series)
        self.chart.setAxisX(self.axis_x, series)
        self.chart.setAxisY(self.axis_y, series)

        # Add percentage labels to pie slices
        total = sum(slice.value() for slice in self.series_pie.slices())
        for slice in self.series_pie.slices():
            percentage = (slice.value() / total) * 100
            slice.setLabel(f"{slice.label()[:6]}:{percentage:.1f}%")
            slice.setLabelVisible()

        self.pie_chart.addSeries(self.series_pie)
        self.pie_chart.setTitle("Pie Chart View")

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Image Category Dialog closing')
        constants.UIConfig.img_analyze_visible = False
        super().closeEvent(event)
