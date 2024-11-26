import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries
from PyQt5.QtGui import QPainter
from loguru import logger
from run import constants
from utils.log_analyis import log_analyze_data_output_new


class LogAnalyzeHistogram(QDialog):
    """Dialog for displaying log analysis histograms and pie charts"""

    def __init__(self, maximize: bool = True):
        super().__init__()
        # Initialize instance variables
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
        self.series = None

        # Configuration
        self.group_size = 5
        self.current_group = 0
        self.log_data = None
        self.log_item = None

        self.setModal(True)
        self.init_ui("Log Analysis")
        
        if maximize:
            self.showMaximized()
        else:
            self.show()
            
        logger.debug("ui finish")

    @logger.catch
    def init_ui(self, window_title):
        """Initialize the UI components"""
        self.resize(800, 600)
        self.window_title = window_title

        # Get initial data
        self.error_counts, self.log_item = self.parse_log_data()

        # Validate data before proceeding
        if not self.error_counts or not self.log_item:
            logger.warning("No log data available for analysis")
            self.error_counts = [0]  # Default value
            self.log_item = ["No Data"]  # Default value

        # Set up main window
        self.setWindowTitle(self.window_title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create chart layouts
        self.h_layout = QHBoxLayout()

        # Create and setup bar chart
        self.chart = self.create_chart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Create pie chart
        self.pie_chart_view = self.create_pie_chart()

        # Create navigation button
        self.next_button = QPushButton('Next Group')
        self.next_button.clicked.connect(self.showNextGroup)

        # Add widgets to layouts
        self.h_layout.addWidget(self.chart_view, stretch=1)
        self.h_layout.addWidget(self.pie_chart_view, stretch=1)
        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.next_button)

        # Set window flags to prevent immediate closing
        self.setWindowFlags(
            Qt.Window |  # Gives the window normal window system frame
            Qt.WindowMinMaxButtonsHint |  # Add minimize/maximize buttons
            Qt.WindowCloseButtonHint  # Add close button
        )
        
        logger.debug("init ui ...")

        # Initialize charts with data
        self.updateChart()

    @logger.catch
    def parse_log_data(self):
        """Parse log data for analysis"""
        labels, values = log_analyze_data_output_new()
        return values, labels  # Return values first, then labels

    @logger.catch
    def create_chart(self):
        """Create and return a bar chart"""
        chart = QChart()
        chart.setTitle("Error Distribution")
        chart.legend().hide()
        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.series = QBarSeries()
        self.series.setLabelsVisible()

        self.axis_x = QBarCategoryAxis()
        self.axis_y = QValueAxis()

        return chart

    @logger.catch
    def create_pie_chart(self):
        """Create and return a pie chart view"""
        self.series_pie = QPieSeries()
        self.pie_chart = QChart()
        chart_view = QChartView(self.pie_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        return chart_view

    @logger.catch
    def showNextGroup(self):
        """Show next group of data"""
        try:
            self.current_group = (self.current_group + 1) % ((len(self.error_counts) - 1) // self.group_size + 1)
            self.updateChart()
        except Exception as e:
            logger.warning(f"Error showing next group: {e}")

    @logger.catch
    def updateChart(self):
        """Update both bar and pie charts with current data"""
        if not self.error_counts or not self.log_item:
            logger.error("error, data Null")
            return

        # Clear existing series
        for series in self.chart.series():
            self.chart.removeSeries(series)
        for series in self.pie_chart.series():
            self.pie_chart.removeSeries(series)
        self.series.clear()
        self.series_pie.clear()

        # Get current group data
        start_idx = self.current_group * self.group_size
        end_idx = min(start_idx + self.group_size, len(self.error_counts))

        # self.error_counts contains the numeric values
        # self.log_item contains the labels
        current_values = self.error_counts[start_idx:end_idx]  # Numeric values
        current_labels = self.log_item[start_idx:end_idx]  # String labels

        # Update bar chart
        for label, value in zip(current_labels, current_values):
            bar_set = QBarSet(str(label))
            bar_set.append(float(value))  # Now value should be numeric
            self.series.append(bar_set)

        self.axis_x.clear()
        self.axis_x.append(current_labels)

        if current_values:
            self.axis_y.setRange(min(current_values), max(current_values))

        # Configure bar chart axes and series
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.chart.setAxisY(self.axis_y, self.series)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.setAxisX(self.axis_x, self.series)
        self.series.setBarWidth(0.8)
        self.chart.addSeries(self.series)

        # Update pie chart
        total = sum(current_values)
        for item, value in zip(current_labels, current_values):
            slice = self.series_pie.append(item, value)
            percentage = (value / total) * 100
            slice.setLabel(f"{item[:6]}:{percentage:.1f}%")
            slice.setLabelVisible(True)

        self.pie_chart.addSeries(self.series_pie)
        self.pie_chart.setTitle("Error Distribution (Pie)")

        logger.debug("ui paint finish.")

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Log Analysis Dialog closing')
        constants.UIConfig.log_analyze_visible = False
        super().closeEvent(event)
