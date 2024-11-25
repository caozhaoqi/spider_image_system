import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, 
    QHBoxLayout, QWidget, QTextEdit
)
from loguru import logger
from run import constants


class KeywordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.keyword_label = None
        self.keyword_edt = None
        self.init_ui()

    @logger.catch
    def init_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle('Add Keywords (Comma Separated)')
        self.setFixedSize(600, 400)

        # Create widgets
        self.keyword_label = QLabel('Keywords:')
        self.keyword_edt = QTextEdit()
        save_button = QPushButton('Save')
        cancel_button = QPushButton('Cancel')

        # Create layouts
        layout = QVBoxLayout()
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        button_layout = QHBoxLayout()

        # Add widgets to layouts
        input_layout.addWidget(self.keyword_label)
        input_layout.addWidget(self.keyword_edt)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(input_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect signals
        save_button.clicked.connect(lambda: self.save_data())
        cancel_button.clicked.connect(self.reject)

    @logger.catch
    def closeEvent(self, event):
        """Handle dialog close event"""
        logger.debug('Keyword Dialog is closing!')
        super().closeEvent(event)

    @logger.catch
    def save_data(self):
        """Save keywords to file"""
        keyword_txt = self.keyword_edt.toPlainText()
        keywords = [k.strip() for k in keyword_txt.split(',') if k.strip()]
        
        if not keywords:
            logger.warning(f"No valid keywords entered: {keyword_txt}")
            return False

        # Create output directory if needed
        spider_dir = Path(constants.data_path) / "auto_spider_img"
        spider_dir.mkdir(exist_ok=True)
        
        keyword_file = spider_dir / "spider_img_keyword.txt"

        # Create file if it doesn't exist
        if not keyword_file.exists():
            keyword_file.write_text("", encoding='utf-8')
            logger.warning(f"Created new keyword file: {keyword_file}")

        # Read existing keywords
        existing_keywords = []
        if keyword_file.stat().st_size > 0:
            existing_keywords = keyword_file.read_text(encoding='utf-8').splitlines()

        # Add new keywords
        all_keywords = existing_keywords + keywords

        # Write back to file
        keyword_file.write_text(
            "\n".join(k.strip() for k in all_keywords), 
            encoding='utf-8'
        )

        logger.success(f"Successfully added keywords: {keyword_txt}")
        self.close()
