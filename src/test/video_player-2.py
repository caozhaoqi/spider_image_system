from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer
import sys


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Player')

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.player = QMediaPlayer()
        self.videoWidget = QVideoWidget()
        layout.addWidget(self.videoWidget)

        self.player.setVideoOutput(self.videoWidget)

        openButton = QPushButton('Open Video')
        openButton.clicked.connect(self.openVideo)
        layout.addWidget(openButton)

    def openVideo(self):
        fileName = r'C:\Users\Administrator\Desktop\WeChat_20240124173613.mp4'  # 替换为您的视频文件路径
        self.player.setMedia(QUrl.fromLocalFile(fileName))
        self.player.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
