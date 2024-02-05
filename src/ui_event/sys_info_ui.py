# import sys
#
# from PyQt5 import QtWidgets, QtGui, QtCore
# from loguru import logger
# from utils.sys_info import look_sys_info, network_usage
# from PyQt5.QtCore import QTimer
#
#
# # 定时获取系统信息的函数
# @logger.catch
# def get_system_info():
#     """
#
#     :return:
#     """
#     memory_usage, cpu_usage = look_sys_info()
#     send_bytes, receiver_bytes = network_usage()  # 示例数据
#     return memory_usage, cpu_usage, send_bytes, receiver_bytes
#
#
# class SystemInfoApp(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.chart1_widget_layout = None
#         self.initUI()
#         self.update_data()  # 初始化数据
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_data)  # 定时器用于更新数据
#         self.timer.start(1000)  # 1秒更新一次数据
#
#     def initUI(self):
#         self.setWindowTitle("System Information")
#         self.setGeometry(300, 300, 800, 600)
#         self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 保持窗口在最前面
#
#         # 创建四个子图
#         self.chart1 = QtCharts.QChart()
#         self.chart1.setTitle("Memory Usage")
#         self.chart1_axis = self.chart1.createDefaultAxes()  # 创建默认的坐标轴
#         self.chart1_axis['left']['min'] = 0  # 设置y轴最小值
#         self.chart1_axis['left']['max'] = 100  # 设置y轴最大值
#         self.chart1_series = QtCharts.QLineSeries()  # 创建线型图系列
#         self.chart1.addSeries(self.chart1_series)  # 将系列添加到图表中
#         self.chart1_legend = self.chart1.legend()  # 获取图例对象
#         self.chart1_legend.setVisible(True)  # 设置图例可见性
#         self.chart1_legend.setAlignment(QtCore.Qt.AlignBottom)  # 设置图例对齐方式
#         self.chart1_widget = QtCharts.QChartView(self.chart1)  # 创建图表视图并设置其属性
#         self.chart1_widget.setRenderHint(QtGui.QPainter.Antialiasing)  # 设置抗锯齿渲染提示
#         self.chart1_widget.setRubberBand(QtCharts.QChartView.RectangleRubberBand)  # 设置缩放区域为矩形区域
#         self.chart1_widget.setDragEnabled(True)  # 设置拖拽功能为启用状态
#         self.chart1_widget.setZoomEnabled(True)  # 设置缩放功能为启用状态
#         self.chart1_widget.setWheelEnabled(True)  # 设置鼠标滚轮缩放功能为启用状态
#         self.chart1_widget_layout = QtWidgets.QVBoxLayout()  # 创建垂直布局对象并设置其属性
#         self.chart1_widget_layout.addWidget(self.chart1_widget)  # 将图表视图添加到垂直布局中
#         self.chart1_widget_container = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         self.chart1_widget_container.setLayout(self.chart1_widget_layout)  # 将布局添加到容器中
#         container_layout = QtWidgets.QHBoxLayout()  # 创建水平布局对象并设置其属性
#         container_layout.addWidget(QtWidgets.QLabel("Memory Usage"))  # 将标签添加到水平布局中
#         container_layout.addWidget(self.chart1_widget_container)  # 将容器添加到水平布局中
#         container = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container.setLayout(container_layout)  # 将布局添加到容器中
#         self.setCentralWidget(container)  # 将容器设置为窗口的中心部件对象
#
#         # 类似地，创建其他三个子图... (略)
#         # 创建子图2
#         self.chart2 = QtCharts.QChart()
#         self.chart2.setTitle("CPU Usage")
#         self.chart2_axis = self.chart2.createDefaultAxes()  # 创建默认的坐标轴
#         self.chart2_axis['left']['min'] = 0  # 设置y轴最小值
#         self.chart2_axis['left']['max'] = 100  # 设置y轴最大值
#         self.chart2_series = QtCharts.QLineSeries()  # 创建线型图系列
#         self.chart2.addSeries(self.chart2_series)  # 将系列添加到图表中
#         self.chart2_legend = self.chart2.legend()  # 获取图例对象
#         self.chart2_legend.setVisible(True)  # 设置图例可见性
#         self.chart2_legend.setAlignment(QtCore.Qt.AlignBottom)  # 设置图例对齐方式
#         self.chart2_widget = QtCharts.QChartView(self.chart2)  # 创建图表视图并设置其属性
#         self.chart2_widget.setRenderHint(QtGui.QPainter.Antialiasing)  # 设置抗锯齿渲染提示
#         self.chart2_widget.setRubberBand(QtCharts.QChartView.RectangleRubberBand)  # 设置缩放区域为矩形区域
#         self.chart2_widget.setDragEnabled(True)  # 设置拖拽功能为启用状态
#         self.chart2_widget.setZoomEnabled(True)  # 设置缩放功能为启用状态
#         self.chart2_widget.setWheelEnabled(True)  # 设置鼠标滚轮缩放功能为启用状态
#         container_layout2 = QtWidgets.QHBoxLayout()  # 创建水平布局对象并设置其属性
#         container_layout2.addWidget(QtWidgets.QLabel("CPU Usage"))  # 将标签添加到水平布局中
#         container_layout2.addWidget(self.chart2_widget)  # 将图表视图添加到水平布局中
#         container2 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container2.setLayout(container_layout2)  # 将布局添加到容器中
#         container_layout3 = QtWidgets.QVBoxLayout()  # 创建垂直布局对象并设置其属性
#         container_layout3.addWidget(container)  # 将容器添加到垂直布局中
#         container_layout3.addWidget(container2)  # 将容器添加到垂直布局中
#         container3 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container3.setLayout(container_layout3)  # 将布局添加到容器中
#         self.setCentralWidget(container3)  # 将容器设置为窗口的中心部件对象
#
#         # 创建子图3
#         self.chart3 = QtCharts.QChart()
#         self.chart3.setTitle("Network Usage")
#         self.chart3_axis = self.chart3.createDefaultAxes()  # 创建默认的坐标轴
#         self.chart3_axis['left']['min'] = 0  # 设置y轴最小值
#         self.chart3_axis['left']['max'] = 100  # 设置y轴最大值
#         self.chart3_series = QtCharts.QLineSeries()  # 创建线型图系列
#         self.chart3.addSeries(self.chart3_series)  # 将系列添加到图表中
#         self.chart3_legend = self.chart3.legend()  # 获取图例对象
#         self.chart3_legend.setVisible(True)  # 设置图例可见性
#         self.chart3_legend.setAlignment(QtCore.Qt.AlignBottom)  # 设置图例对齐方式
#         self.chart3_widget = QtCharts.QChartView(self.chart3)  # 创建图表视图并设置其属性
#         self.chart3_widget.setRenderHint(QtGui.QPainter.Antialiasing)  # 设置抗锯齿渲染提示
#         self.chart3_widget.setRubberBand(QtCharts.QChartView.RectangleRubberBand)  # 设置缩放区域为矩形区域
#         self.chart3_widget.setDragEnabled(True)  # 设置拖拽功能为启用状态
#         self.chart3_widget.setZoomEnabled(True)  # 设置缩放功能为启用状态
#         self.chart3_widget.setWheelEnabled(True)  # 设置鼠标滚轮缩放功能为启用状态
#         container_layout4 = QtWidgets.QHBoxLayout()  # 创建水平布局对象并设置其属性
#         container_layout4.addWidget(QtWidgets.QLabel("Network Usage"))  # 将标签添加到水平布局中
#         container_layout4.addWidget(self.chart3_widget)  # 将图表视图添加到水平布局中
#         container4 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container4.setLayout(container_layout4)  # 将布局添加到容器中
#         container_layout5 = QtWidgets.QVBoxLayout()  # 创建垂直布局对象并设置其属性
#         container_layout5.addWidget(container3)  # 将容器添加到垂直布局中
#         container_layout5.addWidget(container4)  # 将容器添加到垂直布局中
#         container5 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container5.setLayout(container_layout5)  # 将布局添加到容器中
#         self.setCentralWidget(container5)  # 将容器设置为窗口的中心部件对象
#
#         # 创建子图4
#         self.chart4 = QtCharts.QChart()
#         self.chart4.setTitle("Disk Usage")
#         self.chart4_axis = self.chart4.createDefaultAxes()  # 创建默认的坐标轴
#         self.chart4_axis['left']['min'] = 0  # 设置y轴最小值
#         self.chart4_axis['left']['max'] = 100  # 设置y轴最大值
#         self.chart4_series = QtCharts.QLineSeries()  # 创建线型图系列
#         self.chart4.addSeries(self.chart4_series)  # 将系列添加到图表中
#         self.chart4_legend = self.chart4.legend()  # 获取图例对象
#         self.chart4_legend.setVisible(True)  # 设置图例可见性
#         self.chart4_legend.setAlignment(QtCore.Qt.AlignBottom)  # 设置图例对齐方式
#         self.chart4_widget = QtCharts.QChartView(self.chart4)  # 创建图表视图并设置其属性
#         self.chart4_widget.setRenderHint(QtGui.QPainter.Antialiasing)  # 设置抗锯齿渲染提示
#         self.chart4_widget.setRubberBand(QtCharts.QChartView.RectangleRubberBand)  # 设置缩放区域为矩形区域
#         self.chart4_widget.setDragEnabled(True)  # 设置拖拽功能为启用状态
#         self.chart4_widget.setZoomEnabled(True)  # 设置缩放功能为启用状态
#         self.chart4_widget.setWheelEnabled(True)  # 设置鼠标滚轮缩放功能为启用状态
#         container_layout6 = QtWidgets.QHBoxLayout()  # 创建水平布局对象并设置其属性
#         container_layout6.addWidget(QtWidgets.QLabel("Disk Usage"))  # 将标签添加到水平布局中
#         container_layout6.addWidget(self.chart4_widget)  # 将图表视图添加到水平布局中
#         container6 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container6.setLayout(container_layout6)  # 将布局添加到容器中
#         container_layout7 = QtWidgets.QVBoxLayout()  # 创建垂直布局对象并设置其属性
#         container_layout7.addWidget(container5)  # 将容器添加到垂直布局中
#         container_layout7.addWidget(container6)  # 将容器添加到垂直布局中
#         container7 = QtWidgets.QWidget()  # 创建容器对象并设置其属性
#         container7.setLayout(container_layout7)  # 将布局添加到容器中
#         self.setCentralWidget(container7)  # 将容器设置为窗口的中心部件对象
#
#     def update_data(self):
#         memory_usage, cpu_usage, send_bytes, receiver_bytes = get_system_info()
#         self.chart1_series.append(memory_usage)
#         self.chart2_series.append(cpu_usage)
#         self.chart3_series.append(send_bytes)
#         self.chart4_series.append(receiver_bytes)
#
#         if len(self.chart1_series) > 50:  # 保持图表不超过50个数据点
#             self.chart1_series.pop(0)
#         if len(self.chart2_series) > 50:  # 保持图表不超过50个数据点
#             self.chart2_series.pop(0)
#
#         if len(self.chart3_series) > 50:  # 保持图表不超过50个数据点
#             self.chart3_series.pop(0)
#         if len(self.chart4_series) > 50:  # 保持图表不超过50个数据点
#             self.chart4_series.pop(0)
#
#
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     ex = SystemInfoApp()
#     ex.show()
#     sys.exit(app.exec_())
