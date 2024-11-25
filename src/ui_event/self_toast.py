import sys
from pathlib import Path
from threading import Thread

sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog
from loguru import logger

from run import constants


class Toast(QDialog):
    """Toast notification dialog that auto-closes after a delay"""
    
    def __init__(self, message, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.timer = None
        self.setup_ui(message)

    @logger.catch
    def setup_ui(self, message):
        """Set up the toast UI components"""
        # Configure window properties
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create layout and message label
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        
        # Set size
        self.resize(260, 200)
        
        # Set up auto-close timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.setSingleShot(True)
        self.timer.start(constants.detail_delta_time)


@logger.catch
def show_toast(message):
    """Display a toast notification with the given message"""
    toast = Toast(message)
    toast.show()
    toast.exec_()


@logger.catch
def show_toast_async(message):
    """Display a toast notification asynchronously in a separate thread"""
    Thread(target=show_toast, args=(message,), daemon=True).start()
