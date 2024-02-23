from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries
from PyQt5.QtGui import QPainter
from loguru import logger

from run import constants
from utils.data_json import data_json
from utils.log_analyis import log_analyze_data_output, log_analyze_data_output_new


class LogAnalyzeHistogram(QDialog):

    def __init__(self):
        """
        """
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
        self.group_size = 10
        self.series = None
        self.current_group = 0
        self.log_data = None
        self.log_item = None
        self.init_ui("Log Analyze Histogram")
        self.updateChart()

    def init_ui(self, window_title):
        """

        :return: 
        """
        self.resize(800, 600)
        self.window_title = window_title
        self.error_counts, self.log_item = self.parse_log_data()

        self.setWindowTitle(self.window_title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.h_layout = QHBoxLayout()
        self.chart = self.create_chart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view = self.create_pie_chart()

        # 创建按钮
        self.next_button = QPushButton('Next Group')
        self.next_button.clicked.connect(self.showNextGroup)

        # 添加第一个图表视图，并设置其伸缩因子为1
        self.h_layout.addWidget(self.chart_view, stretch=1)
        self.h_layout.addWidget(self.pie_chart_view, stretch=1)

        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.next_button)

    def parse_log_data(self):
        """

        :return:
        """

        error_name_list, error_count_list = log_analyze_data_output_new()
        return error_count_list, error_name_list

    def create_chart(self):
        """
        创建并返回一个带有数据标签的柱状图
        :return: QChart 对象
        """
        self.chart = QChart()
        self.chart.setTitle("chart view")
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        # init ui
        self.series = QBarSeries()
        self.series.setLabelsVisible()  # 启用数据标签

        # 创建类别轴并将其设置为图表的 X 轴
        self.axis_x = QBarCategoryAxis()
        self.axis_y = QValueAxis()

        return self.chart

    def create_pie_chart(self):
        # 创建饼图数据
        self.series_pie = QPieSeries()
        # 创建图表
        self.pie_chart = QChart()
        # 创建图表视图
        chart_view = QChartView(self.pie_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        return chart_view

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

        for series in self.pie_chart.series():
            self.pie_chart.removeSeries(series)

        self.series.clear()  # 清除序列中的数据
        self.series_pie.clear()

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

        for index, data_content in enumerate(update_list_item):
            self.series_pie.append(data_content, update_list_count[index])

        total = sum(slice.value() for slice in self.series_pie.slices())
        for index, pie_slice in enumerate(self.series_pie.slices()):
            # 计算百分比并格式化为字符串
            percentage = (pie_slice.value() / total) * 100
            pie_slice.setLabel(f"{update_list_item[index][0:6]}:{percentage:.1f}%")
            pie_slice.setLabelVisible()  # 设置标签为可见
        # 创建图表
        # self.pie_chart = QChart()
        self.pie_chart.addSeries(self.series_pie)
        self.pie_chart.setTitle("pie chart")

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

# # 使用示例
# if __name__ == "__main__":
#     histogram = LogAnalyzeHistogram()
#     histogram.show()
