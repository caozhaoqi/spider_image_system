import sys

from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QListWidget

from utils.video_process import search_videos, load_and_play_video


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        """
        self.videoWidget = QVideoWidget()
        self.player.setVideoOutput(self.videoWidget)
        self.setCentralWidget(self.videoWidget)
        """
        self.player = QMediaPlayer()
        self.videoWidget = QVideoWidget()
        self.player.setVideoOutput(self.videoWidget)
        self.setCentralWidget(self.videoWidget)
        self.player.stateChanged.connect(self.playerStateChanged)
        self.player.positionChanged.connect(self.updatePosition)
        # 添加其他控件和布局管理...
        self.search_box = QLineEdit("please input need video：")  # 搜索框
        # 添加其他控件...
        layout = QVBoxLayout()  # 布局管理
        layout.addWidget(self.search_box)  # 搜索框布局
        # 添加视频列表框控件
        self.video_list = QListWidget()

        # 布局管理
        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.video_list)  # 将视频列表框添加到布局中

        # 添加其他控件到布局...
        self.setLayout(layout)  # 设置主窗口的布局
        self.show()  # 显示窗口

    def initUI(self):
        self.setWindowTitle('Video Player')  # 设置窗口标题
        # 设置窗口大小和其他属性...

    def playerStateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            print("Playing")
        else:
            print("Paused")

    def updatePosition(self, position):
        elapsed_time = self.player.position() // 1000  # elapsed time in seconds
        total_duration = self.player.media().duration() // 1000  # total duration in seconds
        remaining_time = total_duration - elapsed_time  # remaining time in seconds
        elapsed_time = "{:.2f}".format(elapsed_time)  # elapsed time in mm:ss format
        remaining_time = "{:.2f}".format(remaining_time)  # remaining time in mm:ss format
        self.elapsed_time_label.setText(elapsed_time)  # update elapsed time label text
        self.remaining_time_label.setText(remaining_time)  # update remaining time label text

    # 添加其他方法如控制视频播放、搜索视频等...
    def searchVideos(self, query):  # 一个简单的示例方法，根据实际需求实现搜索功能
        """
        to do search video from internet
        :param query: 关键字
        :return:
        """
        search_videos(query)
        pass  # 在这里实现搜索逻辑，更新视频列表等...

    def playVideo(self, video):  # 根据实际需求实现播放逻辑，可能还需要解析视频链接等...
        """
        load video from local mp4 file
        :param video: 视频
        :return:
        """
        video = "./data/video/1703471146086.mp4"
        load_and_play_video(video)
        pass  # 在这里实现播放视频的逻辑...

    # ... 其他方法和逻辑 ...
    # 创建其他控件和
    def playPause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def seek(self, position):
        self.player.setPosition(position)

    def stop(self):
        self.player.stop()
