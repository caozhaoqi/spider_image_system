from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from loguru import logger


class VideoPlayerThread(QThread):
    update_progress = pyqtSignal(int)  # 用于更新进度条的信号
    update_status = pyqtSignal(str)  # 用于更新播放状态的信号（暂停/播放）
    update_speed = pyqtSignal(float)  # 用于更新播放速度的信号（倍速）
    update_frame = pyqtSignal(int)  # 用于更新当前帧数的信号（可选）
    update_seek = pyqtSignal(int)  # 用于更新快进/快退位置的信号（可选）
    update_speed_labels = pyqtSignal()  # 用于更新倍速按钮的标签（可选）
    stop_signal = pyqtSignal()  # 停止播放的信号（可选）

    def __init__(self, video_file, parent=None):
        super().__init__(parent)
        self.paused = None
        self.video_file = video_file
        self.position = 0
        self.speed = 1.0

    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            logger.error("无法打开视频文件")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        while True:
            # logger.debug(cv2.waitKey(1))
            ret, frame = cap.read()
            if not ret:  # 如果无法获取帧，则退出循环
                break
            self.position += 1
            self.update_progress.emit(int(self.position / fps * 100))  # 更新进度条位置
            self.update_frame.emit(self.position)  # 更新当前帧数（可选）
            if self.position % fps == 0:  # 更新播放状态和倍速信息（可选）
                self.update_status.emit('Playing')
                self.update_speed.emit(self.speed)
            else:
                self.update_status.emit('Paused')
            cv2.imshow("Video show frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按'q'键退出循环和程序
                break
            if cv2.waitKey(1) & 0xFF == ord('p'):  # 按'p'键暂停/继续播放视频
                if self.position % fps == 0:  # 如果是整帧数，则暂停/继续播放视频
                    if self.speed == 1.0:  # 如果是正常速度，则暂停视频
                        self.update_status.emit('Paused')
                        cap.release()
                        cv2.destroyAllWindows()
                        break
                else:  # 否则快进到下一帧并继续播放视频
                    self.position += 1
                    continue
            if cv2.waitKey(1) & 0xFF == ord('b'):  # 按'b'键后退一帧（可选）
                self.position -= 1
                continue
            if cv2.waitKey(1) & 0xFF == ord('f'):  # 按'f'键快进一帧（可选）
                self.position += 1
                continue
            if cv2.waitKey(1) & 0xFF == ord('u'):  # 按'u'键增加播放速度（1.5倍速）（可选）
                # self.speed = 1.5 * self.speed if self.speed < 6 else self.speed  # 上限为6倍速（可选）
                self.speed = 1.5 * self.speed if self.speed < 6 else self.speed  # 上限为6倍速（可选）
                self.update_speed_labels.emit()
            if cv2.waitKey(1) & 0xFF == ord('s'):  # 按's'键将播放速度设为正常速度（1倍速）（可选）
                self.speed = 1.0
                self.update_speed_labels.emit()

            if cv2.waitKey(1) & 0xFF == ord('f'):  # 按'f'键全屏显示视频（可选）
                cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Video', 800, 600)

            if cv2.waitKey(1) & 0xFF == ord('b'):  # 按'b'键回到视频开头（可选）
                self.position = 0
                self.update_progress.emit(0)
                self.update_status.emit('Playing')
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
            if cv2.waitKey(1) & 0xFF == ord('d'):  # 按'd'键暂停/继续播放视频（可选）
                if self.paused:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.position)
                    self.paused = False
                    self.update_status.emit('Playing')
                else:
                    self.paused = True
                    self.update_status.emit('Paused')

