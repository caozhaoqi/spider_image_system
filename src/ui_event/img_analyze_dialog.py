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

        self.init_ui("Image Category Analysis")
        self.updateChart()

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
        for item, count in update_data:
            bar_set = QBarSet(item)
            bar_set.append(count)
            self.series.append(bar_set)

        # Configure axes
        self.axis_x.clear()
        self.axis_x.append([item for item, _ in update_data])
        
        if update_data:
            counts = [count for _, count in update_data]
            self.axis_y.setRange(min(counts), max(counts))

        # Add series and axes to bar chart
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.chart.setAxisY(self.axis_y, self.series)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.setAxisX(self.axis_x, self.series)
        self.series.setBarWidth(0.8)
        self.chart.addSeries(self.series)

        # Update pie chart
        for item, count in update_data:
            self.series_pie.append(item, count)

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
        constants.img_analyze_visible = False
        super().closeEvent(event)
