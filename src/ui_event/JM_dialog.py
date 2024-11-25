import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt
from loguru import logger
from threading import Thread

from run import constants
import jmcomic


class JMDialog(QDialog):
    """Dialog for downloading JM comics by ID"""
    
    def __init__(self):
        super().__init__()
        self.download_button = None
        self.jm_id_label = None 
        self.jm_id_input = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle('JM ID Downloader')
        self.setGeometry(300, 300, 450, 150)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create input widgets
        self.jm_id_label = QLabel('JM ID:')
        self.jm_id_input = QLineEdit()
        self.download_button = QPushButton('Download')
        
        # Add widgets to layout
        layout.addWidget(self.jm_id_label)
        layout.addWidget(self.jm_id_input)
        layout.addWidget(self.download_button)
        
        # Connect signals
        self.download_button.clicked.connect(self.on_download_clicked)
        
        self.show()

    @logger.catch
    def on_download_clicked(self):
        """Handle download button click"""
        jm_id = self.jm_id_input.text().strip()
        if jm_id:
            Thread(target=download_jm_thread, args=(jm_id,)).start()
        else:
            logger.warning("JM ID input is empty")

    def reject(self):
        """Handle dialog rejection"""
        logger.debug('JM dialog is cancel closing!')
        constants.jm_dialog_visible = False
        super().reject()

    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('JM dialog is close closing!')
        constants.jm_dialog_visible = False
        super().closeEvent(event)


@logger.catch
def download_jm_thread(jm_id: str) -> None:
    """Download JM comic in a separate thread
    
    Args:
        jm_id: The ID of the JM comic to download
    """
    logger.debug(f"Start downloading JM ID: {jm_id}")
    jmcomic.download_album(jm_id)
    constants.jm_dialog_visible = False
    logger.success(f"Download JM {jm_id} finished")
