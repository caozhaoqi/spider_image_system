import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QDialog
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter
from loguru import logger

from run import constants
from utils.data_json import data_json
from utils.log_analyis import log_analyze_data_output, log_analyze_data_output_new


class LogAnalyzeHistogram(QDialog):

    def __init__(self, window_title="Log Analyze Histogram"):
        """

        :param window_title:
        """
        super().__init__()

        self.chart_view = None
        self.layout = None
        self.central_widget = None
        # self.app = None
        # self.main_window = None
        self.error_counts = None
        self.window_title = None
        self.next_button = None
        self.chart = None
        self.max_value = None
        self.min_value = None
        self.axis_x = None
        self.axis_y = None
        self.group_size = 10
        self.series = None
        self.current_group = 0
        self.log_data = None
        self.log_item = None
        self.init_ui(window_title)
        self.updateChart()

    def init_ui(self, window_title):
        """

        :return: 
        """
        self.window_title = window_title
        self.error_counts, self.log_item = self.parse_log_data()

        self.setWindowTitle(self.window_title)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.chart = self.create_chart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        # 创建按钮
        self.next_button = QPushButton('Next Group')
        self.next_button.clicked.connect(self.showNextGroup)

        self.setFixedSize(1920, 1080)
        self.showMaximized()
        self.layout.addWidget(self.chart_view)
        self.layout.addWidget(self.next_button)

    def parse_log_data(self):
        """

        :return:
        """

        # error_counts = {}
        data_json(log_analyze_data_output())
        logger.success("log analyze result saved json.")
        error_name_list, error_count_list = log_analyze_data_output_new()
        # logger.info(f"{len(error_name_list)}, {len(error_count_list)}")
        return error_count_list, error_name_list

    def create_chart(self):
        """
        创建并返回一个带有数据标签的柱状图
        :return: QChart 对象
        """
        self.chart = QChart()
        self.chart.setTitle(self.window_title)
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # init ui
        self.series = QBarSeries()
        self.series.setLabelsVisible()  # 启用数据标签

        # 创建类别轴并将其设置为图表的 X 轴
        self.axis_x = QBarCategoryAxis()
        self.axis_y = QValueAxis()

        return self.chart

    def showNextGroup(self):
        # 更新当前数据组索引
        try:
            self.current_group = (self.current_group + 1) % (len(self.error_counts) // self.group_size)
        except Exception as e:
            logger.warning(f"unknown error! detail: {e}")

        # 更新图表
        self.updateChart()

    def updateChart(self):
        """

        :return:
        """
        # 清除旧数据
        for series in self.chart.series():
            self.chart.removeSeries(series)

        self.series.clear()  # 清除序列中的数据

        update_list_count = []
        update_list_item = []
        # 添加新数据组到图表
        start_index = self.current_group * self.group_size  # 5
        end_index = start_index + self.group_size  # 10
        for i in range(start_index, end_index):
            if i < len(self.error_counts):
                set_ = QBarSet(self.log_item[i])
                set_.append(self.error_counts[i])
                update_list_count.append(self.error_counts[i])
                update_list_item.append(self.log_item[i])
                self.series.append(set_)

            # 创建柱状图系列

        self.axis_x.append(update_list_item)
        # 更新图表视图
        if update_list_count:
            self.min_value = min(update_list_count) if update_list_count else 0  # 获取最小值
            self.max_value = max(update_list_count)  # 获取最大值
            self.axis_y.setRange(self.min_value, self.max_value)  # 设置 Y 轴范围
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)  # 将 Y 轴添加到图表左侧
        self.chart.setAxisY(self.axis_y, self.series)  # 将 Y 轴与系列关联
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)  # 将轴添加到图表的底部
        self.chart.setAxisX(self.axis_x, self.series)  # 将 X 轴与数据系列关联
        bar_width = 0.8  # 例如，设置为0.5
        self.series.setBarWidth(bar_width)
        self.chart.addSeries(self.series)

    def closeEvent(self, event):
        """
        对话框关闭
        :param event:
        :return:
        """
        # 在这里你可以添加任何你需要在对话框关闭时执行的代码
        logger.debug('LogAnalyzeHistogram Dialog is closing!')
        constants.log_analyze_visible = False
        # 调用基类的 closeEvent 方法以确保对话框正常关闭
        super(LogAnalyzeHistogram, self).closeEvent(event)


# 使用示例
if __name__ == "__main__":
    # log_data = [
    #     # ... (你的日志数据)
    # ]
    histogram = LogAnalyzeHistogram()
    histogram.show()
    # histogram.parse_log_data()
